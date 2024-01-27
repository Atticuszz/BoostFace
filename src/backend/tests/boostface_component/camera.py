# coding=utf-8
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from time import sleep

import cv2
import numpy as np

from src.boostface.component.camera import CameraTask
from app.services.inference.common import ClosableQueue


def read_video(res_queue: ClosableQueue):
    print("read_video start")
    for img in res_queue:

        imgshow = img.nd_arr
        if isinstance(imgshow, np.ndarray):
            sleep(0.03)
            cv2.imshow("video", imgshow)
        else:
            print("read_video None")
        if cv2.waitKey(1) == ord('q'):
            break


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as executor:
        res_queue = ClosableQueue("camera read", maxsize=200)
        if_done = Event()

        my_camera = CameraTask(res_queue, if_done)
        executor.submit(my_camera.run)
        executor.submit(read_video, res_queue)

        executor.shutdown(wait=True)
