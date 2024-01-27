from PyQt6.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition

from src.app.common import signalBus
from src.app.utils.decorator import error_handler


class InforBarCreator:
    """ create info bar view"""

    def __init__(self, parent):
        self.main_window = parent

    def login_failed(self, content: str):
        """ login failed"""
        InfoBar.error(
            title='Login Failed',
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=-1,
            parent=self.main_window
        )

    @error_handler
    def login_successfully(self, content: str):
        """ login successfully"""
        InfoBar.success(
            title='Login Successfully',
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=2000,
            parent=self.main_window
        )


class InforBarCreaterC:
    """ create info bar controller"""

    def __init__(self, view: InforBarCreator):
        self.view = view
        self.auth_state_connect()

    @error_handler
    def auth_state_connect(self):
        signalBus.login_failed.connect(self.view.login_failed)
        signalBus.login_successfully.connect(self.view.login_successfully)


def create_info_bar(parent=None) -> InforBarCreaterC:
    """ create info bar """
    created_view = InforBarCreator(parent=parent)
    created_controller = InforBarCreaterC(created_view)

    return created_controller
