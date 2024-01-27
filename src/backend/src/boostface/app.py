# coding=utf-8
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import cv2
import numpy as np

from .component.camera import CameraTask
from app.services.inference.common import ClosableQueue, IdentifyManager
from .component.detector import DetectorTask
from .component.identifier import IdentifierTask
from .utils.decorator import thread_error_catcher
from .utils.draw import draw_bbox, draw_text


@thread_error_catcher
def read_video(res_queue: ClosableQueue):
    print("read_video start")
    for img in res_queue:
        if img is None:
            Warning("read_video None")
            continue
        imgshow = img.nd_arr
        if isinstance(imgshow, np.ndarray):
            for face in img.faces:
                draw_bbox(imgshow, face.bbox, (0, 255, 0))
                draw_text(imgshow, face.bbox, face.match_info.uid)
            cv2.imshow("video", imgshow)
        else:
            print("read_video None")
        if cv2.waitKey(1) == ord('q'):
            break

# TODO: reduce to adapt the cloud fun for fastapi
def boostface(identifier_manager: IdentifyManager, if_done: Event):
    """start BoostFace application.
    :param identifier_manager: IdentifyManager
    :param if_done: Event
    """
    with ThreadPoolExecutor() as executor:
        src = ClosableQueue("camera read", maxsize=200)
        detected = ClosableQueue("detected", maxsize=200)
        identified = ClosableQueue("identified", maxsize=200)

        identify_task = IdentifierTask(
            detected, identified, identifier_manager)
        executor.submit(identify_task.run_identify)

        my_camera = CameraTask(src, if_done)
        detect_task = DetectorTask(src, detected)

        executor.submit(my_camera.run_camera)
        executor.submit(detect_task.run_detection)

        executor.submit(read_video, identified)

        executor.shutdown(wait=True)
