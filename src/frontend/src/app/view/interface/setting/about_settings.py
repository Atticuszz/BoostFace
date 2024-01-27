# coding=utf-8
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from qfluentwidgets import SettingCardGroup, HyperlinkCard, PrimaryPushSettingCard, FluentIcon as FIF

from src.app.config.config import HELP_URL, FEEDBACK_URL, YEAR, AUTHOR, VERSION


class AboutSettingsM:
    """ About setting model"""

    def __init__(self):
        self.help_url = HELP_URL
        self.feedback_url = FEEDBACK_URL
        self.year = YEAR
        self.author = AUTHOR
        self.version = VERSION


class AboutSettingsGroup(SettingCardGroup):
    def __init__(self, model: AboutSettingsM, parent=None):
        super().__init__(title='About', parent=parent)
        self.model = model
        self.helpCard = HyperlinkCard(
            self.model.help_url,
            self.tr('Open help page'),
            FIF.HELP,
            self.tr('Help'),
            self.tr(
                'Discover new features and learn useful tips about BoostFace'),
            self
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve BoostFace by providing feedback'),
            self
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            FIF.INFO,
            self.tr('About'),
            '© ' +
            self.tr('Copyright') +
            f" {self.model.year}, {self.model.author}. " +
            self.tr('Version') +
            " " +
            self.model.version,
            self)
        self.addSettingCard(self.helpCard)
        self.addSettingCard(self.feedbackCard)
        self.addSettingCard(self.aboutCard)


class AboutSettingsGroupC:
    """ About setting group controller"""

    def __init__(self, model: AboutSettingsM, parent=None):
        self.model = model
        self.view = AboutSettingsGroup(self.model, parent)

        self.view.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(self.model.feedback_url)))


def create_about_setting_group(parent=None) -> AboutSettingsGroupC:
    """ create about setting group"""
    created_model = AboutSettingsM()
    created_view = AboutSettingsGroupC(created_model, parent=parent)

    return created_view
