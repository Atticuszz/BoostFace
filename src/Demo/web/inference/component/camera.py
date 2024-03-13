"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 14/12/2023
@Description  :
"""

import logging

import cv2

from ..settings import CameraConfig, SourceConfig
from ..common import ImageFaces

logger = logging.getLogger(__name__)


class CameraOpenError(Exception):
    """
    CameraOpenError
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Camera:
    def __init__(self, config: CameraConfig):
        """
        for windows
        cmd 运行setx OPENCV_VIDEOIO_PRIORITY_MSMF 0后重启，可以加快摄像头打开的速度
        :param config: CameraOptions()
        """
        self.config = config
        logger.info(f"camera init with {config}")
        # self.videoCapture = cv2.VideoCapture(self.config.url.files())
        # print( self.config.url_type, SourceConfig.Webcam, self.config.url_type == SourceConfig.Webcam)
        # print( self.config.url_type, SourceConfig.video, self.config.url_type == SourceConfig.video)
        if config.url_type.value == SourceConfig.Webcam.value:
            # linux device
            self.videoCapture = cv2.VideoCapture(self.config.url, cv2.CAP_V4L2)
            self._prepare()
        elif config.url_type.value == SourceConfig.video.value:
            self.videoCapture = cv2.VideoCapture(self.config.url)
        else:
            # logger.info(f"not support {config.url_type}->{SourceConfig.video} yet")
            raise NotImplementedError(f"not support {config.url_type} yet")

        logger.info(f"camera init success, {self}")

    def read(self) -> ImageFaces:
        ret, frame = self.videoCapture.read()
        if ret is None or frame is None:
            error_msg = (
                f"in {self.videoCapture}.read()  self.videoCapture.read() get None"
            )
            logger.error(
                f"camera._read with CameraOpenError{error_msg} with config {self.config}"
            )
            raise CameraOpenError(error_msg)
        return ImageFaces(image=frame, faces=[])

    def _prepare(self):
        """
        for usb or ip camera, set fps and resolution, not necessary for mp4
        :return:
        """
        self.videoCapture.set(cv2.CAP_PROP_FPS, self.config.fps)
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
        real_resolution = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(
            self.videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )
        # 获取帧数
        real_fps = int(self.videoCapture.get(cv2.CAP_PROP_FPS))
        repr_string = (
            f"The video  codec  is {self.cap_codec_format}\n"
            f"camera params = {self.config}\n"
            f"real resolution = {real_resolution}\n"
            f"real fps = {real_fps}\n"
        )
        return repr_string
