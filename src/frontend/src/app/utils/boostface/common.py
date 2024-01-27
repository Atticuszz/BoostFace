import queue
import uuid
from collections import deque
from dataclasses import dataclass
from threading import Thread, Event
from typing import Any

import numpy as np
from PyQt6.QtCore import QThread, pyqtSlot

from src.app.common import signalBus
from src.app.config import qt_logger
from src.app.utils.time_tracker import time_tracker
from src.app.common.types import Image, Bbox, Kps, Embedding, MatchedResult, Face2Search


@dataclass
class SignUpInfo:

    id: str
    name: str


class Face:
    """face"""

    def __init__(
            self,
            bbox: Bbox,
            kps: Kps,
            det_score: float,
            scene_scale: tuple[int, int, int, int],
            face_id: str | None = None
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
        self.sign_up_info = SignUpInfo(id=face_id,name='')

    def face_image(self, scene: Image) -> Face2Search:
        """
        get face image from scense
        :param scene:
        :return:
        """
        # 确保 bbox 中的值是整数
        x1, y1, x2, y2 = map(
            int, [self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3]])

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

        return Face2Search(
            face_img,
            kps,
            self.det_score,
            self.match_info.uid)


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
        pass

    def produce(self) -> ImageFaces:
        """read from result_queue"""
        pass

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
        """release camera and kill thread """
        self._is_sleeping.set()
        self._is_running.clear()


class ClosableQueue(queue.Queue):
    """
    A Queue that can be closed. This queue allows items to be added and removed, but
    can be closed when no more items are expected. When closed, the iterator stops yielding
    new items after draining existing items in the queue.

    :param task_name: Name of the task associated with the queue.
    :param maxsize: Maximum size of the queue. Defaults to 100.
    :param wait_time: Time to wait for an item before closing the queue. Defaults to 5 seconds.
    """

    def __init__(self, task_name: str, maxsize: int = 100, wait_time: int = 5):
        super().__init__(maxsize=maxsize)
        self._task_name = task_name
        self._closed = False
        self._wait_time = wait_time

    def close(self):
        """
        Mark the queue as closed.
        """
        self._closed = True

    def __iter__(self):
        """
        Provide an iterator over items in the queue. The iterator will end when the queue
        is closed and empty.
        """
        while not self._closed or not self.empty():
            with time_tracker.track(f"ClosableQueue.__iter__ task {self._task_name}"):
                try:
                    item = self.get(timeout=self._wait_time)
                    yield item
                except queue.Empty:
                    qt_logger.warn(
                        f"{self._task_name} queue: Waiting for {self._wait_time} sec, no item received. Closing.")
                    self.close()
                    break
                except Exception as e:
                    qt_logger.error(
                        f"{self._task_name} queue: Error while getting item from queue: {e}")
                    break


class WorkingThread(QThread):
    """long time prod_cons task in a thread and auto get queues
    running by  signalBus.is_identify_running
    """
    threads = 0
    prod_cons_queues = [
        ClosableQueue(task_name='read_2_detect'),
        ClosableQueue(task_name='detected_2_identify'),
        ClosableQueue(task_name='identified_2_draw'),
    ]

    def __init__(self, works_name: str, is_consumer=True):
        super().__init__()
        self.works_name = works_name
        self._is_consumer = is_consumer
        # get queues
        if self._is_consumer:
            # only for consumer consume jobs
            self.jobs_queue = self.get_queues()

        self.result_queue = self.get_queues()

        self._is_running = True

        # control all working thread
        signalBus.is_identify_running.connect(self._update_working)

    def produce(self) -> Any:
        """produce"""
        raise NotImplementedError

    def consume(self, item: Any):
        """consume"""
        if self._is_consumer:
            raise NotImplementedError

    def stop_thread(self):
        self._is_running = False
        self.wait()

    def run(self):
        """running long time task in a thread"""
        qt_logger.info(f"{self.works_name} start")
        while self._is_running:
            with time_tracker.track(f"WorkingThread.run task {self.works_name}"):
                try:
                    if self._is_consumer:
                        # continue to consume until queue is empty for a while
                        for item in self.jobs_queue:
                            self.consume(item)
                    else:
                        # continue to produce until queue is full
                        self.result_queue.put(self.produce())
                except Exception as e:
                    qt_logger.error(f"WorkingThread.run error:{e}")
                    break
        qt_logger.info(f"{self.works_name} stop")

    @classmethod
    def get_queues(cls) -> ClosableQueue:
        """distribution queues for working thread"""
        _queue = cls.prod_cons_queues[cls.threads]
        cls.threads += 1
        return _queue

    @pyqtSlot(bool)
    def _update_working(self, is_running: bool):
        """slot to accept signal to update working state"""
        self._is_running = is_running
