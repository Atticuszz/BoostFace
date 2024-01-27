# coding=utf-8
"""
Auth dialog
"""
import re

from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, PasswordLineEdit

from src.app.common import signalBus
from src.app.common.client import client

__all__ = ['create_login_dialog']

from src.app.utils.decorator import error_handler


class AuthDialog(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget.setMinimumWidth(350)
        self.titleLabel = SubtitleLabel('Log in', self)

        # account line edit
        self.email_line_edit = LineEdit(self)
        self.email_line_edit.setPlaceholderText('Enter your account id')
        self.email_line_edit.setClearButtonEnabled(True)

        # password line edit
        self.password_line_edit = PasswordLineEdit(self)
        self.password_line_edit.setPlaceholderText(
            self.tr("Enter you password"))

        # button
        # check the password format and verify in the cloud
        self.yesButton.setText('Login')
        self.cancelButton.setText('Cancel')

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.email_line_edit)
        self.viewLayout.addWidget(self.password_line_edit)

        # self.account_line_edit.textChanged.connect(self._validateUrl)

    # def _validateUrl(self, text):
    #     self.yesButton.setEnabled(QUrl(text).isValid())


class AuthDialogM:
    def __init__(self):
        self.email: str = ''
        self.password: str = ''

    def login(self) -> bool:
        """
        login in with client
        """
        if client.login(self.email, self.password):
            return True
        else:
            return False

    def set_email(self, text: str):

        self.email = text

    def set_password(self, text: str):
        self.password = text

    def validate_email(self) -> bool:
        """email format validation"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, self.email) is not None

    def validate_password(self) -> bool:
        """
        Must have one uppercase letter, one lowercase letter, one number, and one symbol
        At least 8, at most 16 characters
        """
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#@!$%^&*])[A-Za-z\d#@!$%^&*]{8,16}$"
        return re.match(pattern, self.password) is not None


class AuthDialogC:
    def __init__(self, model: AuthDialogM, view: AuthDialog):
        self.model = model
        self.view = view

        # connect
        self.view.password_line_edit.textChanged.connect(
            self.model.set_password)
        self.view.email_line_edit.textChanged.connect(self.model.set_email)
        self.view.yesButton.clicked.connect(self.login)

    @error_handler
    def login(self):
        if not self.model.validate_email():
            signalBus.login_failed.emit("your email is invalid!")
        elif not self.model.validate_password():
            signalBus.login_failed.emit(
                "your password must have one uppercase letter,\
                                         one lowercase letter, one number, and one symbol At least 8, at most 16 characters ")
        elif not self.model.login():
            signalBus.login_failed.emit("login failed!")
        else:
            signalBus.login_successfully.emit("login successfully!")


def create_login_dialog(parent=None) -> AuthDialogC:
    """create login dialog"""
    w = AuthDialog(parent)
    model = AuthDialogM()
    controller = AuthDialogC(model, w)
    return controller
