import sys
import time

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import FluentIcon as FIF, TextEdit

from src.app.utils.decorator import error_handler
from src.app.view.component.expand_info_card import ExpandInfoCard
from src.app.view.component.system_monitor import SystemMonitor


class ConsoleSimulator(QThread):
    newText = pyqtSignal(str)
    @error_handler
    def run(self):
        count = 0
        while True:
            time.sleep(1)  # 控制输出速度
            count += 1
            self.newText.emit(f"Line {count}: The current count is {count}\n")


class LocalDevInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

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

        self.bc_layout.addWidget(self.camera_info_card, 1)
        self.bc_layout.addWidget(self.resource_monitor, 2)

        # init window
        self.setWindowTitle('Local Development Interface')
        self.resize(1000, 800)

    def _init_camera_card(self):
        # B区域：摄像头信息，这里假设您的ExpandInfoCard已经创建好了
        self.camera_info_card = ExpandInfoCard(
            FIF.CAMERA,
            self.tr('Camera information'),
            parent=self
        )
        self.camera_info_card.add_info(
            {
                'Camera name': 'USB2.0 Camera',
                'Camera type': 'USB',
                'Camera resolution': '1920x1080',
                'Camera FPS': '30',
            }
        )

    def _init_resource_monitor(self):
        # C区域：资源监测图表
        self.resource_monitor = SystemMonitor(self)

    def _init_console_log(self):
        """
        init console log
        :return:
        """
        # A区域：控制台日志输出
        self.console_log = TextEdit()
        self.console_log.setReadOnly(True)
        self.a_layout.addWidget(self.console_log, 2)
        self.console_simulator = ConsoleSimulator(self)
        self.console_simulator.newText.connect(self.append_text)
        self.console_simulator.start()

    def append_text(self, text):
        """
        listen to the newText signal and append the text to the text edit
        :param text:
        :return:
        """
        cursor = self.console_log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.console_log.setTextCursor(cursor)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LocalDevInterface()
    window.show()
    sys.exit(app.exec())
