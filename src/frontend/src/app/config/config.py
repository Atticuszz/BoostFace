# coding:utf-8
from enum import Enum
from typing import NamedTuple

import sys
from PyQt6.QtCore import QLocale
from qfluentwidgets import (
    qconfig,
    QConfig,
    ConfigItem,
    OptionsConfigItem,
    BoolValidator,
    OptionsValidator,
    RangeConfigItem,
    RangeValidator,
    Theme,
    ConfigSerializer,
    __version__)


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(
        QLocale.Language.Chinese,
        QLocale.Country.China)
    CHINESE_TRADITIONAL = QLocale(
        QLocale.Language.Chinese,
        QLocale.Country.HongKong)
    ENGLISH = QLocale(QLocale.Language.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class CameraUrl(Enum):
    """
    url configs for camera
    """
    laptop: int = 0
    usb: int = 1
    ip: str = "http://"
    video: str = r"C:\Users\18317\python\BoostFace_pyqt6\tests\video\friends.mp4"


class CameraConfig(NamedTuple):
    """
    config for Camera
    """
    fps: int = 30
    resolution: tuple[int, ...] = (1920, 1080)
    url: CameraUrl = CameraUrl.video


class Config(QConfig):
    """ Config of application """
    # camera

    cameraFps = OptionsConfigItem("Camera", "Fps", 30, OptionsValidator(
        [10, 15, 20, 25, 30, "default"]), restart=True)
    cameraDevice = OptionsConfigItem("Camera",
                                     "Device",
                                     CameraUrl.video,
                                     OptionsValidator([CameraUrl.laptop,
                                                       CameraUrl.usb,
                                                       CameraUrl.video,
                                                       "default"]),
                                     restart=True)
    cameraResolution = OptionsConfigItem("Camera", "Resolution", (1920, 1080), OptionsValidator([
        (1920, 1080), (1280, 720), "default"]), restart=True)

    # main window
    micaEnabled = ConfigItem(
        "MainWindow",
        "MicaEnabled",
        isWin11(),
        BoolValidator())
    dpiScale = OptionsConfigItem("MainWindow", "DpiScale", "Auto", OptionsValidator(
        [1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow",
        "Language",
        Language.AUTO,
        OptionsValidator(Language),
        LanguageSerializer(),
        restart=True)

    # Material
    blurRadius = RangeConfigItem(
        "Material",
        "AcrylicBlurRadius",
        15,
        RangeValidator(
            0,
            40))

    # software update
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator())


YEAR = 2023
AUTHOR = "Atticus-Zhou"
VERSION = __version__
HELP_URL = "https://qfluentwidgets.com"
REPO_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"
EXAMPLE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/PyQt6/examples"
FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"
SUPPORT_URL = "https://afdian.net/a/zhiyiYo"


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('app/config/config.json', cfg)
