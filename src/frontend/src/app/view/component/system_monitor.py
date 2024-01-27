"""
System Monitor Widget
"""

import pyqtgraph as pg
from PyQt6.QtGui import QLinearGradient, QColor, QPainter, QBrush
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import Theme

from src.app.config.config import cfg
from src.app.utils.decorator import error_handler


class ResourceGraph(pg.PlotWidget):
    """Resource Graph Widget"""

    def __init__(self, title: str, unit: str,
                 color: tuple[int, int, int] = (0, 0, 255), parent=None):
        super().__init__(parent=parent)
        if cfg.themeMode.value != Theme.DARK and cfg.themeMode.value != Theme.AUTO:
            self.setBackground('w')
        pg.setConfigOptions(antialias=True)

        # Create the gradient
        self.gradient = QLinearGradient(0, 1, 0, 0)
        self.gradient.setColorAt(1.0, QColor(
            *color, 0))  # Change the color here
        self.gradient.setColorAt(0.0, QColor(
            *color, 150))  # Change the color here
        self.gradient.setCoordinateMode(
            QLinearGradient.CoordinateMode.ObjectBoundingMode)

        self.brush = QBrush(self.gradient)

        self.data = [0] * 100
        self.curve = self.plot(pen=pg.mkPen(QColor(*color), width=2)
                               )  # Change pen color here
        self.curve.setBrush(QBrush(self.gradient))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set title and axis labels
        # Set title and axis labels
        self.setTitle(title)
        self.getAxis('left').setLabel('Usage', units=unit)  # 使用传递的单位

    def update_data(self, new_data):
        self.data[:-1] = self.data[1:]
        self.data[-1] = new_data
        self.curve.setData(self.data, fillLevel=0, brush=self.brush)


class SystemMonitor(QWidget):
    """System Monitor Widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        # init graphs
        self.cpu_graph = ResourceGraph("CPU Usage", "%", (255, 0, 0))
        self.ram_graph = ResourceGraph("RAM Usage", "%", (0, 255, 0))
        self.net_graph = ResourceGraph(
            "Network Throughput", "Bytes/s", (0, 0, 255))

        # add graphs to layout
        self.layout.addWidget(self.cpu_graph)
        self.layout.addWidget(self.ram_graph)
        self.layout.addWidget(self.net_graph)
        # self.close_event: Callable[[], None] | None = None
        # signalBus.quit_all.connect(self.closeEvent)
    @error_handler
    def update_stats(
            self,
            cpu_percent: float,
            ram_percent: float,
            net_throughput: float):
        """updatte cpu, ram, and network usage"""
        self.cpu_graph.update_data(cpu_percent)
        self.ram_graph.update_data(ram_percent)
        self.net_graph.update_data(net_throughput)

    # def closeEvent(self, event) -> None:
    #     if self.close_event:
    #         self.close_event()
    #
    #     qt_logger.debug("close cloud system monitor sub sub thread")
    #     super().closeEvent(event)
