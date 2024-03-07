"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 10/02/2024
@Description  :
"""

from dataclasses import dataclass

import numpy as np
from numpy._typing import NDArray
from src.boostface.db.base_model import MatchedResult

Kps = NDArray[np.float64]  # shape: (5, 2)
Bbox = NDArray[np.float64]  # shape: (4, 2)
Embedding = NDArray[np.float64]  # shape: (512, )
Image = NDArray[np.uint8]  # shape: (height, width, 3)


# @dataclass
# class Face2Search:
#     face_img: Image
#     kps: Kps
#     det_score: float
#     uid: str
#
#     @classmethod
#     def from_schema(cls, schema: BaseModel) -> "Face2Search":
#         """init from request schema"""
#         # 将 base64 编码的图像转换为 Image 类型 (NumPy ndarray)
#         image_data = decode_base64(schema.face_img)
#         image = cv2.imdecode(
#             np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR
#         )
#         if image is None:
#             raise ValueError("Failed to decode image")
#
#         kps = np.array(schema.kps, dtype=np.float64)
#
#         return cls(face_img=image, kps=kps, det_score=schema.det_score, uid=schema.uid)
#
#     def to_face(self) -> Face:
#         """turn into face"""
#         return Face(
#             img=self.face_img,
#             uid=self.uid,
#             kps=self.kps,
#             det_score=self.det_score,
#             embedding=None,
#         )


@dataclass
class DetectedResult:
    bbox: Bbox
    kps: Kps
    det_score: float


class Face:
    """face"""

    def __init__(
        self,
        detectedResult: DetectedResult,
        scene_image: Image,
    ):
        self.bbox = detectedResult.bbox
        self.kps = detectedResult.kps
        self.det_score = detectedResult.det_score
        self.scene_image = scene_image
        self.embedding: Embedding = np.zeros(512)
        self.match_info: MatchedResult | None = None

    @property
    def face_image(self) -> Image:
        # 确保 bbox 中的值是整数
        x1, y1, x2, y2 = map(
            int, [self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3]]
        )

        # 避免超出图像边界
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(self.scene_image.shape[1], x2)  # scene.shape[1] 是图像的宽度
        y2 = min(self.scene_image.shape[0], y2)  # scene.shape[0] 是图像的高度

        # 裁剪人脸图像
        face_img = self.scene_image[y1:y2, x1:x2]

        return face_img
