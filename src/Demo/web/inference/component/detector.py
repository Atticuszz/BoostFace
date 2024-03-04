"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""

import logging
from time import sleep

from ...setttings import ModelsConfig
from ..common import Face, ImageFaces, ThreadBase
from ..model_zoo.model_router import get_model
from ..utils.decorator import error_handler
from ..utils.time_tracker import time_tracker

logger = logging.getLogger(__name__)


class Detector:
    """
    scrfd det_2.5g.onnx with onnxruntime
    """

    def __init__(self):
        root = ModelsConfig.detect_model.path()
        logger.info(f"loading detector model from {root}")
        self.detector_model = get_model(
            root, providers=("CUDAExecutionProvider", "CPUExecutionProvider")
        )
        prepare_params = {"ctx_id": 0, "det_thresh": 0.5, "input_size": (320, 320)}
        self.detector_model.prepare(**prepare_params)

    @time_tracker.track_func
    def run_onnx(self, img2detect: ImageFaces) -> ImageFaces:
        """
        run onnx model
        :param img2detect:
        :return: Image2Detect with faces
        """
        detect_params = {"max_num": 0, "metric": "default"}
        bboxes, kpss = self.detector_model.detect(img2detect.nd_arr, **detect_params)
        for i in range(bboxes.shape[0]):
            kps = kpss[i] if kpss is not None else None
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            face: Face = Face(
                bbox,
                kps,
                det_score,
                (0, 0, img2detect.nd_arr.shape[1], img2detect.nd_arr.shape[0]),
            )
            img2detect.faces.append(face)
        logger.debug(f"detector detect {len(img2detect.faces)} faces")
        return img2detect
