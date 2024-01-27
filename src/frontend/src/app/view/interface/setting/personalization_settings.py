# coding=utf-8
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import SettingCardGroup, OptionsSettingCard, SwitchSettingCard, CustomColorSettingCard, \
    ComboBoxSettingCard

from src.app.config.config import cfg

__all__ = ['create_personalization_setting_group']


class PersonalizationSettingM:
    """ Personlization setting model"""

    def __init__(self):
        # theme
        self.theme_mode = cfg.themeMode
        self.theme_color = cfg.themeColor

        # dpi
        self.dpi_scale = cfg.dpiScale

        # language
        self.language = cfg.language


class PersonalizationSettingGroup(SettingCardGroup):
    """ Personalization setting group"""

    def __init__(self, model: PersonalizationSettingM, parent=None):
        super().__init__(title='Personalization', parent=parent)
        self.model = model
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr('Mica effect'),
            self.tr('Apply semi transparent to windows and surfaces'),
            cfg.micaEnabled,
            self
        )

        self.themeCard = OptionsSettingCard(
            self.model.theme_mode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self
        )
        self.themeColorCard = CustomColorSettingCard(
            self.model.theme_color,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            parent=self
        )
        self.zoomCard = OptionsSettingCard(
            self.model.dpi_scale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self
        )
        self.languageCard = ComboBoxSettingCard(
            self.model.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self
        )

        self.addSettingCard(self.micaCard)
        self.addSettingCard(self.themeCard)
        self.addSettingCard(self.themeColorCard)
        self.addSettingCard(self.zoomCard)
        self.addSettingCard(self.languageCard)


class PersonalizationSettingC:
    """ Personalization setting controller"""

    def __init__(self, model: PersonalizationSettingM,
                 view: PersonalizationSettingGroup):
        self.model = model
        self.view = view
        self._init_signal_binding()

    def _init_signal_binding(self):
        # self.view.micaCard.optionChanged.connect(self._update_mica)
        self.view.themeCard.optionChanged.connect(self._update_theme)
        self.view.themeColorCard.colorChanged.connect(self._update_theme_color)
        self.view.zoomCard.optionChanged.connect(self._update_zoom)
        # self.view.languageCard.optionChanged.connect(self._update_language)

    def _update_mica(self, value):
        self.model.micaEnabled = value

    def _update_theme(self, value):
        self.model.themeMode = value

    def _update_theme_color(self, value):
        self.model.themeColor = value

    def _update_zoom(self, value):
        self.model.dpiScale = value

    def _update_language(self, value):
        self.model.language = value


def create_personalization_setting_group(parent=None) -> PersonalizationSettingC:
    """ create personalization setting group"""
    created_model = PersonalizationSettingM()
    created_view = PersonalizationSettingGroup(created_model, parent=parent)
    created_controller = PersonalizationSettingC(created_model, created_view)

    return created_controller
