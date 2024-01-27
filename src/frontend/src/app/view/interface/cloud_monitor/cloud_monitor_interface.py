from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import FluentIcon as FIF

from .cloud_log_widget import create_cloud_log
from .cloud_sm_widget import create_cloud_system_monitor
from ...component.expand_info_card import ExpandInfoCard


class CloudMonitorInterface(QWidget):
    """ Cloud development interface
    widgets:
        A: console log
        B: cloud server info expand card
        C: system monitor
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('CloudDevInterface')
        # init layout
        self.main_layout = QHBoxLayout(self)
        self.bc_layout = QVBoxLayout()
        self.a_layout = QVBoxLayout()
        self.main_layout.addLayout(self.a_layout, 2)
        self.main_layout.addLayout(self.bc_layout, 1)

        # init widgets

        self._init_camera_card()
        self._init_resource_monitor()
        self._init_console_log()

        # add widgets to layout
        self.a_layout.addWidget(self.console_log)
        self.bc_layout.addWidget(self.cloud_info_card, 1)
        self.bc_layout.addWidget(self.resource_monitor, 2)

        # init window
        self.setWindowTitle('Local Development Interface')
        self.resize(1000, 800)

    def _init_camera_card(self):
        # B区域：摄像头信息，这里假设您的ExpandInfoCard已经创建好了
        self.cloud_info_card = ExpandInfoCard(
            FIF.GLOBE,
            self.tr('Cloud Server Info'),
            parent=self
        )
        self.cloud_info_card.add_info({
            'domain': "www.digitalocean.com",
            'location': 'New York',
            'OS': 'Ubuntu 20.04',
            'CPU': '4 vCPU',
            'RAM': '8 GB',
            'GPU': 'NVIDIA RTX 3080',
            'Storage': '1 TB',
        })

    def _init_resource_monitor(self):
        self.sys_monitor_c = create_cloud_system_monitor(parent=self)
        self.resource_monitor = self.sys_monitor_c.view

    def _init_console_log(self):
        """
        init console log
        :return:
        """
        # A区域：控制台日志输出
        self.console_log_c = create_cloud_log(parent=self)
        self.console_log = self.console_log_c.view


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    win = CloudMonitorInterface()
    win.show()
    app.exec()
