"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 08/02/2024
@Description  :
"""
import logging
import sys
from collections.abc import Generator
from pathlib import Path

import cv2
import numpy as np

from src.boostface.base import Image
from src.boostface.utils.download import download_lfw

# TODO: use the face detection model to crop the face from the image
# TODO: test arcface accuracy with the cropped face **test_result** by cuda or not
# TODO: test milvus search performance with the cropped face **test_result** by cuda or not
# TODO: test together with the face extract and search in milvus to see the performance


class LFW:
    def __init__(self):
        self.root = (
            Path(__file__).parent / "data" / "lfw-deepfunneled" / "lfw-deepfunneled"
        )
        self.npz_path = self.root.parent / "lfw_images.npz"
        if not self.root.exists():
            download_lfw()

        if self.npz_path.exists():
            logging.info("Loading images from npz file...")
            data = np.load(self.npz_path)
            self.images = data["images"]
            self.names = data["names"]
        else:
            logging.info("Loading and saving images to npz file...")
            self.image_paths = list(self.root.rglob("*.jpg"))
            self.images = []
            self.names = []
            for i, path in enumerate(self.image_paths):
                sys.stdout.write(f"\rLoading {i + 1}/{len(self.image_paths)} images")
                sys.stdout.flush()
                self.images.append(cv2.imread(path.as_posix()))
                self.names.append(path.stem)
            sys.stdout.write("\n")
            logging.info("compressing images to npz file ...")
            np.savez_compressed(
                self.npz_path, images=np.array(self.images), names=np.array(self.names)
            )
            logging.info(f"Saved images to {self.npz_path}")

    def __len__(self):
        return len(self.images)

    def __iter__(self) -> Generator[tuple[str, Image], None, None]:
        yield from zip(self.names, self.images)


lfw = LFW()

if __name__ == "__main__":
    lfw = LFW()
    logging.info(f"Total number of images in LFW: {len(lfw)}")
    for img in lfw:
        cv2.imshow("lfw", img)
        cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
