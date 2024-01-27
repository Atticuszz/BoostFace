# coding:utf-8
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from src.app.view.interface.home.camera_widget import (
    create_camera_widget,
    create_state_widget)


class HomeInterface(QWidget):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('homeInterface')
        self._init_layout()

    def _init_layout(self):
        """
        init layout
        """
        self.main_layout = QVBoxLayout(self)  # 主布局

        self.camera_widget_C = create_camera_widget(self)
        self.camera_widget = self.camera_widget_C.view
        self.state_widget_C = create_state_widget(self)
        self.state_widget = self.state_widget_C.view

        self.main_layout.addWidget(self.state_widget)
        self.main_layout.addWidget(self.camera_widget)





if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    home = HomeInterface()
    home.show()
    app.exec()
