from src.application.usecases.get_content import get_current_content
from src.domain.aggregates import Content, PostGroup
from src.domain.entities.keyboard import KeyboardButton
from src.domain.value_objects.button import ButtonType
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store import state_store


class NavigateException(Exception):
    pass


class ButtonNotFoundException(NavigateException):
    def __init__(self, button_label: str, *args):
        message = f"Button '{button_label}' bot found"
        super().__init__(message, *args)


def navigate(network: Network, external_user_id: int | str, button_label: str) -> Content:
    """
    Navigate from the current node to the next node based on the button label.
    Handles the 'Back' button to go back in history.
    Returns the content for the next (or previous) node.
    """
    user_key = UserKey(network, str(external_user_id))
    current_node = get_current_content(user_key)

    button = _find_button(current_node, button_label)
    if not button:
        raise ButtonNotFoundException(button_label=button_label)

    match button.type:
        case ButtonType.MAIN_MENU:
            state_store.create_or_reset(user_key, NodeName.ROOT)

        case ButtonType.BACK:
            state_store.pop_node(user_key)

        case _:
            state_store.push_node(user_key, button.target)

    return get_current_content(user_key)


def _find_button(node: Content, target_label: str) -> KeyboardButton | None:
    content = node.posts if isinstance(node, PostGroup) else [node]
    for post in content:
        for row in post.keyboard:
            for button in row:
                if button.text == target_label:
                    return button
    return None
