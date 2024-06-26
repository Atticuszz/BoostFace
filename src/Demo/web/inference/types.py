import base64
import uuid
from dataclasses import dataclass

import cv2
import numpy as np
from numpy._typing import NDArray
from pydantic import BaseModel, Field

from .utils.decorator import error_handler

Kps = NDArray[np.float64]  # shape: (5, 2)
Bbox = NDArray[np.float64]  # shape: (4, 2) #FIXME: (4, )
Embedding = NDArray[np.float64]  # shape: (512, )
Image = NDArray[np.uint8]  # shape: (height, width, 3)
Color = tuple[int, int, int]


class Face2SearchSchema(BaseModel):
    """Face2Search schema to transfer data"""

    face_img: str = Field(..., description="Base64 encoded image data")
    kps: list[list[float]] = Field(..., description="Keypoints")
    det_score: float = Field(..., description="Detection score")
    uid: str = Field(..., description="Face Instance UID")


@dataclass
class IdentifyResult:
    """Identify results for face from backend"""

    registered_id: str  # uid for first time register and in the database
    uid: str
    name: str
    time: str
    score: float

    @classmethod
    def from_dict(cls, data: dict) -> "IdentifyResult":
        return cls(**data)


@dataclass
class MatchedResult:
    """attribute of class Face,created from backend identify result."""

    uid: str = str(uuid.uuid4())  # for search
    registered_id: str = ""  # for show
    score: float = 0.0
    name: str = "unknown"

    @classmethod
    def from_IdentifyResult(cls, identify_result: IdentifyResult) -> "MatchedResult":
        return cls(
            uid=identify_result.uid,
            registered_id=identify_result.registered_id,
            score=identify_result.score,
            name=identify_result.name,
        )


@dataclass
class WebsocketRSData:
    """Websocket sender and receive data"""

    def to_schema(self) -> BaseModel:
        """data to schema"""
        raise NotImplementedError


@dataclass
class Face2Search(WebsocketRSData):
    """
    face to search, it is a image filled with face for process transfer
    :attr uid: face instance uid
    """

    face_img: Image
    kps: Kps
    det_score: float
    uid: str

    @error_handler
    def to_base64(self) -> str:
        """将图像转换为 base64 编码的字符串"""
        retval, buffer = cv2.imencode(".jpg", self.face_img)
        if not retval:
            raise ValueError("Failed to encode image")
        image_base64 = base64.b64encode(buffer).decode("utf-8")
        return image_base64

    @error_handler
    def to_schema(self) -> Face2SearchSchema:
        """将 Face2Search 对象转换为 schema 对象"""
        # qt_logger.debug(f"face2search to schema:{self.bbox}")
        # qt_logger.debug(f"face2search to schema:{self.kps}")
        return Face2SearchSchema(
            face_img=self.to_base64(),
            kps=self.kps.tolist(),
            det_score=self.det_score,
            uid=self.uid,
        )
