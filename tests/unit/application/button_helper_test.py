import pytest

from src.application.button_helper import add_automatic_buttons
from src.domain.aggregates.menu_node import MenuNode
from src.domain.aggregates.post_node import PostNode
from src.domain.entities.keyboard_button import KeyboardButton
from src.domain.value_objects.buttons import Button
from src.domain.value_objects.menu_node_flags import MenuNodeFlags
from src.domain.value_objects.network import Network
from src.domain.value_objects.nodes import NodeName
from src.domain.value_objects.user_key import UserKey
from src.domain.value_objects.user_session import UserSession


@pytest.fixture
def session():
    user_key = UserKey(Network.TELEGRAM, "123")
    return UserSession(user_key, NodeName.ROOT)


@pytest.fixture
def menu_node():
    return MenuNode(
        id="test_menu",
        content=[],
        keyboard=[
            [KeyboardButton(text="Settings", target="settings")],
        ],
        flags=MenuNodeFlags(build=True, is_back=True, is_main=True),
    )


def test_add_automatic_buttons_returns_post_node_unchanged(session):
    post_node = PostNode(id="test_post", media=[])
    result = add_automatic_buttons(post_node, session)
    assert result is post_node


def test_add_automatic_buttons_returns_menu_node_unchanged_when_build_false(menu_node, session):
    menu_node.flags.build = False
    result = add_automatic_buttons(menu_node, session)
    assert result is menu_node


def test_add_automatic_buttons_adds_back_button_when_conditions_met(menu_node, session):
    menu_node.flags.is_main = False
    session.push("settings")  # History: [ROOT, settings]

    result = add_automatic_buttons(menu_node, session)

    assert result is not menu_node
    assert len(result.keyboard) == 2
    assert result.keyboard[0] == [KeyboardButton(text="Settings", target="settings")]
    assert result.keyboard[1] == [KeyboardButton(text=Button.BACK, target=NodeName.ROOT)]


def test_add_automatic_buttons_does_not_add_back_button_when_history_length_1(menu_node, session):
    menu_node.flags.is_main = False
    result = add_automatic_buttons(menu_node, session)

    assert result is not menu_node
    assert len(result.keyboard) == 1
    assert result.keyboard[0] == [KeyboardButton(text="Settings", target="settings")]


def test_add_automatic_buttons_adds_main_menu_button_when_conditions_met(menu_node, session):
    menu_node.flags.is_back = False
    session.push("settings")  # History: [ROOT, settings]

    result = add_automatic_buttons(menu_node, session)

    assert result is not menu_node
    assert len(result.keyboard) == 2
    assert result.keyboard[0] == [KeyboardButton(text="Settings", target="settings")]
    assert result.keyboard[1] == [KeyboardButton(text=Button.MAIN_MENU, target=NodeName.ROOT)]


def test_add_automatic_buttons_does_not_add_main_menu_button_when_history_length_1(menu_node, session):
    menu_node.flags.is_back = False
    result = add_automatic_buttons(menu_node, session)

    assert result is not menu_node
    assert len(result.keyboard) == 1
    assert result.keyboard[0] == [KeyboardButton(text="Settings", target="settings")]


def test_add_automatic_buttons_adds_both_buttons_when_conditions_met(menu_node, session):
    session.push("settings")  # History: [ROOT, settings]

    result = add_automatic_buttons(menu_node, session)

    assert result is not menu_node
    assert len(result.keyboard) == 3
    assert result.keyboard[0] == [KeyboardButton(text="Settings", target="settings")]
    assert result.keyboard[1] == [KeyboardButton(text=Button.BACK, target=NodeName.ROOT)]
    assert result.keyboard[2] == [KeyboardButton(text=Button.MAIN_MENU, target=NodeName.ROOT)]


def test_add_automatic_buttons_preserves_original_menu_node(menu_node, session):
    session.push("settings")  # History: [ROOT, settings]

    original_id = menu_node.id
    original_content = menu_node.content
    original_keyword_ref = menu_node.keyboard
    original_flags = menu_node.flags

    result = add_automatic_buttons(menu_node, session)

    assert menu_node.id == original_id
    assert menu_node.content == original_content
    assert menu_node.keyboard == original_keyword_ref
    assert menu_node.flags == original_flags

    assert result is not menu_node
    assert result.id == original_id
    assert result.content == original_content
    assert len(result.keyboard) == 3
