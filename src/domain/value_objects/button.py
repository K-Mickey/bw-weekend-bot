from enum import StrEnum


class BaseButton(StrEnum):
    BACK = "Назад"
    MAIN_MENU = "Главное меню"


class ButtonType(StrEnum):
    DEFAULT = "default"
    BACK = "back"
    MAIN_MENU = "main_menu"
