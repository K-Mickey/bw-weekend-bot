from src.domain.aggregates import Content, PostNode
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.button_type import ButtonType
from src.domain.entities.keyboard import Keyboard, KeyboardButton, KeyboardRow
from src.domain.value_objects.buttons import Button
from src.domain.value_objects.nodes import NodeName
from src.domain.value_objects.user_session import UserSession


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
    if isinstance(node, MenuNode):
        content = node.content
    else:
        content = [node]

    for post in content:
        post.keyboard = _form_keyboard(post, session)

    return node


def _form_keyboard(node: PostNode, session: UserSession) -> Keyboard:
    keyboard = node.keyboard.model_copy(deep=True)

    if not node.flags.build:
        return keyboard

    if node.flags.is_back and len(session.history) > 1:
        back_target = session.history[-2]
        keyboard.add_row(
            KeyboardRow(
                buttons=[
                    KeyboardButton(
                        text=Button.BACK,
                        target=back_target,
                        type=ButtonType.BACK,
                    )
                ]
            )
        )

    if node.flags.is_main and len(session.history) > 1:
        main_target = NodeName.ROOT
        keyboard.add_row(
            KeyboardRow(
                buttons=[
                    KeyboardButton(
                        text=Button.MAIN_MENU,
                        target=main_target,
                        type=ButtonType.MAIN_MENU,
                    )
                ]
            )
        )

    return keyboard
