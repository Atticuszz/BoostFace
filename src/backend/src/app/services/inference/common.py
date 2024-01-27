import uuid
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np
from numpy._typing import NDArray
from numpy.linalg import norm as l2norm

from app.services.db.base_model import MatchedResult


Kps = NDArray[np.float64]  # shape: (5, 2)
Bbox = NDArray[np.float64]  # shape: (4, 2)
Embedding = NDArray[np.float64]  # shape: (512, )
Image = NDArray[np.uint8]  # shape: (height, width, 3)


@dataclass
class SignUpInfo:

    id: str
    name: str


@dataclass
class Face:
    """pure face img"""
    img: Image
    face_id: uuid
    kps: Kps
    sign_up_id: str = ''
    sign_up_name: str = ''
    det_score: float = 0.0
    embedding: Embedding | None = None

    @property
    def normed_embedding(self) -> Embedding:
        return self.embedding / l2norm(self.embedding)


class TaskType(Enum):
    IDENTIFY = auto()
    REGISTER = auto()


@dataclass
class TaskItem:
    task_type: TaskType
    face: Face
    # bool for register, MatchedResult for identify
    result: MatchedResult | bool | None = None
