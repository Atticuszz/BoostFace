import numpy as np

from src.app.common import signalBus
from src.app.common.client.web_socket import WebSocketClient
from src.app.config import qt_logger
from src.app.utils.time_tracker import time_tracker
from src.app.common.types import Bbox, Kps, MatchedResult, IdentifyResult
from src.app.utils.boostface.common import Face, ImageFaces
from .sort_plus import associate_detections_to_trackers, KalmanBoxTracker
from ...decorator import calm_down


class Target:
    """
    :param face: Face
    :ivar _hit_streak: frames of keeping existing in screen
    :ivar _frames_since_update: frames of keeping missing in screen
    :ivar face: Face
    :ivar _frames_since_identified: frames since reced
    :ivar _tracker: KalmanBoxTracker
    """

    def __init__(self, face: Face):

        self._hit_streak = 0  # frames of keeping existing in screen
        self._frames_since_update = 0  # frames of keeping missing in screen
        self._frames_since_identified = 0
        self.face: Face = face
        self._tracker: KalmanBoxTracker = KalmanBoxTracker(face.bbox)

    @property
    def rec_satified(self) -> bool:
        if self._scale_satisfied and not self._if_matched and self.in_screen:
            return True
        elif self._if_matched and self._scale_satisfied and self._time_satisfied and self.in_screen:
            return True
        else:
            return False

    def update_pos(self, bbox: Bbox, kps: Kps, score: float):
        self.face.bbox = bbox
        self.face.kps = kps
        self.face.det_score = score

    def update_tracker(self, bbox: Bbox):
        """
        update tracker with bbox, and update state of continuation
        """
        self._frames_since_update = 0
        self._hit_streak += 1
        self._tracker.update(bbox)

    def unmatched(self):
        """
        update state of continuation
        :return:
        """
        self._frames_since_update += 1
        self._hit_streak = 0

    def old_enough(self, max_age: int) -> bool:
        """
        if the target is too old ,should be del
        """
        return self._frames_since_update > max_age

    @property
    def in_screen(self, min_hits=3) -> bool:
        """
        if the target is in screen should be satisfied min_hits,forbid the shiver
        """
        # almost 0.1s if fps=30
        return self._hit_streak >= min_hits
        # return True

    @property
    def get_predicted_tar(self) -> Face:
        """
        get predicted Face by tracker
        :return:
        """
        # get predicted bounding box from Kalman Filter
        bbox = self._tracker.predict()[0]
        predicted_face: Face = Face(
            bbox,
            self.face.kps,
            self.face.det_score,
            face_id=self.face.id,
            scene_scale=self.face.scene_scale)
        return predicted_face

    @property
    def name(self) -> str:
        if self._if_matched:
            return self.face.match_info.name
        else:
            return f'target[{self.face.id}]'

    @property
    def _time_satisfied(self) -> bool:
        """
        Checks if the time(frames) elapsed since the target was last identified exceeds a predefined threshold.
        """
        frames_threshold = 100  # almost 3 sec if fps=30
        if not self._if_matched:
            return False
        elif self._frames_since_identified < frames_threshold:
            self._frames_since_identified += 1
            return False
        else:
            self._frames_since_identified = 0
            return True

    @property
    def _scale_satisfied(self) -> bool:
        """
        if the scale of target is satisfied
        """
        # TODO：test to fit
        scale_threshold = 0.005
        target_area = (self.face.bbox[2] - self.face.bbox[0]) * \
                      (self.face.bbox[3] - self.face.bbox[1])
        screen_area = (self.face.scene_scale[3] - self.face.scene_scale[1]) * (
            self.face.scene_scale[2] - self.face.scene_scale[0])
        return (target_area / screen_area) > scale_threshold

    @property
    def _if_matched(self) -> bool:
        return self.face.match_info.Identity_id != ""


class Tracker:
    """
    tracker for a single target
    :param max_age: del as frames not matched
    :param iou_threshold: for Hungarian algorithm
    """

    def __init__(
            self,
            max_age=10,
            iou_threshold=0.3
    ):
        super().__init__()

        self._targets: dict[str, Target] = {}
        self.max_age = max_age
        self.iou_threshold = iou_threshold
        self._recycled_ids = []

    @time_tracker.track_func
    def _update(self, image2update: ImageFaces):
        """
        according to the "memory" in Kalman tracker update former targets info by Hungarian algorithm
        :param image2update:
        """
        detected_tars: list[Face] = image2update.faces

        if self._targets:
            predicted_tars: list[Face] = self._clean_dying()
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
            unmatched_det_tars: list[Face] = detected_tars

        # add new targets
        for detected_tar in unmatched_det_tars:
            self._targets[detected_tar.id] = Target(face=detected_tar)

        self._clear_dead()

    def _clean_dying(self) -> list[Face]:
        """
        clean dying targets from tracker prediction
        :return tracker predictions
        """
        predicted_tars: list[Face] = []
        for tar in self._targets.values():
            raw_tar: Face = tar.get_predicted_tar
            # store key in self.self._targets.values()
            pos = raw_tar.bbox
            if np.any(np.isnan(pos)):
                qt_logger.debug(f"tracker remove {tar.face.id} due to nan")
                del self._targets[tar.face.id]
            else:
                # got new predict tars
                predicted_tars.append(raw_tar)
        return predicted_tars

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
            qt_logger.debug(f"tracker remove {k} due to old enough")
            del self._targets[k]


class Identifier(Tracker):
    def __init__(self):
        super().__init__()
        self.indentify_client = WebSocketClient("identify")
        self.indentify_client.start_ws()

    @time_tracker.track_func
    def identify(self, image2identify: ImageFaces) -> ImageFaces:
        """
        fill image2identify.faces with match info or return MatchInfo directly
        :param image2identify:
        :return: get image2identify match info
        """
        self._update_from_result()
        self._update(image2identify)
        self._search(image2identify)
        # [tar.face.match_info for tar in self._targets.values()]
        # qt_logger.debug(
        # f"identifier identify {len(image2identify.faces)} faces")
        # qt_logger.debug(f"identifier identify {len(self._targets)} targets")
        return ImageFaces(
            image2identify.nd_arr, [
                tar.face for tar in self._targets.values() if tar.in_screen])

    def stop_ws_client(self):
        self.indentify_client.stop_ws()

    @time_tracker.track_func
    def _update_from_result(self):
        """update from client results"""
        while True:
            # FIXME: update slow
            with time_tracker.track("Identifier.receive"):
                result_dict = self.indentify_client.receive()
                if result_dict:
                    # update match info
                    result = IdentifyResult.from_dict(result_dict)
                    qt_logger.debug(f"Identifier receive {result}")
                    for tar in self._targets.values():
                        if tar.face.id == result.uid:
                            tar.face.match_info = MatchedResult.from_IdentifyResult(
                                result)
                            break
                else:
                    break

    @time_tracker.track_func
    def _search(self, image2identify: ImageFaces):
        """ send data to search"""
        for tar in self._targets.values():
            if tar.rec_satified:  # FIXME: seems like send data under wrong condition，send too much
                data_2_send = tar.face.face_image(image2identify.nd_arr)
                self.indentify_client.send(data_2_send)
