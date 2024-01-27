"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""
from pathlib import Path
from time import sleep

from src.app.config import qt_logger
from src.app.utils.boostface.common import ImageFaces, Face, ThreadBase
from ..model_zoo.model_router import get_model
from ...decorator import error_handler
from ...time_tracker import time_tracker


class DetectorBase:
    """
    scrfd det_2.5g.onnx with onnxruntime
    """

    def __init__(self):
        root = Path(__file__).parents[1] / \
            'model_zoo' / 'models' / 'det_2.5g.onnx'
        self.detector_model = get_model(root, providers=(
            'CUDAExecutionProvider', 'CPUExecutionProvider'))
        prepare_params = {'ctx_id': 0,
                          'det_thresh': 0.5,
                          'input_size': (320, 320)}
        self.detector_model.prepare(**prepare_params)

    @time_tracker.track_func
    def run_onnx(self, img2detect: ImageFaces) -> ImageFaces:
        """
        run onnx model
        :param img2detect:
        :return: Image2Detect with faces
        """
        detect_params = {'max_num': 0, 'metric': 'default'}
        bboxes, kpss = self.detector_model.detect(
            img2detect.nd_arr, **detect_params)
        for i in range(bboxes.shape[0]):
            kps = kpss[i] if kpss is not None else None
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            face: Face = Face(
                bbox,
                kps,
                det_score,
                (0,
                 0,
                 img2detect.nd_arr.shape[1],
                 img2detect.nd_arr.shape[0]))
            img2detect.faces.append(face)
        qt_logger.debug(f"detector detect {len(img2detect.faces)} faces")
        return img2detect


class Detector(ThreadBase):
    def __init__(self):
        super().__init__()
        self.detector = DetectorBase()
        super().start()

    @time_tracker.track_func
    def produce(self) -> ImageFaces:
        while True:
            try:
                return self._result_queue.popleft()
            except IndexError:
                # qt_logger.debug("detector._result_queue is empty")
                sleep(0.02)

    @error_handler
    def run(self):
        while self._is_running.is_set():

            self._is_sleeping.wait()
            try:
                img2detect = self._jobs_queue.popleft()
            except IndexError:
                # qt_logger.debug("detector._jobs_queue is empty")
                sleep(0.02)
            else:
                img2detect = self.detector.run_onnx(img2detect)
                self._result_queue.append(img2detect)
