import pytest

from src.application.keyboard_helper import add_automatic_buttons, find_target_button_in_content
from src.domain.value_objects.button import BaseButton, ButtonType
from src.domain.value_objects.keyboard import KeyboardButton, KeyboardRow
from src.domain.value_objects.node import NodeName


@pytest.fixture
def simple_post(get_content):
    return get_content("post_simple.yaml")


def get_test_keyboard_row():
    return KeyboardRow(buttons=[KeyboardButton(text="Settings", target="settings", type=ButtonType.DEFAULT)])


def get_back_button():
    return KeyboardButton(text=BaseButton.BACK, target="other", type=ButtonType.BACK)


def get_main_menu_button():
    return KeyboardButton(text=BaseButton.MAIN_MENU, target=NodeName.ROOT, type=ButtonType.MAIN_MENU)


def test_add_automatic_buttons_returns_post_node_unchanged(session, post):
    result = add_automatic_buttons(post, session)
    assert result is post


def test_add_automatic_buttons_returns_menu_node_unchanged_when_build_false(simple_post, session):
    simple_post.flags.build = False
    result = add_automatic_buttons(simple_post, session)
    assert result is simple_post


def test_add_automatic_buttons_adds_back_button_when_conditions_met(simple_post, session):
    simple_post.flags.is_main = False
    session.push("other")
    session.push("settings")  # History: [ROOT, other, settings]

    result = add_automatic_buttons(simple_post, session)

    assert len(result.keyboard) == 2
    assert result.keyboard[0] == get_test_keyboard_row()
    assert result.keyboard[1] == KeyboardRow(buttons=[get_back_button()])


def test_add_automatic_buttons_does_not_add_back_button_when_history_length_1(simple_post, session):
    simple_post.flags.is_main = False
    result = add_automatic_buttons(simple_post, session)

    assert len(result.keyboard) == 1
    assert result.keyboard[0] == get_test_keyboard_row()


def test_add_automatic_buttons_adds_main_menu_button_when_conditions_met(simple_post, session):
    simple_post.flags.is_back = False
    session.push("settings")  # History: [ROOT, settings]

    result = add_automatic_buttons(simple_post, session)

    assert len(result.keyboard) == 2
    assert result.keyboard[0] == get_test_keyboard_row()
    assert result.keyboard[1] == KeyboardRow(buttons=[get_main_menu_button()])


def test_add_automatic_buttons_does_not_add_main_menu_button_when_history_length_1(simple_post, session):
    simple_post.flags.is_back = False
    result = add_automatic_buttons(simple_post, session)

    assert len(result.keyboard) == 1
    assert result.keyboard[0] == get_test_keyboard_row()


def test_add_automatic_buttons_adds_both_buttons_when_conditions_met(simple_post, session):
    session.push("other")
    session.push("settings")  # History: [ROOT, other, settings]

    result = add_automatic_buttons(simple_post, session)

    assert len(result.keyboard) == 2
    assert result.keyboard[0] == get_test_keyboard_row()
    assert result.keyboard[1] == KeyboardRow(buttons=[get_main_menu_button(), get_back_button()])


def test_add_automatic_buttons_preserves_original_menu_node(simple_post, session):
    session.push("other")
    session.push("settings")  # History: [ROOT, other, settings]

    original_id = simple_post.id
    original_media = simple_post.media
    original_flags = simple_post.flags

    result = add_automatic_buttons(simple_post, session)

    assert simple_post.id == original_id
    assert simple_post.media == original_media
    assert simple_post.flags == original_flags

    assert result.id == original_id
    assert result.media == original_media
    assert len(result.keyboard) == 2


@pytest.mark.parametrize(
    "button_label", ("Цены", "Музыкальные группы", "Локации", "Педагоги", "Чат-болталка", "Контакты")
)
def test_find_target_button_in_content(get_content, button_label: str):
    content = get_content("main.yaml")
    result = find_target_button_in_content(content, button_label)
    assert isinstance(result, KeyboardButton)


@pytest.mark.parametrize("button_label", ("Button 1", "Button 2"))
def test_find_target_button_in_content_with_group_posts(get_content, button_label: str):
    content = get_content("menu_full.yaml")
    result = find_target_button_in_content(content, button_label)
    assert isinstance(result, KeyboardButton)


@pytest.mark.parametrize("button_label", ("Назад", "Главное меню"))
def test_find_target_button_in_content_not_found(get_content, button_label: str):
    content = get_content("main.yaml")
    result = find_target_button_in_content(content, button_label)
    assert result is None
