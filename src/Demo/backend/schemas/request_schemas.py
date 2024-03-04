from dataclasses import dataclass

import cv2
import numpy as np
from pydantic import BaseModel, Field

from ..services.inference.common import Face, Image, Kps
from ..utils.base64_decode import decode_base64


class Face2SearchSchema(BaseModel):
    """Face2Search schema to transfer data"""

    face_img: str = Field(..., description="Base64 encoded image data")
    kps: list[list[float]] = Field(..., description="Keypoints")
    det_score: float = Field(..., description="Detection score")
    uid: str = Field(..., description="Face ID")


@dataclass
class Face2Search:
    """date to search in milvus"""

    face_img: Image
    kps: Kps
    det_score: float
    uid: str

    @classmethod
    def from_schema(cls, schema: BaseModel) -> "Face2Search":
        """init from request schema"""
        # 将 base64 编码的图像转换为 Image 类型 (NumPy ndarray)
        image_data = decode_base64(schema.face_img)
        image = cv2.imdecode(
            np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if image is None:
            raise ValueError("Failed to decode image")

        kps = np.array(schema.kps, dtype=np.float64)

        return cls(face_img=image, kps=kps, det_score=schema.det_score, uid=schema.uid)

    def to_face(self) -> Face:
        """turn into face"""
        return Face(
            img=self.face_img,
            face_id=self.uid,
            kps=self.kps,
            det_score=self.det_score,
            embedding=None,
        )
