import pytest

from src.application.button_helper import add_automatic_buttons
from src.domain.aggregates.post_node import PostNode
from src.domain.entities.button_type import ButtonType
from src.domain.entities.keyboard import KeyboardButton, KeyboardRow
from src.domain.value_objects.buttons import Button
from src.domain.value_objects.menu_node_flags import PostNodeFlags
from src.domain.value_objects.nodes import NodeName


@pytest.fixture
def post_node():
    return PostNode(
        id="test_menu",
        media=[],
        keyboard=[[dict(text="Settings", target="settings")]],
        flags=PostNodeFlags(build=True, is_back=True, is_main=True),
    )


def test_add_automatic_buttons_returns_post_node_unchanged(session):
    post_node = PostNode(id="test_post", media=[])
    result = add_automatic_buttons(post_node, session)
    assert result is post_node


def test_add_automatic_buttons_returns_menu_node_unchanged_when_build_false(post_node, session):
    post_node.flags.build = False
    result = add_automatic_buttons(post_node, session)
    assert result is post_node


def test_add_automatic_buttons_adds_back_button_when_conditions_met(post_node, session):
    post_node.flags.is_main = False
    session.push("settings")  # History: [ROOT, settings]

    result = add_automatic_buttons(post_node, session)

    assert len(result.keyboard) == 2
    assert result.keyboard[0] == KeyboardRow(
        buttons=[KeyboardButton(text="Settings", target="settings", type=ButtonType.DEFAULT)]
    )
    assert result.keyboard[1] == KeyboardRow(
        buttons=[KeyboardButton(text=Button.BACK, target=NodeName.ROOT, type=ButtonType.BACK)]
    )


def test_add_automatic_buttons_does_not_add_back_button_when_history_length_1(post_node, session):
    post_node.flags.is_main = False
    result = add_automatic_buttons(post_node, session)

    assert len(result.keyboard) == 1
    assert result.keyboard[0] == KeyboardRow(
        buttons=[KeyboardButton(text="Settings", target="settings", type=ButtonType.DEFAULT)]
    )


def test_add_automatic_buttons_adds_main_menu_button_when_conditions_met(post_node, session):
    post_node.flags.is_back = False
    session.push("settings")  # History: [ROOT, settings]

    result = add_automatic_buttons(post_node, session)

    assert len(result.keyboard) == 2
    assert result.keyboard[0] == KeyboardRow(
        buttons=[KeyboardButton(text="Settings", target="settings", type=ButtonType.DEFAULT)]
    )
    assert result.keyboard[1] == KeyboardRow(
        buttons=[KeyboardButton(text=Button.MAIN_MENU, target=NodeName.ROOT, type=ButtonType.MAIN_MENU)]
    )


def test_add_automatic_buttons_does_not_add_main_menu_button_when_history_length_1(post_node, session):
    post_node.flags.is_back = False
    result = add_automatic_buttons(post_node, session)

    assert len(result.keyboard) == 1
    assert result.keyboard[0] == KeyboardRow(
        buttons=[KeyboardButton(text="Settings", target="settings", type=ButtonType.DEFAULT)]
    )


def test_add_automatic_buttons_adds_both_buttons_when_conditions_met(post_node, session):
    session.push("settings")  # History: [ROOT, settings]

    result = add_automatic_buttons(post_node, session)

    assert len(result.keyboard) == 3
    assert result.keyboard[0] == KeyboardRow(
        buttons=[KeyboardButton(text="Settings", target="settings", type=ButtonType.DEFAULT)]
    )
    assert result.keyboard[1] == KeyboardRow(
        buttons=[KeyboardButton(text=Button.BACK, target=NodeName.ROOT, type=ButtonType.BACK)]
    )
    assert result.keyboard[2] == KeyboardRow(
        buttons=[KeyboardButton(text=Button.MAIN_MENU, target=NodeName.ROOT, type=ButtonType.MAIN_MENU)]
    )


def test_add_automatic_buttons_preserves_original_menu_node(post_node, session):
    session.push("settings")  # History: [ROOT, settings]

    original_id = post_node.id
    original_media = post_node.media
    original_flags = post_node.flags

    result = add_automatic_buttons(post_node, session)

    assert post_node.id == original_id
    assert post_node.media == original_media
    assert post_node.flags == original_flags

    assert result.id == original_id
    assert result.media == original_media
    assert len(result.keyboard) == 3
