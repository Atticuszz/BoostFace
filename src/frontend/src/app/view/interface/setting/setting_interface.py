# coding:utf-8
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel
from qfluentwidgets import InfoBar
from qfluentwidgets import (
    ScrollArea,
    ExpandLayout)

from src.app.config.config import cfg, isWin11
from src.app.view.interface.setting.about_settings import create_about_setting_group
from src.app.view.interface.setting.camera_settings import create_camera_setting_group
from src.app.view.interface.setting.personalization_settings import create_personalization_setting_group
from src.app.view.style_sheet import StyleSheet


class SettingInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # # Camera settings
        self.cameraGroup_c = create_camera_setting_group(self.scrollWidget)
        self.cameraGroup = self.cameraGroup_c.view

        # personalization
        self.personalGroup_c = create_personalization_setting_group(
            self.scrollWidget)
        self.personalGroup = self.personalGroup_c.view

        # application
        self.aboutGroup_c = create_about_setting_group(self.scrollWidget)
        self.aboutGroup = self.aboutGroup_c.view

        self._initWidget()
        self._initLayout()
        cfg.appRestartSig.connect(self._showRestartTooltip)

    def _initWidget(self):
        # init window
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.personalGroup.micaCard.setEnabled(isWin11())

        # initialize layout
        self._initLayout()

    def _initLayout(self):
        self.settingLabel.move(36, 30)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)

        # 1. set into layout
        self.expandLayout.addWidget(self.cameraGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def _showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('Updated successfully'),
            self.tr('Configuration takes effect after restart'),
            duration=1500,
            parent=self
        )


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    from src.app.config.logging_config import QLoggingHandler

    app = QApplication(sys.argv)
    view = SettingInterface()
    logging_header_set_up = QLoggingHandler()
    view.show()
    sys.exit(app.exec())
