from src.domain.aggregates import Content
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.keyboard_button import KeyboardButton
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
    if not isinstance(node, MenuNode):
        return node

    if not node.flags.build:
        return node

    new_node = node.model_copy(deep=True)

    if node.flags.is_back and len(session.history) > 1:
        back_target = session.history[-2]
        new_node.keyboard.append([KeyboardButton(text=Button.BACK, target=back_target)])

    if node.flags.is_main and len(session.history) > 1:
        main_target = NodeName.ROOT
        new_node.keyboard.append([KeyboardButton(text=Button.MAIN_MENU, target=main_target)])

    return new_node
