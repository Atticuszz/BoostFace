"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""
from collections import deque
from threading import Thread, Event

import cv2
from time import sleep

from src.app.config import cfg
from src.app.config import qt_logger
from src.app.config.config import CameraUrl, CameraConfig
from src.app.utils.decorator import error_handler, calm_down
from src.app.utils.time_tracker import time_tracker
from src.app.utils.boostface.common import ImageFaces, ThreadBase


class CameraOpenError(Exception):
    """
    CameraOpenError
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class CameraBase:
    """config for camera"""

    def __init__(self, config: CameraConfig = CameraConfig(
            fps=cfg.cameraFps.value, url=cfg.cameraDevice.value)):
        """
        cmd 运行setx OPENCV_VIDEOIO_PRIORITY_MSMF 0后重启，可以加快摄像头打开的速度
        :param config: CameraOptions()
        """
        self.config = config
        self.videoCapture = cv2.VideoCapture(self.config.url.value)
        if config.url != CameraUrl.video:
            self._prepare()
        qt_logger.debug(f"camera init success, {self}")

    def _prepare(self):
        """
        for usb or ip camera, set fps and resolution, not necessary for mp4
        :return:
        """
        #  设置帧数
        self.videoCapture.set(cv2.CAP_PROP_FPS, self.config.fps)
        # 设置分辨率
        self.videoCapture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.config.resolution[0])
        self.videoCapture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.config.resolution[1])

        # 设置视频编解码格式 note: 务必在set分辨率之后设置，否则不知道为什么又会回到默认的YUY2
        self.videoCapture.set(
            cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc("M", "J", "P", "G")
        )

    @property
    def cap_codec_format(self):
        """
        get current video codec format
        :return:
        """
        # 获取当前的视频编解码器
        fourcc = self.videoCapture.get(cv2.CAP_PROP_FOURCC)
        # 因为FOURCC编码是一个32位的值，我们需要将它转换为字符来理解它
        # 将整数编码值转换为FOURCC编码的字符串表示形式
        codec_format = "".join(
            [chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
        return codec_format

    def __repr__(self):
        """
        print camera info
        """
        self.real_resolution = int(
            self.videoCapture.get(
                cv2.CAP_PROP_FRAME_WIDTH)), int(
            self.videoCapture.get(
                cv2.CAP_PROP_FRAME_HEIGHT))
        # 获取帧数
        self.real_fps = int(self.videoCapture.get(cv2.CAP_PROP_FPS))
        repr_string = (f"The video  codec  is {self.cap_codec_format}\n"
                       f"camera params = {self.config}")
        return repr_string


class Camera(ThreadBase):
    """Camera component"""

    def __init__(self):
        super().__init__()
        self._camera_base = CameraBase()
        self._camera = self._camera_base.videoCapture
        super().start()

    @error_handler
    def run(self):
        while self._is_running.is_set():
            with time_tracker.track("camera.run"):
                try:
                    with calm_down(0.03):
                        self._is_sleeping.wait()
                        img = self._read()
                        self._result_queue.append(img)
                except CameraOpenError:
                    break

    def stop(self):
        super().stop()
        self._camera.release()
        self.join()
        qt_logger.debug("camera stopped")

    @time_tracker.track_func
    def _read(self) -> ImageFaces:
        """
        read a Image from url by opencv.VideoCapture.read()
        :exception CameraOpenError
        :return: ImageFaces
        """

        ret, frame = self._camera.read()
        if ret is None or frame is None:
            error_msg = f"in {self}.read()  self.videoCapture.read() get None"
            qt_logger.error(f"camera._read with CameraOpenError{error_msg}")
            raise CameraOpenError(error_msg)
        return ImageFaces(image=frame, faces=[])



if __name__ == "__main__":
    camera = Camera()
    i = 0
    while i < 1000:
        img = camera.produce()
        if cv2.waitKey(1) == 27:
            break
        i += 1
    camera.stop()
    cv2.destroyAllWindows()
    time_tracker.close()
