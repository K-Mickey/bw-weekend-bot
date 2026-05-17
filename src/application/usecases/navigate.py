from src.application.usecases.get_content import get_content
from src.application.usecases.start_conversation import start_conversation
from src.domain.aggregates import Content
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.button_type import ButtonType
from src.domain.entities.keyboard_button import KeyboardButton
from src.domain.value_objects.network import Network
from src.domain.value_objects.nodes import NodeName
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store import state_store


def navigate(network: Network, external_user_id: int | str, button_label: str) -> Content:
    """
    Navigate from the current node to the next node based on the button label.
    Handles the 'Back' button to go back in history.
    Returns the content for the next (or previous) node.
    """
    user_key = UserKey(network, str(external_user_id))
    session = state_store.get_session(user_key)
    if not session:
        return start_conversation(network, external_user_id)

    current_node_id = session.current
    current_node = get_content(session)

    if not isinstance(current_node, MenuNode):
        raise ValueError(f"Current node {current_node_id} is not a menu node")

    if not current_node.keyboard:
        raise ValueError(f"Current node {current_node_id} has no keyboard to navigate")

    button = _find_button(current_node.keyboard, button_label)
    if not button:
        raise ValueError("Button not found")

    match button.type:
        case ButtonType.MAIN_MENU:
            state_store.create_or_reset(user_key, NodeName.ROOT)

        case ButtonType.BACK:
            state_store.pop_node(user_key)

        case _:
            state_store.push_node(user_key, button.target)

    return get_content(session)


def _find_button(keyboard: list[list[KeyboardButton]], target_label: str) -> KeyboardButton | None:
    for row in keyboard:
        for button in row:
            if button.text == target_label:
                return button
    return None
