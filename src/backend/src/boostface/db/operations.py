# coding=utf-8
import traceback
import warnings
from pathlib import Path
from timeit import default_timer

import cv2
import numpy as np
from numpy import ndarray
from numpy.linalg import norm
from pymilvus.orm import utility

from boostface.types import MatchInfo, Image
from app.services.inference.common import Embedding, Image2Detect
from src.boostface.db.milvus_client import MilvusClient

__all__ = ["Register", "Matcher"]


class Matcher:
    """
    继承milvus_client ,作为匹配器
    """

    def __init__(self, threshold=0.5, **kwargs):
        self._client = MilvusClient(**kwargs)
        self._threshold = threshold
        print("Loading collection to RAM")
        self._client.collection.load(timeout=10)
        utility.wait_for_loading_complete(
            self._client.collection.name, timeout=10)

    def __enter__(self):
        """:
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context and shut down the client. Logs exception if occurred.

        :param exc_type: Exception type if an exception occurred.
        :param exc_val: Exception value if an exception occurred.
        :param exc_tb: Traceback information if an exception occurred.
        """
        if exc_type is not None:
            print(f"An exception occurred: {exc_type.__name__}")
            print(f"Exception message: {exc_val}")
            print("Exception traceback:")
            traceback.print_tb(exc_tb)

        self._client.shut_down()

    def search(self, embedding: Embedding) -> MatchInfo:
        """
        :param embedding: must be normed
        :return: uuid and score of matched face
        """
        assert np.isclose(norm(embedding), 1), "embedding must be normed"
        results: list[list[dict]] = self._client.search([embedding])
        ret = MatchInfo(uid='', score=0.0)
        for i, result in enumerate(results):
            result = result[0]  # top_k=1
            # if result['score'] > self._threshold:
            ret = MatchInfo(uid=str(result['id']), score=result['score'])
        return ret


class Register:
    def __init__(self, client: MilvusClient):
        from src.boostface.component.detector import Detector
        from src.boostface.component.identifier import Extractor
        self._client = client
        self._detector = Detector()
        self._extractor = Extractor()

    def sign_up(self, images: Image, id: str):
        image2detect: Image2Detect = Image2Detect(images, [])
        res_det: Image2Detect = self._detector.run_onnx(image2detect)
        if len(res_det.faces) != 1:
            warnings.warn("register image must have one face")
            return

        embedding: Embedding = self._extractor.run_onnx(
            image2detect.nd_arr,
            res_det.faces[0].bbox,
            res_det.faces[0].kps,
            res_det.faces[0].det_score)
        self._insert(embedding, id)

    def _insert(self, embedding: ndarray[512], id: str):
        assert np.isclose(norm(embedding), 1), "embedding must be normed"
        self._client.insert(
            [np.array([id]), np.array(['name']), np.array([embedding])])

    # 批量插入
    def _insert_batch(self, faces: list[list[ndarray[512], str, str]]):
        ids = []
        embeddings = []
        names = []
        for embedding, id, name in faces:
            assert np.isclose(norm(embedding), 1), "embedding must be normed"
            ids.append(id)
            embeddings.append(embedding)
            names.append(name)
        self._client.insert(
            [np.array(ids), np.array(names), np.array(embeddings)])


# register = Register(client)
# matcher = Matcher(client)
if __name__ == '__main__':

    client = MilvusClient()
    register = Register(client)
    image_dir: Path = Path(__file__).parent / "data\\test_01\\known"
    assert image_dir.exists() and image_dir.is_dir(), "image_dir must be a dir"
    i = 0
    for image_path in image_dir.iterdir():
        i += 1
        start = default_timer()
        img: Image | None = cv2.imread(image_path.as_posix())
        if img is None:
            warnings.warn(f"image {image_path.name} is None")
            continue
        register.sign_up(img, image_path.name)
        print(
            f"registered {i}/13261 image:{image_path.name} cost:{default_timer() - start}")
