# coding: utf-8

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    NavigationAvatarWidget,
    NavigationItemPosition,
    FluentWindow,
    SplashScreen)

from src.app.common.signal_bus import signalBus
from src.app.common.translator import Translator
from src.app.config.config import cfg
from src.app.view.interface import CloudMonitorInterface, HomeInterface, LocalMonitorInterface, SettingInterface
from .component.auth_dialog import create_login_dialog
from .resource import compiled_resources


# FIXME: move window lead to crash
class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        self.initWindow()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.local_console_interface = LocalMonitorInterface(self)
        self.settingInterface = SettingInterface(self)
        self.cloudInterface = CloudMonitorInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        # signalBus.switchToSampleCard.connect(self.switchToSample)
        # signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.navigationInterface.addSeparator()
        self.addSubInterface(
            self.cloudInterface,
            FIF.CLOUD,
            self.tr('Cloud Dev'))

        self.addSubInterface(
            self.local_console_interface,
            FIF.COMMAND_PROMPT,
            self.tr('Local Console'))

        # add login widget to bottom

        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=NavigationAvatarWidget(
                'zhiyiYo', ':/gallery/images/shoko.png'),
            onClick=self.login,  # FIXME: bug here click ,failed program
            position=NavigationItemPosition.BOTTOM
        )

        # setting interface
        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            self.tr('Settings'),
            NavigationItemPosition.BOTTOM)

    def initWindow(self):
        """
        Initialize the window,splash screen and FluentWindow
        """
        # set full screen size
        # desktop = QApplication.screens()[0].availableGeometry()
        # w, h = desktop.width(), desktop.height()
        w, h = 960, 780
        self.resize(w, h)
        self.setMinimumWidth(760)

        # set window icon and title
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('基于云计算+深度学习的高负荷多终端人脸识别微服务架构系统 桌面端')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106 * 2, 106 * 2))
        self.splashScreen.raise_()

        # move window to center
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()
    def login(self):
        self.login_dialog_c = create_login_dialog(self)
        self.login_dialog = self.login_dialog_c.view

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    # def switchToSample(self, routeKey, index):
    #     """ switch to sample """
    #     interfaces = self.findChildren(GalleryInterface)
    #     for w in interfaces:
    #         if w.objectName() == routeKey:
    #             self.stackedWidget.setCurrentWidget(w, False)
    #             w.scrollToCard(index)
