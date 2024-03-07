"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 10/02/2024
@Description  :
"""

import logging
import sys

import cv2
import onnxruntime
from src.boostface.dataset_loader.lfw_loader import lfw, lfw_cropped
from src.boostface.inference import detector


def show_lfw_face():
    logging.info(onnxruntime.get_device())
    logging.info(f"Total number of images in LFW: {len(lfw)}")
    cnt = 0
    for name, img in lfw:
        res = detector.detect_faces(img)
        # logging.info(f"detected faces:{name}")
        if res and res.det_score > 0.75:
            sys.stdout.write(f"\rdetected  {cnt + 1}/{len(lfw)} images")
            sys.stdout.flush()

            cnt += 1
            cv2.imshow("lfw", res.face_image)

            cv2.waitKey(0)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break


def show_cropped_lfw():
    lfw_cropped.load_cropped_images()
    for name, img in lfw_cropped:
        cv2.imshow("img", img)
        cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


if __name__ == "__main__":
    pass
