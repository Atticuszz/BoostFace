"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""

import logging

from .common import ImageFaces
from .component.camera import Camera, CameraOpenError
from .component.detector import Detector
from .component.drawer import Drawer
from .component.identifier import Identifier
from .settings import CameraConfig, DetectorConfig, TrackerConfig
from .types import Image
from .utils.decorator import error_handler
from .utils.time_tracker import time_tracker

logger = logging.getLogger(__name__)


class BoostFace:
    def __init__(
        self,
        camera_config: CameraConfig,
        detector_config: DetectorConfig,
        tracker_config: TrackerConfig,
    ):
        self._camera = Camera(camera_config)
        self._detector = Detector(detector_config)
        self._identifier = Identifier(tracker_config)
        self._draw = Drawer()

    @error_handler
    def get_result(self, image: Image | None = None) -> Image:
        """
        :exception CameraOpenError
        :return: Image
        """
        if image is None:
            frame: ImageFaces = self._camera.read()
        else:
            frame = ImageFaces(image=image, faces=[])
        detected = self._detector.run_onnx(frame)
        identified = self._identifier.identify(detected)
        draw_on = self._draw.show(identified)
        return draw_on.nd_arr

    @error_handler
    def stop_app(self):
        self._identifier.stop_ws_client()
