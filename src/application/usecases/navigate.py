from src.application.usecases.get_content import get_content
from src.domain.aggregates.menu_node import MenuNode
from src.domain.aggregates.post_node import PostNode
from src.domain.entities.keyboard_button import KeyboardButton
from src.domain.value_objects.buttons import Button
from src.domain.value_objects.network import Network
from src.domain.value_objects.nodes import NodeName
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.content_repository import ContentRepository
from src.infrastructure.state_store import state_store


def navigate(network: Network, external_user_id: int | str, button_label: str) -> MenuNode | PostNode:
    """
    Navigate from the current node to the next node based on the button label.
    Handles the 'Back' button to go back in history.
    Returns the content for the next (or previous) node.
    """
    user_key = UserKey(network, str(external_user_id))
    session = state_store.get_session(user_key)
    if session is None or button_label == Button.MAIN_MENU:
        state_store.create_or_reset(user_key, NodeName.ROOT)
        current_node_id = NodeName.ROOT
        return get_content(current_node_id)

    if button_label == Button.BACK:
        state_store.pop_node(user_key)
        current_node_id = session.current
        return get_content(current_node_id)

    current_node_id = session.current

    current_node = ContentRepository.get_node(current_node_id)
    if current_node is None:
        raise ValueError(f"Current node not found: {current_node_id}")

    if not isinstance(current_node, MenuNode):
        raise ValueError(f"Current node {current_node_id} is not a menu node")

    if not current_node.keyboard:
        raise ValueError(f"Current node {current_node_id} has no keyboard to navigate")

    target_node_id = _find_button(current_node.keyboard, button_label)
    if target_node_id is None:
        raise ValueError("Button not found")

    state_store.push_node(user_key, target_node_id)

    return get_content(target_node_id)


def _find_button(keyboard: list[list[KeyboardButton]], target_label: str) -> str | None:
    for row in keyboard:
        for button in row:
            if button.text == target_label:
                return button.target
    return None
