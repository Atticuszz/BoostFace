# coding: utf-8
from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ pyqtSignal bus """

    switchToSampleCard = pyqtSignal(str, int)
    micaEnableChanged = pyqtSignal(bool)
    supportSignal = pyqtSignal()
    login_failed = pyqtSignal(str)
    login_successfully = pyqtSignal(str)
    is_identify_running = pyqtSignal(bool)
    identify_results = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    quit_all = pyqtSignal()  # call close event of all sub-threads

signalBus = SignalBus()
