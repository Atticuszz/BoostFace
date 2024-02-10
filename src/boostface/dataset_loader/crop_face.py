"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 08/02/2024
@Description  :
"""
import logging
from pathlib import Path

import cv2

from src.boostface.base import Image
from src.boostface.utils.download import download_lfw


# TODO: use the face detection model to crop the face from the image
# TODO: test arcface accuracy with the cropped face **test_result** by cuda or not
# TODO: test milvus search performance with the cropped face **test_result** by cuda or not
# TODO: test together with the face extract and search in milvus to see the performance


class LFW:
    def __init__(self):
        self.root = Path(__file__).parent / "data" / "lfw-deepfunneled" / "lfw-deepfunneled"
        if not self.root.exists():
            download_lfw()
        self._num_of_image = 0

    def __len__(self):
        if self._num_of_image == 0:
            self._num_of_image = len(list(self.root.rglob("*.jpg")))
        return self._num_of_image

    def __iter__(self) -> Image:
        for image in self.root.rglob("*.jpg"):
            yield cv2.imread(image.as_posix())




lfw = LFW()

if __name__ == "__main__":
    lfw = LFW()
    logging.info(f"Total number of images in LFW: {len(lfw)}")
    for img in lfw:
        cv2.imshow("lfw", img)
        cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

