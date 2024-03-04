"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""

import logging

import cv2

from ...setttings import CameraConfig, SourceConfig
from ..common import ImageFaces, ThreadBase
from ..utils.decorator import calm_down, error_handler
from ..utils.time_tracker import time_tracker

logger = logging.getLogger(__name__)


class CameraOpenError(Exception):
    """
    CameraOpenError
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Camera:
    """config for camera"""

    def __init__(self, config=CameraConfig()):
        """
        cmd 运行setx OPENCV_VIDEOIO_PRIORITY_MSMF 0后重启，可以加快摄像头打开的速度
        :param config: CameraOptions()
        """
        self.config = config
        logger.debug(f"camera init with {config}")
        self.videoCapture = cv2.VideoCapture(self.config.url.files()[1].as_posix())
        # self.videoCapture = cv2.VideoCapture(self.config.url.files())
        if config.url != SourceConfig.video:
            self._prepare()
        logger.debug(f"camera init success, {self}")

    def read(self) -> ImageFaces:
        ret, frame = self.videoCapture.read()
        if ret is None or frame is None:
            error_msg = (
                f"in {self.videoCapture}.read()  self.videoCapture.read() get None"
            )
            logger.error(f"camera._read with CameraOpenError{error_msg}")
            raise CameraOpenError(error_msg)
        return ImageFaces(image=frame, faces=[])

    def _prepare(self):
        """
        for usb or ip camera, set fps and resolution, not necessary for mp4
        :return:
        """
        #  设置帧数
        self.videoCapture.set(cv2.CAP_PROP_FPS, self.config.fps)
        # 设置分辨率
        self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.resolution[0])
        self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.resolution[1])

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
        codec_format = "".join([chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
        return codec_format

    def __repr__(self):
        """
        print camera info
        """
        self.real_resolution = int(
            self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
        ), int(self.videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 获取帧数
        self.real_fps = int(self.videoCapture.get(cv2.CAP_PROP_FPS))
        repr_string = (
            f"The video  codec  is {self.cap_codec_format}\n"
            f"camera params = {self.config}"
        )
        return repr_string
