import logging
import uuid
from collections import deque
from dataclasses import dataclass
from threading import Event, Thread

import numpy as np

from .types import Bbox, Embedding, Face2Search, Image, Kps, MatchedResult

logger = logging.getLogger(__name__)

class Face:
    """face"""

    def __init__(
        self,
        bbox: Bbox,
        kps: Kps,
        det_score: float,
        scene_scale: tuple[int, int, int, int],
        face_id: str | None = None,
    ):
        """
        init a face
        :param bbox:shape [4,2]
        :param kps: shape [5,2]
        :param det_score:
        :param scene_scale: (x1,y1,x2,y2) of scene image
        """
        self.bbox: Bbox = bbox
        self.kps: Kps = kps
        self.det_score: float = det_score
        self.scene_scale: tuple[int, int, int, int] = scene_scale
        self.embedding: Embedding = np.zeros(512)
        self.id = face_id if face_id else str(uuid.uuid4())
        self.match_info = MatchedResult(uid=self.id)


    def face_image(self, scene: Image) -> Face2Search:
        """
        get face image from scense
        :param scene:
        :return:
        """
        # 确保 bbox 中的值是整数
        x1, y1, x2, y2 = map(
            int, [self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3]]
        )

        # 避免超出图像边界
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(scene.shape[1], x2)  # scene.shape[1] 是图像的宽度
        y2 = min(scene.shape[0], y2)  # scene.shape[0] 是图像的高度

        # 裁剪人脸图像
        face_img = scene[y1:y2, x1:x2]
        bbox = np.array([0, 0, face_img.shape[1], face_img.shape[0]])

        # 调整关键点位置
        kps = self.kps - np.array([x1, y1])

        return Face2Search(face_img, kps, self.det_score, self.match_info.uid)


class ImageFaces:
    """
    image to detect
    :param image: image
    :param faces: [face, face, ...]
    """

    def __init__(self, image: Image, faces: list[Face]):
        self.nd_arr: Image = image
        self.faces: list[Face] = faces

    @property
    def scale(self) -> tuple[int, int, int, int]:
        """
        :return: (x1, y1, x2, y2)
        """
        return 0, 0, self.nd_arr.shape[1], self.nd_arr.shape[0]


class ThreadBase(Thread):
    """CameraBase thread"""

    def __init__(self):
        super().__init__()
        self._jobs_queue = deque(maxlen=1000)
        self._result_queue = deque(maxlen=1000)
        self._is_running = Event()
        self._is_sleeping = Event()
        self._is_running.set()
        self._is_sleeping.set()

    def run(self):
        """long time thread works"""

    def produce(self) -> ImageFaces:
        """read from result_queue"""

    @property
    def result_queue(self):
        """result_queue"""
        return self._result_queue

    def connect_jobs_queue(self, result_queue: deque):
        """connect jobs_queue"""
        self._jobs_queue = result_queue

    def wake_up(self):
        """wake up thread"""
        self._is_sleeping.set()

    def sleep(self):
        """sleep thread"""
        self._is_sleeping.clear()

    def stop(self):
        """release camera and kill thread"""
        self._is_sleeping.set()
        self._is_running.clear()
