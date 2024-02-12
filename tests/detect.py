"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 10/02/2024
@Description  :
"""
import logging

import cv2
import onnxruntime

from src.boostface.dataset_loader.crop_face import LFW
from src.boostface.inference import detector

if __name__ == "__main__":
    logging.info(onnxruntime.get_device())
    lfw = LFW()
    logging.info(f"Total number of images in LFW: {len(lfw)}")
    for img in lfw:
        res = detector.detect_faces(img)
        if res and res.det_score > 0.90:
            cv2.imshow("lfw", res.face_image)

            cv2.waitKey(0)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
