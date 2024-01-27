# coding=utf-8
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup, OptionsSettingCard

from src.app.config.config import cfg
from src.app.utils.decorator import error_handler


class CameraSettingM:
    """ Camera setting model"""

    def __init__(self):
        self.camera_fps = cfg.cameraFps
        self.camera_fps_options_texts = [
            '10', '15', '20', '25', '30'
        ]

        self.camera_device = cfg.cameraDevice
        self.camera_device_options_texts = [
            'laptop camera', 'external camera', 'video'
        ]

        self.camera_resolution = cfg.cameraResolution
        self.camera_resolution_options_texts = [
            '1920x1080', '1280x720'
        ]


class CameraSettingGroup(SettingCardGroup):
    """ Camera setting group"""

    def __init__(self, model: CameraSettingM, parent=None):
        super().__init__(title='Camera', parent=parent)
        self.model = model
        self.cameraFpsCard = OptionsSettingCard(
            self.model.camera_fps,
            FIF.SPEED_HIGH,
            self.tr('Camera FPS'),
            self.tr('Set the FPS of the camera'),
            texts=self.model.camera_fps_options_texts,
            parent=self
        )
        self.cameraDeviceCard = OptionsSettingCard(
            self.model.camera_device,
            FIF.CAMERA,
            self.tr('Camera device'),
            self.tr('Set the camera device'),
            texts=self.model.camera_device_options_texts,
            parent=self
        )
        self.cameraResolutionCard = OptionsSettingCard(
            self.model.camera_resolution,
            FIF.PHOTO,
            self.tr('Camera resolution'),
            self.tr('Set the resolution of the camera'),
            texts=self.model.camera_resolution_options_texts,
            parent=self
        )
        self.addSettingCard(self.cameraFpsCard)
        self.addSettingCard(self.cameraDeviceCard)
        self.addSettingCard(self.cameraResolutionCard)

# FIXME: invalid setting change
class CameraSettingC:
    """ Camera setting controller"""

    def __init__(self, model: CameraSettingM, view: CameraSettingGroup):
        self.model = model
        self.view = view
        self._init_signal_binding()

    def _init_signal_binding(self):
        self.view.cameraFpsCard.optionChanged.connect(self._update_camera_fps)
        self.view.cameraDeviceCard.optionChanged.connect(
            self._update_camera_device)
        self.view.cameraResolutionCard.optionChanged.connect(
            self._update_camera_resolution)

    def _update_camera_fps(self, value: str):
        self.model.camera_fps = value

    def _update_camera_device(self, value: str):
        self.model.camera_device = value

    def _update_camera_resolution(self, value: str):
        self.model.camera_resolution = value


def create_camera_setting_group(parent=None) -> CameraSettingC:
    """ create camera setting"""
    created_model = CameraSettingM()
    created_view = CameraSettingGroup(created_model, parent=parent)
    created_controller = CameraSettingC(created_model, created_view)

    return created_controller
