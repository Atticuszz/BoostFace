"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 08/02/2024
@Description  :
"""

import logging
import sys
from collections.abc import Generator, Iterable
from pathlib import Path

import cv2
import numpy as np
from numpy.lib.npyio import NpzFile

from src.boostface.base import Face, Image
from src.boostface.inference import DetectorBase
from src.boostface.utils.download import download_lfw

# TODO: test arcface accuracy with the cropped face **test_result** by cuda or not
# TODO: test milvus search performance with the cropped face **test_result** by cuda or not


# TODO: test together with the face extract and search in milvus to see the performance


class LFW(Iterable):
    """LFW dataset"""

    def __init__(self):
        # define source from where
        self._root = (
            Path(__file__).parent / "data" / "lfw-deepfunneled" / "lfw-deepfunneled"
        )
        self._npz_path = self._root.parent / "lfw_images.npz"
        self._image_paths = list(self._root.rglob("*.jpg"))

        # define iterable contents
        self.images: list[Image] = []
        self.names: list[str] = []

        # download lfw if not exists
        if not self._root.exists():
            download_lfw()

    def load_images(self):
        """load images from npz file or image files"""
        if self._npz_path.exists():
            self._load_from_npz()
        else:
            self._load_from_image()

    def _load_from_npz(self):
        """load images from npz file"""
        logging.info("Loading images from npz file...")
        data: NpzFile = np.load(self._npz_path)

        self.images = data["images"]
        self.names = data["names"]

    def _load_from_image(self):
        """load images from image files and save to npz file"""
        logging.info("Loading and saving images to npz file...")
        for i, path in enumerate(self._image_paths):
            sys.stdout.write(f"\rLoading {i + 1}/{len(self._image_paths)} images")
            sys.stdout.flush()
            self.images.append(cv2.imread(path.as_posix()))
            self.names.append(path.stem)
        sys.stdout.write("\n")

    def _flush_into_npz(self):
        """flush images into npz file"""
        logging.info("compressing images to npz file ...")
        np.savez_compressed(
            self._npz_path, images=np.array(self.images), names=np.array(self.names)
        )
        logging.info(f"Saved images to {self._npz_path}")

    def __len__(self):
        return len(self.images)

    def __iter__(self) -> Generator[tuple[str, Image], None, None]:
        yield from zip(self.names, self.images)


class LFWCrop(LFW):
    """cropped by face detection model"""

    def __init__(
        self,
        detector: DetectorBase,
        threshold: float = 0.8,
        cropped_size: tuple[int, int] = (320, 320),
    ):
        super().__init__()
        self.cropped_npz_path = self._npz_path.parent / "lfw_cropped_images.npz"
        self.detector = detector
        self.threshold = threshold
        self.cropped_size = cropped_size

    def load_cropped_images(self):
        """load cropped images from npz file or crop the images and save to npz file"""
        if self.cropped_npz_path.exists():
            self._npz_path = self.cropped_npz_path
            self._load_from_npz()
        else:
            self._crop_images()

    def _crop_images(self):
        """load from lfw and crop the face into self.cropped_npz_path"""
        self.load_images()
        logging.info("Cropping images...")
        crop_image: list[Image] = []
        crop_image_names: list[str] = []
        for i, (name, image) in enumerate(self):
            sys.stdout.write(f"\rCropping {i + 1}/{len(self)} images")
            sys.stdout.flush()
            face: Face | None = self.detector.detect_faces(image)
            if face and face.det_score > self.threshold:
                resized_image = cv2.resize(face.face_image, self.cropped_size)
                crop_image.append(resized_image)
                crop_image_names.append(name)

                # cv2.imshow("face", face.face_image)
                # cv2.waitKey(0)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break

        sys.stdout.write("\n")
        self.images = crop_image
        self.names = crop_image_names
        self._npz_path = self.cropped_npz_path
        self._flush_into_npz()


lfw = LFW()
lfw_cropped = LFWCrop(DetectorBase())
if __name__ == "__main__":
    lfw_cropped.load_cropped_images()
    for name, img in lfw_cropped:
        cv2.imshow("img", img)
        cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
