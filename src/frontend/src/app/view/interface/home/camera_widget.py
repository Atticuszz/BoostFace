from dataclasses import asdict

from time import sleep

import cv2
from PyQt6.QtCore import Qt, QRectF, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QLinearGradient, QColor, QBrush, QImage
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import TogglePushButton
from qfluentwidgets import isDarkTheme, FluentIcon

from src.app.common import signalBus
from src.app.common.types import Image
from src.app.config import qt_logger
from src.app.config.config import HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from src.app.utils.boostface import BoostFace
from src.app.utils.boostface.common import ImageFaces, Face
from src.app.utils.boostface.component.camera import CameraOpenError
from src.app.utils.decorator import error_handler, calm_down
from src.app.utils.time_tracker import time_tracker
from src.app.view.component.link_card import LinkCardView

__all__ = ['create_camera_widget', 'create_state_widget']


class CameraModel(QThread):
    """ Camera model """
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.ai_camera: BoostFace | None = None  # lazy load ,load as start thread
        self._t_running = False
        self._c_sleeping = False
        self.img_size = (960, 540)
        self.default_pixmap = QPixmap(self.img_size[0], self.img_size[1])
        self.default_pixmap.fill(QColor(0, 0, 0, 0))

    def start_capture(self):
        """start capture thread"""

        # thread init
        if not self.isRunning():
            self._t_running = True
            self.start()
        else:
            self._wake_up()

    def stop_capture(self):
        """sleep capture"""
        # time_tracker.close()
        self._sleep()
        time_tracker.close()

    @error_handler
    def stop(self):
        self.stop_capture()
        if self.ai_camera:
            self.ai_camera.stop_app()
        self._t_running = False
        self.wait()
        qt_logger.debug("CameraModel stopped")

    @error_handler
    def run(self):
        self.ai_camera = BoostFace()

        while self._t_running:

            if self._c_sleeping:
                self.change_pixmap_signal.emit(self.default_pixmap.toImage())
                # qt_logger.debug("ai_camera is sleeping")
                sleep(1)
                continue

            with time_tracker.track("CameraModel.run"):

                with calm_down(0.03):
                    try:
                        # frame = self.capture.read()
                        res: ImageFaces = self.ai_camera.get_result()
                    except CameraOpenError:
                        print("camera open error or camera has released")
                        break
                    rgb_image = cv2.cvtColor(res.nd_arr, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    convert_to_Qt_format = QImage(
                        rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                    self.change_pixmap_signal.emit(convert_to_Qt_format)


    def _wake_up(self):
        self.ai_camera.wake_up()
        self._c_sleeping = False

    def _sleep(self):
        """sleeping thread"""
        self._c_sleeping = True
        if self.ai_camera:
            self.ai_camera.sleep()


class VideoStreamWidget(QWidget):
    """ Widget to display video stream from camera"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.img_size = (960, 540)
        self.default_pixmap = QPixmap(self.img_size[0], self.img_size[1])
        self.default_pixmap.fill(QColor(0, 0, 0, 0))
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.default_pixmap)

    @error_handler
    def update_image(self, image: QImage):
        """start camera to update image"""
        scaled_image = QPixmap.fromImage(image).scaled(
            self.img_size[0],
            self.img_size[1],
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_image)

    def reset_image(self):
        """reset image"""
        self.image_label.setPixmap(self.default_pixmap)


class CameraWidget(VideoStreamWidget):
    """
    camera_card
    |--- start button
    |---VideoStreamWidget

    add control components on video stream widget
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.layout = QVBoxLayout(self)
        # need to connect in controller
        self.toggle_switch = TogglePushButton(
            FIF.PLAY_SOLID, "start camera", self)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.toggle_switch)


# TODO: change to true camera state
class StateWidget(QWidget):
    """
    state_card
    |---background
    |---card CPU
    |---card RAM
    |---card Running time
    |---card connect to cloud
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(160)

        self.vBoxLayout = QVBoxLayout(self)

        # label
        self.galleryLabel = QLabel('BoostFace System', self)

        # banner image
        self.banner = QPixmap(':/gallery/images/header1.png')

        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(
            self.linkCardView, 1, Qt.AlignmentFlag.AlignBottom)
        self.vBoxLayout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.linkCardView.addCard(
            ':/gallery/images/logo.png',
            self.tr('Getting started'),
            self.tr('An overview of app development options and samples.'),
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub repo'),
            self.tr(
                'The latest fluent design controls and styles for your applications.'),
            REPO_URL
        )

        self.linkCardView.addCard(
            FluentIcon.CODE,
            self.tr('Code samples'),
            self.tr(
                'Find samples that demonstrate specific tasks, features and APIs.'),
            EXAMPLE_URL
        )

        self.linkCardView.addCard(
            FluentIcon.FEEDBACK,
            self.tr('Send feedback'),
            self.tr('Help us improve PyQt-Fluent-Widgets by providing feedback.'),
            FEEDBACK_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()

        # init linear gradient effect
        gradient = QLinearGradient(0, 0, 0, h)

        # draw background color
        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.fillPath(path, QBrush(gradient))

        # draw banner image
        pixmap = self.banner.scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))


class StateWidgetC:
    def __init__(self, view: StateWidget):
        self.view = view


class CameraWidgetC:
    def __init__(self, model: CameraModel, view: CameraWidget):
        self.model = model
        self.view = view

        # update image
        self.model.change_pixmap_signal.connect(
            self.view.update_image)
        # toggle camera
        self.view.toggle_switch.toggled.connect(self.toggle_camera)
        # bind close event
        signalBus.quit_all.connect(self.model.stop)

    @error_handler
    def toggle_camera(self, checked: bool):
        """
        toggle camera action
        """
        qt_logger.debug(f"toggle_camera {checked}")
        if checked:
            self.model.start_capture()
            # self.view.reset_image()
        else:
            self.model.stop_capture()


def create_camera_widget(parent=None) -> CameraWidgetC:
    """ create camera widget"""
    created_model = CameraModel()
    created_view = CameraWidget(parent=parent)
    created_controller = CameraWidgetC(created_model, created_view)

    return created_controller


def create_state_widget(parent=None) -> StateWidgetC:
    """ create state widget"""
    created_view = StateWidget(parent=parent)
    created_controller = StateWidgetC(created_view)

    return created_controller


if __name__ == '__main__':
    pass
