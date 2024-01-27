import psutil
from PyQt6.QtCore import QTimer

from src.app.utils.decorator import error_handler
from src.app.view.component.system_monitor import SystemMonitor

__all__ = ['create_local_system_monitor']


class LocalSystemStats:
    """ Local system stats"""

    def __init__(self):
        self.last_net_io = psutil.net_io_counters()

    def get_cpu_usage(self):
        return psutil.cpu_percent()

    def get_ram_usage(self):
        return psutil.virtual_memory().percent

    def get_network_throughput(self):
        net_io = psutil.net_io_counters()
        net_send = net_io.bytes_sent - self.last_net_io.bytes_sent
        net_recv = net_io.bytes_recv - self.last_net_io.bytes_recv
        self.last_net_io = net_io
        return net_send + net_recv


class LocalSystemMonitorC:
    """ Controller for local system monitor"""

    def __init__(self, view: SystemMonitor, model: LocalSystemStats):
        self.view = view
        self.model = model
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_stats)
        self.timer.start(1000)
        self.view.close_event = self.timer.stop

    @error_handler
    def update_system_stats(self):
        """update local system stats"""
        cpu_percent = self.model.get_cpu_usage()
        ram_percent = self.model.get_ram_usage()
        net_throughput = self.model.get_network_throughput()
        self.view.update_stats(cpu_percent, ram_percent, net_throughput)


def create_local_system_monitor(parent=None) -> LocalSystemMonitorC:
    """create local system monitor"""
    created_model = LocalSystemStats()
    created_view = SystemMonitor(parent=parent)
    created_controller = LocalSystemMonitorC(created_view, created_model)

    return created_controller
