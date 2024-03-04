"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""

import logging

from .common import ImageFaces
from .component.camera import Camera, Camera, CameraOpenError
from .component.detector import Detector, Detector
from .component.drawer import Drawer
from .component.identifier import Identifier
from .utils.decorator import error_handler
from .utils.time_tracker import time_tracker

logger = logging.getLogger(__name__)


class BoostFace:
    def __init__(self):
        self._camera = Camera()
        self._detector = Detector()
        self._identifier = Identifier()
        self._draw = Drawer()

    @error_handler
    @time_tracker.track_func
    def get_result(self) -> ImageFaces:
        """
        :exception CameraOpenError
        :return: Image
        """

        frame: ImageFaces = self._camera.read()
        detected = self._detector.run_onnx(frame)
        identified = self._identifier.identify(detected)
        draw_on = self._draw.show(identified)
        return draw_on

    @error_handler
    def stop_app(self):
        self._identifier.stop_ws_client()


onnx_runner = BoostFace()
