from .location import LOCATION_MESSAGES
from .main_menu import MENU_MESSAGES
from .schedule import SCHEDULE_MESSAGES
from .states import States

MESSAGES = MENU_MESSAGES | LOCATION_MESSAGES | SCHEDULE_MESSAGES

__all__ = ["States", "MESSAGES"]
