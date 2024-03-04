"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""
import logging

from .common import ImageFaces
from .component.camera import Camera, CameraBase, CameraOpenError
from .component.detector import Detector, DetectorBase
from .component.drawer import Drawer
from .component.identifier import Identifier
from .utils.decorator import error_handler
from .utils.time_tracker import time_tracker

logger = logging.getLogger(__name__)


class BoostFace:
    """
    sub-threads:
        camera
    """

    def __init__(self):
        self._camera = CameraBase()
        self._detector = DetectorBase()
        self._identifier = Identifier()
        self._draw = Drawer()
        # self.wake_up()

    @error_handler
    @time_tracker.track_func
    def get_result(self) -> ImageFaces:
        """
        :exception CameraOpenError
        :return: Image
        """
        # FIXME: run it for while will crash the app
        success, frame = self._camera.videoCapture.read()
        if success:
            detected = self._detector.run_onnx(ImageFaces(image=frame, faces=[]))
            identified = self._identifier.identify(detected)
            draw_on = self._draw.show(identified)
            return draw_on
        else:
            error_msg = f"in {self._camera}.read()  self.videoCapture.read() get None"
            logger.error(f"camera._read with CameraOpenError{error_msg}")
            raise CameraOpenError(error_msg)

    # def wake_up(self):
    #     self._camera.wake_up()
    #     self._detector.wake_up()

    # def sleep(self):
    #     self._camera.sleep()
    #     self._detector.sleep()

    @error_handler
    def stop_app(self):
        # self._camera.stop()
        # self._detector.stop()
        self._identifier.stop_ws_client()


onnx_runner = BoostFace()
