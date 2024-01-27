import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
# 主窗口，用于展示 ExpandSettingCard
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtWidgets import QGridLayout
from qfluentwidgets import ExpandGroupSettingCard
from qfluentwidgets import FluentIcon as FIF


class KeyValueWidget(QWidget):
    def __init__(self, data_dict, parent=None):
        super().__init__(parent=parent)
        self.layout = QGridLayout(self)

        # 设置固定的间距和列宽
        key_padding = 20  # key的左边距
        space_between = 10  # key和value之间的距离

        for row, (key, value) in enumerate(data_dict.items()):
            # 创建键标签
            key_label = QLabel(f"{key}:")
            key_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            key_label.setFixedWidth(key_label.fontMetrics().boundingRect(key_label.text()).width() + key_padding)

            # 创建值标签
            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # 为浅色和深色主题设置不同的颜色
            palette = value_label.palette()
            palette.setColor(QPalette.ColorRole.WindowText, QColor('#6c757d'))  # 浅黑色
            value_label.setPalette(palette)

            # 将键和值标签添加到网格布局中
            self.layout.addWidget(key_label, row, 0)
            self.layout.addWidget(value_label, row, 1)
            self.layout.setSpacing(space_between)  # 设置行间距

        # 设置布局的列间距
        self.layout.setColumnMinimumWidth(0, key_padding)
        self.layout.setColumnMinimumWidth(1, space_between)

        # 设置整体布局的边距为0
        self.layout.setContentsMargins(key_padding, 0, key_padding, 0)


# 假设的主窗口类
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建 ExpandGroupSettingCard 实例
        self.expand_group_card = ExpandGroupSettingCard(icon=FIF.SETTING, title="Device Info", parent=self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.expand_group_card)

        # 示例数据
        device_info = {
            "Device name": "Atticus-Zhou",
            "Processor": "AMD Ryzen 7 5700U with Radeon Graphics",
            "Installed RAM": "16.0 GB (15.3 GB usable)",
            "Device ID": "AFE29FB7-1431-4669-843C-D863AED27529",
            "Product ID": "00330-80000-00000-AA521",
            "System type": "64-bit operating system, x64-based processor",
            "Pen and touch": "No pen or touch input is available for this display"
        }

        # 添加信息到卡片
        # 在主窗口中
        self.key_value_widget = KeyValueWidget(device_info)
        self.expand_group_card.addGroupWidget(self.key_value_widget)
        self.expand_group_card.adjustSize()
        self.expand_group_card.setExpand(True)
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Expandable Group Setting Card')


# 运行应用
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
