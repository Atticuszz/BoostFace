# coding=utf-8
import dataclasses
import logging
import traceback
import warnings
from datetime import datetime
from pathlib import Path
from timeit import default_timer

import cv2
import numpy as np
from numpy import ndarray
from numpy.linalg import norm
from pymilvus.orm import utility

from app.core.config import logger
from app.services.db.base_model import MatchedResult
from app.services.inference.common import Embedding


__all__ = ["Registrar", "Matcher"]

from tests import data_generator

from ..db.milvus_client import milvus_client


class Matcher:
    """wrapper of MilvusClient"""

    def __init__(self, threshold=0.5):
        self._client = milvus_client
        self._threshold = threshold
        if self._client.get_entity_num > 0:
            logger.debug("Loading collection to RAM")
            self._client.collection.load(timeout=10)
            utility.wait_for_loading_complete(
                self._client.collection.name, timeout=10)

    def search(self, embedding: Embedding) -> MatchedResult:
        """
        :param embedding: must be normed
        :return: uuid and score of matched face
        """
        assert np.isclose(norm(embedding), 1), "embedding must be normed"
        results: list[list[dict]] = self._client.search([embedding])
        for i, result in enumerate(results):
            result = result[0]  # top_k=1
            # TODO: set threshold?
            # if result['score'] > self._threshold:
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.debug(f"matched {result['id']} with score {result['score']}")
            return MatchedResult(id=str(result['id']),
                                 name=result['name'],
                                 score=result['score'],
                                 time=time_now)

    def stop_client(self):
        self._client.shut_down()

# TODO: register if the operation is registered instead of identify


class Registrar:
    def __init__(self):
        self._client = milvus_client

    def sign_up(self, embedding: Embedding, id: str, name: str):

        assert np.isclose(norm(embedding), 1), "embedding must be normed"
        logging.debug(f"registering {id} {name}")
        self._client.insert(
            [np.array([id]), np.array([name]), np.array([embedding])])

    # 批量插入
    def insert_batch(self, faces: list[list[ndarray[512], str, str]]):
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

    def insert_fake_face(self, num: int):
        faces_g = data_generator(num_items=100000)
        i = 0
        for embedding, id, name in faces_g:
            i += 1
            logger.debug(f'inserting {i}th/{num} face')
            self._client.insert(
                [np.array([id]), np.array([name]), np.array([embedding])])




# register = Register(client)
# matcher = Matcher(client)
if __name__ == '__main__':
    pass
    # client = MilvusClient()
    # register = Registrar(client)
    # image_dir: Path = Path(__file__).parent / "data\\test_01\\known"
    # assert image_dir.exists() and image_dir.is_dir(), "image_dir must be a dir"
    # i = 0
    # for image_path in image_dir.iterdir():
    #     i += 1
    #     start = default_timer()
    #     img: Image | None = cv2.imread(image_path.as_posix())
    #     if img is None:
    #         warnings.warn(f"image {image_path.name} is None")
    #         continue
    #     register.sign_up(img, image_path.name)
    #     print(
    # f"registered {i}/13261 image:{image_path.name} cost:{default_timer() -
    # start}")
