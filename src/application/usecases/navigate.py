from src.application.usecases.get_content import get_current_content
from src.domain.aggregates import Content, PostGroup
from src.domain.entities.keyboard import KeyboardButton
from src.domain.value_objects.button import ButtonType
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store import StateStore


class NavigateException(Exception):
    pass


class ButtonNotFoundException(NavigateException):
    def __init__(self, button_label: str, *args):
        message = f"Button '{button_label}' bot found"
        super().__init__(message, *args)


async def navigate(
    state_store: StateStore,
    network: Network,
    external_user_id: int | str,
    button_label: str,
) -> Content:
    user_key = UserKey(network, str(external_user_id))
    current_node = await get_current_content(state_store, user_key)

    button = _find_button(current_node, button_label)
    if not button:
        raise ButtonNotFoundException(button_label=button_label)

    match button.type:
        case ButtonType.MAIN_MENU:
            await state_store.create_or_reset(user_key, NodeName.ROOT)

        case ButtonType.BACK:
            await state_store.pop_node(user_key)

        case _:
            await state_store.push_node(user_key, button.target)

    return await get_current_content(state_store, user_key)


def _find_button(node: Content, target_label: str) -> KeyboardButton | None:
    content = node.posts if isinstance(node, PostGroup) else [node]
    for post in content:
        for button in post.keyboard.get_buttons():
            if button.text == target_label:
                return button
    return None
