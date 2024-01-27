"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""
from time import sleep

from src.app.common.types import Image
from src.app.utils.boostface.common import ImageFaces
from src.app.utils.boostface.component.camera import Camera
from src.app.utils.boostface.component.detector import Detector
from src.app.utils.boostface.component.drawer import Drawer
from src.app.utils.boostface.component.identifier import Identifier
from src.app.utils.decorator import error_handler
from src.app.utils.time_tracker import time_tracker


class BoostFace:
    """
    sub-threads:
        camera
    """

    def __init__(self):
        self._camera = Camera()
        self._detector = Detector()
        self._detector.connect_jobs_queue(self._camera.result_queue)
        self._identifier = Identifier()
        self._draw = Drawer()

    @error_handler
    @time_tracker.track_func
    def get_result(self) -> ImageFaces:
        """
        :exception CameraOpenError
        :return: Image
        """
        # FIXME: run it for while will crash the app
        img = self._camera.produce()
        detected = self._detector.produce()
        identified = self._identifier.identify(detected)
        draw_on = self._draw.show(identified)
        return draw_on

    def wake_up(self):
        self._camera.wake_up()
        self._detector.wake_up()

    def sleep(self):
        self._camera.sleep()
        self._detector.sleep()

    @error_handler
    def stop_app(self):
        self._camera.stop()
        self._detector.stop()
        self._identifier.stop_ws_client()
