import collections
import logging
from logging.handlers import QueueHandler
from multiprocessing import Process, Event, Queue
from pathlib import Path

from boostface.types import Embedding
from app.services.inference.common import Face, TaskType
from .model_zoo import ArcFaceONNX
from .model_zoo import get_model
from ..db.operations import Matcher, Registrar

matched_and_in_screen_deque = collections.deque(maxlen=1)


class Extractor:
    """
    extract face embedding from given target bbox and kps, and det_score by running model in onnx
    """

    def __init__(self):
        root = Path(__file__).parent / \
            'model_zoo' / 'models' / 'irn50_glint360k_r50.onnx'
        self.rec_model: ArcFaceONNX = get_model(root, providers=(
            'CUDAExecutionProvider', 'CPUExecutionProvider'))
        self.rec_model.prepare(ctx_id=0)

    def run_onnx(self, face: Face) -> Embedding:
        """
        get embedding of face from given target kps, and det_score
        :return: face embedding
        """
        self.rec_model.get(face.img, face)
        logging.debug(f"extractor extracted {face.face_id} embedding")
        return face.normed_embedding


class IdentifyWorker(Process):
    """
    solo worker for extractor and then search by milvus
    """

    def __init__(
            self,
            task_queue: Queue,
            result_queue: Queue,
            registered_queue: Queue,
            sub_process_msg_queue: Queue):
        super().__init__(daemon=True)
        self._registrar = None
        self._matcher = None
        self._extractor = None
        self.registered_queue = registered_queue
        self._is_running = Event()
        self._task_queue = task_queue  # Queue[tuple[TaskType, Face]]
        self._result_queue = result_queue  # Queue[MatchedResult]
        self._msg_queue = sub_process_msg_queue

    def start(self) -> None:
        self._is_running.set()
        super().start()

    def run(self):
        """long time works in a single process"""
        self._configure_logging()
        self._extractor = Extractor()
        self._matcher = Matcher()
        self._registrar = Registrar()
        logging.debug("IdentifyWorker running")
        while self._is_running.is_set():
            task_type, face = self._task_queue.get()
            if task_type == TaskType.IDENTIFY:
                self._identify(face)
            elif task_type == TaskType.REGISTER:
                self._register(face)
            else:
                raise TypeError("task_type must be TaskType")

    def stop(self):
        self._is_running.clear()
        if self._matcher:
            self._matcher.stop_client()
        super().join()
        logging.debug("IdentifyWorker stop")

    def _identify(self, face: Face):
        normed_embedding = self._extractor.run_onnx(face)
        match_info = self._matcher.search(normed_embedding)
        match_info.face_id = face.face_id
        assert match_info is not None, "match_info must not be None"
        self._result_queue.put(match_info)

    def _register(self, face: Face):
        normed_embedding = self._extractor.run_onnx(face)
        self._registrar.sign_up(
            normed_embedding,
            face.sign_up_id,
            face.sign_up_name)
        # self._result_queue.put(face.face_id)

    def _configure_logging(self):
        queue_handler = QueueHandler(self._msg_queue)
        # queue_handler.setFormatter(log_format)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(queue_handler)
