"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""

from pathlib import Path

from ..base import DetectedResult, Face, Image
from ..utils.download import download_scrfd
from .model_zoo.model_router import get_model


class DetectorBase:
    """
    scrfd det_2.5g.onnx with onnxruntime
    """

    def __init__(self):
        root = Path(__file__).parent / "model_zoo" / "models" / "det_2.5g.onnx"
        if not root.exists():
            root.parent.mkdir(exist_ok=True, parents=True)
            download_scrfd(output_dir=root.parent)

        if not root.exists():
            raise FileNotFoundError(
                f"can't find {root} after download from github release"
            )

        self.detector_model = get_model(
            root, providers=("CUDAExecutionProvider", "CPUExecutionProvider")
        )
        prepare_params = {"ctx_id": 0, "det_thresh": 0.5, "input_size": (320, 320)}
        self.detector_model.prepare(**prepare_params)

    def detect_faces(self, img2detect: Image) -> Face | None:
        """detect faces from given image"""
        detect_params = {"max_num": 0, "metric": "default"}
        bboxes, kpss = self.detector_model.detect(img2detect, **detect_params)
        face: Face | None = None
        for i in range(bboxes.shape[0]):
            kps = kpss[i] if kpss is not None else None
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            detected = DetectedResult(bbox, kps, det_score)
            face = Face(detected, img2detect)
        return face


detector = DetectorBase()
