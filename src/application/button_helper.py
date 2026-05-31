from src.domain.aggregates import Content, Post, PostGroup
from src.domain.entities.keyboard import Keyboard, KeyboardButton, KeyboardRow
from src.domain.entities.user_session import UserSession
from src.domain.value_objects.button import BaseButton, ButtonType
from src.domain.value_objects.node import NodeName


def add_automatic_buttons(node: Content, session: UserSession) -> Content:
    """
    Add automatic Back and Main menu buttons to a MenuNode based on its flags and session state.
    Returns the node unchanged if it's not a MenuNode.

    Button logic:
    - Back button added when flags.build=True and flags.is_back=True and len(session.history) > 1
    - Main menu button added when flags.build=True and flags.is_main=True and len(session.history) > 1
    - Buttons are added as new rows at the end of the keyboard array
    - Back button target = session.history[-2] (previous node)
    - Main menu button target = NodeName.ROOT
    """
    if isinstance(node, PostGroup):
        content = node.posts
    else:
        content = [node]

    for post in content:
        post.keyboard = _form_keyboard(post, session)

    return node


def _form_keyboard(node: Post, session: UserSession) -> Keyboard:
    keyboard = node.keyboard.model_copy(deep=True)

    if not node.flags.build:
        return keyboard

    buttons = []
    if node.flags.is_main and len(session.history) > 1:
        main_target = NodeName.ROOT
        buttons.append(
            KeyboardButton(
                text=BaseButton.MAIN_MENU,
                target=main_target,
                type=ButtonType.MAIN_MENU,
            )
        )

    if node.flags.is_back and len(session.history) > 2:
        back_target = session.history[-2]
        buttons.append(
            KeyboardButton(
                text=BaseButton.BACK,
                target=back_target,
                type=ButtonType.BACK,
            )
        )

    if buttons:
        keyboard.add_row(KeyboardRow(buttons=buttons))

    return keyboard
