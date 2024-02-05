from enum import Enum

from qfluentwidgets import FluentIconBase, Theme, getIconColor


class Icon(FluentIconBase, Enum):
    GRID = "Grid"
    MENU = "Menu"
    TEXT = "Text"
    EMOJI_TAB_SYMBOLS = "EmojiTabSymbols"

    def path(self, theme=Theme.AUTO):
        return f":/gallery/images/icons/{self.value}_{getIconColor(theme)}.svg"
