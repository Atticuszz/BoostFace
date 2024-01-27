# coding=utf-8
from src.app.common import signalBus
from src.app.common.client.web_socket import WebSocketClient
from src.app.config import qt_logger
from src.app.utils.decorator import error_handler
from src.app.view.component.system_monitor import SystemMonitor

__all__ = ['create_cloud_system_monitor']


from PyQt6.QtCore import QTimer


class CloudSystemStats:
    """
    Remote system stats
    """

    def __init__(self, ws_type="cloud_system_monitor"):
        self.ws_client = WebSocketClient(ws_type)
        self.cpu_percent = 0
        self.ram_percent = 0
        self.net_throughput = 0
        self.ws_client.start_ws()

    def update_stats(self):
        """This method will be called by a timer from the controller"""
        data = self.ws_client.receive()
        if data is None:
            return
        if isinstance(data, dict):
            self.process_data(data)
        else:
            raise TypeError(f"cloud system monitor data type error:{data}")

    def process_data(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError("data must be dict")
        self.cpu_percent = float(data.get('cpu_percent', 0))
        self.ram_percent = float(data.get('ram_percent', 0))
        self.net_throughput = float(data.get('net_throughput', 0))

    def stop_ws(self):
        self.ws_client.stop_ws()
        qt_logger.debug("CloudSystemStats stopped")


class CloudSystemMonitorC:
    """
    Controller for remote system monitor
    """

    def __init__(self, view: SystemMonitor, model: CloudSystemStats):
        self.view = view
        self.model = model
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_stats)
        self.timer.start(1000)  # Update every second
        signalBus.quit_all.connect(self.stop)

    @error_handler
    def update_system_stats(self):
        """ Fetch new data from the model and update the view. """
        self.model.update_stats()  # Ask the model to fetch new data
        # Update the view with new data
        self.view.update_stats(
            self.model.cpu_percent,
            self.model.ram_percent,
            self.model.net_throughput
        )

    def stop(self):
        self.model.stop_ws()
        self.timer.stop()


def create_cloud_system_monitor(parent=None) -> CloudSystemMonitorC:
    """ Factory function to create the monitor components. """
    model = CloudSystemStats()
    # Assume SystemMonitor is a QWidget or similar
    view = SystemMonitor(parent=parent)
    controller = CloudSystemMonitorC(view, model)
    return controller
