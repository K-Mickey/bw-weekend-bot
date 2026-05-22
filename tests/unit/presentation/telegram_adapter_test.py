from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from aiogram.types import KeyboardButton

from src.domain.aggregates.menu_node import MenuNode
from src.domain.value_objects.network import Network
from src.presentation.telegram_adapter import _create_keyboard, _send_content, cmd_help, cmd_start, handle_text_message
from tests.conftest import get_test_data


@pytest.fixture
def menu_node():
    yaml_file = get_test_data("menu_full.yaml")
    return MenuNode(**yaml_file)


@pytest.fixture
def mock_msg():
    mock = MagicMock()
    mock.from_user.id = 123456789
    mock.text = "Example"

    mock.answer = AsyncMock()
    mock.answer_photo = AsyncMock()
    mock.answer_video = AsyncMock()
    return mock


@pytest.fixture
def mock_start_conversation():
    with patch(
        "src.presentation.telegram_adapter.start_conversation",
        Mock(),
    ) as mock_start_conversation:
        yield mock_start_conversation


@pytest.fixture
def mock_navigate():
    navigate = Mock()
    with patch(
        "src.presentation.telegram_adapter.navigate",
        navigate,
    ) as mock_navigate:
        yield mock_navigate


@pytest.fixture
def mock_send_content():
    with patch(
        "src.presentation.telegram_adapter._send_content",
        AsyncMock(),
    ) as mock_send_content:
        yield mock_send_content


@pytest.mark.asyncio
async def test_create_keyboard_returns_correct_markup(menu_node):
    markup = _create_keyboard(menu_node)

    assert len(markup.keyboard) == 2
    row = markup.keyboard[0]
    assert len(row) == 1
    button_1 = row[0]
    assert button_1.text == "Button 1"
    assert isinstance(button_1, KeyboardButton)
    row = markup.keyboard[1]
    assert len(row) == 1
    button_2 = row[0]
    assert button_2.text == "Button 2"
    assert isinstance(button_2, KeyboardButton)


@pytest.mark.asyncio
async def test_create_keyboard_with_no_buttons():
    menu = MenuNode(id="root", content=[], keyboard=[])
    markup = _create_keyboard(menu)
    assert markup.keyboard == []


@pytest.mark.asyncio
async def test_send_text_content(menu_node, mock_msg):
    post = menu_node.content[0]
    await _send_content(mock_msg, post)

    mock_msg.answer.assert_awaited_once_with("Hello world", reply_markup=None)


@pytest.mark.asyncio
async def test_send_media_content(menu_node, mock_msg):
    post = menu_node.content[1]
    await _send_content(mock_msg, post)

    mock_msg.answer_photo.assert_awaited_once_with(photo="some_photo.jpg", caption="real photo", reply_markup=None)
    mock_msg.answer_video.assert_awaited_once_with(video="some_video.mp4", caption="real video", reply_markup=None)


@pytest.mark.asyncio
async def test_send_menu_content(menu_node, mock_msg):
    mock_keyboard = Mock()
    mock_keyboard.return_value = []

    with patch(
        "src.presentation.telegram_adapter._create_keyboard", return_value=mock_keyboard
    ) as mock_create_keyboard:
        await _send_content(mock_msg, menu_node)

        mock_create_keyboard.assert_called_once_with(menu_node)

    mock_msg.answer.assert_awaited_once_with("Hello world", reply_markup=mock_keyboard)
    mock_msg.answer_photo.assert_awaited_once_with(
        photo="some_photo.jpg", caption="real photo", reply_markup=mock_keyboard
    )
    mock_msg.answer_video.assert_awaited_once_with(
        video="some_video.mp4", caption="real video", reply_markup=mock_keyboard
    )


@pytest.mark.asyncio
async def test_send_content_with_no_content(mock_msg):
    menu = MenuNode(id="id", content=[])
    await _send_content(mock_msg, menu)
    mock_msg.answer.assert_not_awaited()
    mock_msg.answer_photo.assert_not_awaited()
    mock_msg.answer_video.assert_not_awaited()


@pytest.mark.asyncio
async def test_cmd_start(mock_msg, mock_start_conversation, mock_send_content):
    menu = MenuNode(id="id", content=[])
    mock_start_conversation.return_value = menu

    await cmd_start(mock_msg)

    mock_start_conversation.assert_called_once_with(Network.TELEGRAM, mock_msg.from_user.id)
    mock_send_content.assert_called_once_with(mock_msg, menu)


@pytest.mark.asyncio
async def test_cmd_help(mock_msg):
    await cmd_help(mock_msg)
    mock_msg.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_text_message(mock_msg, mock_navigate, mock_send_content):
    menu_example = MenuNode(id="id", content=[])
    mock_navigate.return_value = menu_example

    await handle_text_message(mock_msg)

    mock_navigate.assert_called_once_with(Network.TELEGRAM, mock_msg.from_user.id, mock_msg.text)
    mock_send_content.assert_called_once_with(mock_msg, menu_example)
    mock_msg.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_error_message(mock_msg, mock_navigate, mock_send_content):
    mock_navigate.side_effect = ValueError("Error")
    await handle_text_message(mock_msg)
    mock_send_content.assert_not_awaited()
    mock_msg.answer.assert_awaited_once()
