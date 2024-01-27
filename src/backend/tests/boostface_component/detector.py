# coding=utf-8
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import cv2
import numpy as np

from src.boostface.component.camera import CameraTask
from app.services.inference.common import ClosableQueue
from src.boostface.component.detector import DetectorTask
from src.boostface.utils.decorator import thread_error_catcher
from src.boostface.utils.draw import draw_bbox


@thread_error_catcher
def read_video(res_queue: ClosableQueue):
    print("read_video start")
    for img in res_queue:
        print("read_video start")
        imgshow = img.nd_arr
        if isinstance(imgshow, np.ndarray):
            for face in img.faces:
                draw_bbox(imgshow, face.bbox, (0, 255, 0))
            cv2.imshow("video", imgshow)
        else:
            print("read_video None")
        if cv2.waitKey(1) == ord('q'):
            break


if __name__ == '__main__':
    with ThreadPoolExecutor() as executor:
        src = ClosableQueue("camera read", maxsize=200)
        detected = ClosableQueue("detected", maxsize=200)
        if_done = Event()

        my_camera = CameraTask(src, if_done)
        detect_task = DetectorTask(src, detected)
        executor.submit(my_camera.run)
        executor.submit(detect_task.run)
        executor.submit(read_video, detected)

        executor.shutdown(wait=True)
