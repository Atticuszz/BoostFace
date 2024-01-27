"""
安装前提 ： libjpeg-turbo-gcc64
"""
import random
from collections import deque
from timeit import default_timer as current_time

import cv2

from numpy import ndarray

from src.app.common.types import Color, Image, Bbox
from src.app.config import qt_logger
from src.app.utils.boostface.common import ImageFaces
from src.app.utils.time_tracker import time_tracker


class Drawer:
    def __init__(self):
        self._interval_time_sum_cnt = 0
        self._frame_cnt = 0
        self.image_size = None
        self._interval_time = deque(maxlen=2)
        self._interval = deque(maxlen=200)
        self._temp_sum = 0
        self.ave_fps = 0
        self._pre = 0
        self._cur = 0
        self._colors: list[Color] = [(200, 150, 255), (255, 255, 153), (
            144, 238, 144), (173, 216, 230), (255, 182, 193), (255, 165, 0)]
    @time_tracker.track_func
    def show(self, image2show: ImageFaces) -> ImageFaces:
        self._frame_cnt += 1
        if self._frame_cnt > 10000:
            self._frame_cnt = 0
        image2show_nd_arr = self._draw_on(image2show)
        res = self._draw_fps(image2show_nd_arr)
        image2show.nd_arr = res
        # cv2.imshow('screen', image2show_nd_arr)
        return image2show

    def _draw_bbox(self, dimg: Image, bbox: Bbox, bbox_color: Color):
        """
        only draw the bbox beside the corner,and the corner is round
        :param dimg: img to draw bbox on
        :param bbox: face bboxes
        """
        # 定义矩形的四个角的坐标
        pt1 = (bbox[0], bbox[1])
        pt2 = (bbox[2], bbox[3])
        bbox_thickness = 4
        # 定义直角附近线段的长度
        line_len = int(0.08 * (pt2[0] - pt1[0]) + 0.06 * (pt2[1] - pt1[1]))

        def draw_line(_pt1, _pt2):
            cv2.line(dimg, _pt1, _pt2, bbox_color, bbox_thickness)

        draw_line((pt1[0], pt1[1]), (pt1[0] + line_len, pt1[1]))
        draw_line((pt1[0], pt1[1]), (pt1[0], pt1[1] + line_len))
        draw_line((pt2[0], pt1[1]), (pt2[0] - line_len, pt1[1]))
        draw_line((pt2[0], pt1[1]), (pt2[0], pt1[1] + line_len))
        draw_line((pt1[0], pt2[1]), (pt1[0] + line_len, pt2[1]))
        draw_line((pt1[0], pt2[1]), (pt1[0], pt2[1] - line_len))
        draw_line((pt2[0], pt2[1]), (pt2[0] - line_len, pt2[1]))
        draw_line((pt2[0], pt2[1]), (pt2[0], pt2[1] - line_len))

    def _draw_text(self, dimg, box, name, color):
        # 文字信息显示
        self.font_scale = 3
        # 设置文本的位置，将文本放在人脸框的下方
        text_position = (box[0], box[3] + 22)
        # ft2 = cv2.freetype.createFreeType2()
        # ft2.loadFontData(fontFileName='simhei.ttf', id=0)
        # ft2.putText(img=dimg,
        #             text=name,
        #             org=text_position,
        #             fontHeight=20,
        #             color=color,
        #             thickness=-1,
        #             line_type=cv2.LINE_AA,
        #             bottomLeftOrigin=True)
        # 添加文本  中文问题还没有解决
        cv2.putText(img=dimg,
                    text=name,
                    org=text_position,
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=self.font_scale,
                    color=color,
                    thickness=3,
                    lineType=cv2.LINE_AA)

    def _draw_fps(self, image2draw_fps: ndarray):
        """
        取最近200次的时间间隔，计算平均fps，从而稳定FPS显示
        Args:
            image2draw_fps: image to draw FPS
        Returns: None
        """
        if self._pre == 0:
            self._pre = current_time()
        elif self._cur == 0:
            self._cur = current_time()
        else:
            self._pre = self._cur
            self._cur = current_time()
            interval = self._cur - self._pre
            if self._interval.__len__() < 200:
                self._temp_sum += interval
            elif self._interval.__len__() == 200:
                self._temp_sum += interval
                self._temp_sum -= self._interval.popleft()
            self._interval.append(interval)
            self.ave_fps = 1 / self._temp_sum * self._interval.__len__()
            cv2.putText(
                image2draw_fps,
                f"FPS = {self.ave_fps :.2f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
        return image2draw_fps

    def _draw_on(self, image2draw_on: ImageFaces):
        dimg = image2draw_on.nd_arr
        qt_logger.debug(f"drawer draw {len(image2draw_on.faces)} faces")
        for face in image2draw_on.faces:
            # face=[bbox, kps, det_score, color, match_info]

            bbox = face.bbox.astype(int)
            if face.match_info.uid:
                bbox_color = (0, 0, 255)
                text_color = (0, 0, 255)
            else:
                bbox_color = random.choice(self._colors)
                text_color = random.choice(self._colors)
            name = face.match_info.name
            # 黄色闪烁
            self._draw_bbox(dimg, bbox, bbox_color)
            # text show
            self._draw_text(dimg, bbox, name, text_color)
        return dimg
