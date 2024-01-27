import collections
import heapq
import multiprocessing
import queue
import uuid
from multiprocessing import Process
from pathlib import Path

import numpy as np
from line_profiler_pycharm import profile

from boostface.types import Image, Bbox, Kps, Embedding, MatchInfo
from app.services.inference.common import Face, Target, IdentifyManager, Image2Detect, FaceNew, Face2Search, ClosableQueue
from .sort_plus import associate_detections_to_trackers
from ..db.operations import Matcher
from ..model_zoo import get_model, ArcFaceONNX
from ..utils.decorator import thread_error_catcher

matched_and_in_screen_deque = collections.deque(maxlen=1)


class Extractor:
    """
    extract face embedding from given target bbox and kps, and det_score by running model in onnx
    """

    def __init__(self):
        root: Path = Path(__file__).parents[1].joinpath(
            'model_zoo\\models\\insightface\\irn50_glint360k_r50.onnx')
        self.rec_model: ArcFaceONNX = get_model(root, providers=(
            'CUDAExecutionProvider', 'CPUExecutionProvider'))
        self.rec_model.prepare(ctx_id=0)

    def run_onnx(self,
                 img2extract: Image,
                 bbox: Bbox,
                 kps: Kps,
                 det_score: float) -> Embedding:
        """
        get embedding of face from given target bbox and kps, and det_score
        :param img2extract: target at which image
        :param bbox: target bbox
        :param kps: target kps
        :param det_score: target det_score
        :return: face embedding
        """
        face = Face(bbox=bbox,
                    kps=kps,
                    det_score=det_score)
        self.rec_model.get(img2extract, face)
        return face.normed_embedding


def identify_works(
        task_queue: multiprocessing.Queue,
        result_dict: dict,
        stop_event: multiprocessing.Event):
    """
    long term works in a single process
    1. get Face from worker_queue
    2. extract embedding
    3. search in milvus by embedding
    4. put result in result_queue
    :param stop_event:
    :param result_dict:
    :param task_queue:
    :return:
    """
    with Matcher() as mathcer:
        extractor = Extractor()
        while not stop_event.is_set():
            try:
                item = task_queue.get(timeout=1)
                task_id: uuid = item[0]
                task: Face2Search = item[1]
                # start = default_timer()
                emmbedding = extractor.run_onnx(
                    task.face_img, task.bbox, task.kps, task.det_score)
                # print(f'extractor cost time: {default_timer() - start}')
                # start = default_timer()
                result_dict[task_id] = mathcer.search(emmbedding)
            except queue.Empty:
                continue
            except Exception as e:
                print(
                    f"An error occurred while processing the{task_id} task: {e}")


class IdentifyWorker(Process):
    """
    solo worker for extractor and then search by milvus
    """

    def __init__(
            self,
            task_queue: multiprocessing.Queue,
            result_dict: dict,
    ):
        self._stop_event = multiprocessing.Event()
        super().__init__(
            target=identify_works,
            daemon=True,
            args=(
                task_queue,
                result_dict,
                self._stop_event))

    def start(self):
        super().start()
        print("IdentifyWorker start")

    def stop(self):
        self._stop_event.set()
        super().join()
        print("IdentifyWorker stop")


class Tracker:
    """
    tracker for a single target
    :param max_age: del as frames not matched
    :param min_hits: be treated normal
    :param iou_threshold: for Hungarian algorithm
    :param manager: IdentifyManager
    """

    def __init__(
            self,
            manager: IdentifyManager,
            max_age=10,
            min_hits=1,
            iou_threshold=0.3,
    ):
        self._targets: dict[int, Target] = {}
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self._recycled_ids = []
        self._identifier_manager: IdentifyManager = manager

    @profile
    @thread_error_catcher
    def identified_results(self, image2identify: Image2Detect) -> Image2Detect:
        """
        fill image2identify.faces with match info or return MatchInfo directly
        :param image2identify:
        :return: get image2identify match info
        """
        self._update(image2identify)
        self._search(image2identify)
        # [tar.face.match_info for tar in self._targets.values()]
        return Image2Detect(
            image2identify.nd_arr, [
                tar.face for tar in self._targets.values() if tar.in_screen])

    @thread_error_catcher
    def _update(self, image2update: Image2Detect):
        """
        according to the "memory" in Kalman tracker update former targets info by Hungarian algorithm
        :param image2update:
        :return:
        """
        detected_tars: list[FaceNew] = image2update.faces

        if self._targets:
            predicted_tars: list[FaceNew] = self._clean_dying()
            # match predicted and detected
            matched, unmatched_det_tars, unmatched_pred_tars = associate_detections_to_trackers(
                detected_tars, predicted_tars, self.iou_threshold)

            # update pred_tar with matched detected tar
            for pred_tar, detected_tar in matched:
                self._targets[pred_tar.id].update_pos(
                    detected_tar.bbox, detected_tar.kps, detected_tar.det_score)

                self._targets[pred_tar.id].update_tracker(detected_tar.bbox)

            # update  state of continuation of  unmatched_pred_tars
            for unmatched_tar in unmatched_pred_tars:
                self._targets[unmatched_tar.id].unmatched()

        else:
            unmatched_det_tars: list[FaceNew] = detected_tars

        # add new targets
        for detected_tar in unmatched_det_tars:
            new_id = self._generate_id()
            assert new_id not in self._targets, f'{new_id} is already in self._targets'
            detected_tar.id = new_id
            self._targets[new_id] = Target(face=detected_tar)

            # dev only
            self._targets[new_id].face.match_info = MatchInfo(uid=self._targets[new_id].name, score=0.0)

        self._clear_dead()

    @thread_error_catcher
    def _search(self, image2identify: Image2Detect):
        """
        search in a process and then update face.match_info
        :param image2identify:
        """
        for tar in self._targets.values():
            if tar.rec_satified:
                uuid = self._identifier_manager.add_task(
                    tar.face.face_image(image2identify.nd_arr))
                tar.face.update_match_info(
                    self._identifier_manager.get_result(uuid))

    @thread_error_catcher
    def _clean_dying(self) -> list[FaceNew]:
        """
        clean dying targets from tracker prediction
        :return tracker predictions
        """
        predicted_tars: list[FaceNew] = []
        to_del: list[int] = []
        for tar in self._targets.values():
            raw_tar: FaceNew = tar.get_predicted_tar
            # store key in self.self._targets.values()
            pos = raw_tar.bbox
            if np.any(np.isnan(pos)):
                to_del.append(raw_tar.id)
            # got new predict tars
            predicted_tars.append(raw_tar)

        #  del dying tars
        for k in to_del:
            assert k in self._targets, f'k = {k} not in self._targets'
            assert isinstance(k, int), "k in to_del,should be int"
            heapq.heappush(self._recycled_ids, k)
            del self._targets[k]
        return predicted_tars

    @thread_error_catcher
    def _clear_dead(self):
        """
        clear dead targets
        """
        keys = []
        for tar in self._targets.values():
            # remove dead targets
            if tar.old_enough(self.max_age):
                keys.append(tar.face.id)
        for k in keys:
            try:
                del self._targets[k]
            except KeyError:
                print(f'KeyError: tar.id = {k}')
            else:
                heapq.heappush(self._recycled_ids, k)

    @thread_error_catcher
    def _generate_id(self) -> int:
        """
        generate id as small as possible
        """
        try:
            return heapq.heappop(self._recycled_ids)
        except IndexError:
            return len(self._targets)


class IdentifierTask(Tracker):
    """
    :param manager:IdentifyManager
    """

    def __init__(
            self,
            jobs: ClosableQueue,
            results: ClosableQueue,
            manager: IdentifyManager):
        super().__init__(manager)
        self.jobs = jobs
        self.results = results

    @profile
    @thread_error_catcher
    def run_identify(self):
        for img in self.jobs:
            identified = self.identified_results(img)
            self.results.put(identified)

        return "IdentifierTask Done"
