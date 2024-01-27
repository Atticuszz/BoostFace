# coding=utf-8
import time
from PyQt6.QtCore import QThread

from src.app.common import signalBus
from src.app.config import qt_logger
from src.app.utils.decorator import error_handler
from src.app.view.component.console_log_widget import ConsoleLogWidget


class ConsoleSimulator(QThread):
    """
    A console output simulator
    Signal: newText
    """
    @error_handler
    def run(self):
        count = 0
        while True:
            time.sleep(1000)  # 控制输出速度
            count += 1
            qt_logger.info(f"Line {count}: The current count is {count}\n")

    def stop(self):
        self.quit()
        self.wait()


class LocalLogModel:
    """
    :var camera_info: dict, camera information
    :var console_simulator: ConsoleSimulator, a console output simulator
    """

    def __init__(self):
        self.console_simulator = ConsoleSimulator()
        self.camera_info = {
            'camera_name': 'Camera 1',
            'camera_type': 'USB',
            'camera_model': 'Logitech C920',
            'camera_resolution': '1920x1080',
            'camera_fps': '30',
            'camera_status': 'Connected',
        }


class LocalDevC:
    """
    connect console_append_text to update console log view
    """

    def __init__(self, model: LocalLogModel, view: ConsoleLogWidget):
        self.model = model
        self.view = view
        # self.view.close_event = self.model.console_simulator.stop
        # self.model.console_simulator.newText.connect(self.console_append_text)
        # receive log message from all sender in the bus
        signalBus.log_message.connect(self.view.append_text)
        # self.model.console_simulator.start()


def create_local_log(parent=None) -> LocalDevC:
    """
    create local log
    :param parent:
    """
    _model = LocalLogModel()
    _view = ConsoleLogWidget(parent)
    _controller = LocalDevC(_model, _view)
    return _controller
