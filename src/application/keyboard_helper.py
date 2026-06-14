from src.domain.aggregates import Content, Post, PostGroup
from src.domain.value_objects.button import BaseButton, ButtonType
from src.domain.value_objects.keyboard import Keyboard, KeyboardButton, KeyboardRow
from src.domain.value_objects.node import NodeName


def find_target_button_in_content(content: Content, target_label: str) -> KeyboardButton | None:
    content = content.posts if isinstance(content, PostGroup) else [content]
    for post in content:
        for button in post.keyboard.get_buttons():
            if button.text == target_label:
                return button
    return None


def add_automatic_buttons(content: Content, history: tuple[str, ...]) -> Content:
    """
    Add automatic Back and Main menu buttons to a MenuNode based on its flags and session state.

    Button logic:
    - Back button added when flags.build=True and flags.is_back=True and len(session.history) > 1
    - Main menu button added when flags.build=True and flags.is_main=True and len(session.history) > 1
    - Buttons are added as new rows at the end of the keyboard array
    - Back button target = session.history[-2] (previous node)
    - Main menu button target = NodeName.ROOT
    """
    post_group = content.posts if isinstance(content, PostGroup) else [content]
    for post in post_group:
        post.keyboard = _form_keyboard(post, history)
    return content


def _form_keyboard(post: Post, history: tuple[str, ...]) -> Keyboard:
    keyboard = post.keyboard.model_copy(deep=True)
    if not post.flags.build:
        return keyboard

    buttons = []
    if post.flags.is_main and len(history) > 1:
        main_target = NodeName.ROOT
        buttons.append(
            KeyboardButton(
                text=BaseButton.MAIN_MENU,
                target=main_target,
                type=ButtonType.MAIN_MENU,
            )
        )

    if post.flags.is_back and len(history) > 2:
        back_target = history[-2]
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
