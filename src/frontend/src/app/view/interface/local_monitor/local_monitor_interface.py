from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import FluentIcon as FIF

from src.app.config.logging_config import QLoggingHandler
from src.app.view.component.expand_info_card import ExpandInfoCard
from src.app.view.interface.local_monitor.local_log_widget import create_local_log
from src.app.view.interface.local_monitor.local_sm_widget import create_local_system_monitor


class LocalMonitorInterface(QWidget):
    """ Local development interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('localDevInterface')
        # init layout
        self.main_layout = QHBoxLayout(self)
        self.bc_layout = QVBoxLayout()
        self.a_layout = QVBoxLayout()
        self.main_layout.addLayout(self.a_layout, 2)  # 加入主布局，比例为1
        self.main_layout.addLayout(self.bc_layout, 1)  # 加入主布局，比例为1

        # init widgets

        self._init_camera_card()
        self._init_resource_monitor()
        self._init_console_log()

        # add widgets to layout
        self.a_layout.addWidget(self.console_log)
        self.bc_layout.addWidget(self.camera_info_card, 1)
        self.bc_layout.addWidget(self.system_monitor, 2)

        # init window
        self.setWindowTitle('Local Development Interface')
        self.resize(1000, 800)

    def _init_camera_card(self):
        # B区域：摄像头信息，这里假设您的ExpandInfoCard已经创建好了
        self.camera_info_card = ExpandInfoCard(
            FIF.CAMERA,
            self.tr('Camera Info'),
            parent=self
        )
        self.camera_info_card.add_info(
            {
                'Device name': 'USB2.0 Camera',
                'Connection type': 'USB',
                'Image resolution': '1920x1080',
                'Capture FPS': '30',
            }
        )

    def _init_resource_monitor(self):
        self.system_monitor_c = create_local_system_monitor(parent=self)
        self.system_monitor = self.system_monitor_c.view

    def _init_console_log(self):
        """
        init console log
        :return:
        """
        self.console_log_c = create_local_log(parent=self)
        self.console_log = self.console_log_c.view


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    view = LocalMonitorInterface()
    logging_header_set_up = QLoggingHandler()
    view.show()
    sys.exit(app.exec())
