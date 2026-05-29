from unittest.mock import ANY, AsyncMock, MagicMock, Mock, call, patch

import pytest
from aiogram.types import KeyboardButton

from src.domain.aggregates import PostNode
from src.domain.aggregates.menu_node import MenuNode
from src.domain.value_objects.network import Network
from src.presentation.telegram_adapter import _create_keyboard, _send_content, cmd_help, cmd_start, handle_text_message

PREFIX = "src.presentation.telegram_adapter"


@pytest.fixture
def menu_node(get_test_data):
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
    with patch(f"{PREFIX}.start_conversation", Mock()) as mock_start_conversation:
        yield mock_start_conversation


@pytest.fixture
def mock_navigate():
    navigate = Mock()
    with patch(f"{PREFIX}.navigate", navigate) as mock_navigate:
        yield mock_navigate


@pytest.fixture
def mock_send_content():
    with patch(f"{PREFIX}._send_content", AsyncMock()) as mock_send_content:
        yield mock_send_content


@pytest.fixture
def mock_cmd_start():
    with patch(f"{PREFIX}.cmd_start", AsyncMock()) as mock_cmd_start:
        yield mock_cmd_start


@pytest.fixture
def mock_send_photo_with_cache():
    with patch(f"{PREFIX}._send_photo_with_cache", AsyncMock()) as mock_send_photo_with_cache:
        yield mock_send_photo_with_cache


@pytest.fixture
def mock_send_video_with_cache():
    with patch(f"{PREFIX}._send_video_with_cache", AsyncMock()) as mock_send_video_with_cache:
        yield mock_send_video_with_cache


@pytest.fixture
def mock_create_keyboard():
    with patch(f"{PREFIX}._create_keyboard", Mock(return_value=[])) as mock_create_keyboard:
        yield mock_create_keyboard


@pytest.fixture
def mock_get_content_by_id(get_test_data):
    help_file = get_test_data("help.yaml")
    return_value = PostNode(**help_file)
    with patch(f"{PREFIX}.get_content_by_id", Mock(return_value=return_value)) as mock_get_content_by_id:
        yield mock_get_content_by_id


@pytest.mark.asyncio
async def test_create_keyboard_returns_correct_markup(menu_node):
    markup = _create_keyboard(menu_node.content[0])

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
    menu = PostNode(id="root", media=[])
    markup = _create_keyboard(menu)
    assert markup.keyboard == []


@pytest.mark.asyncio
async def test_send_text_content(menu_node, mock_msg, mock_create_keyboard):
    post = menu_node.content[0]
    await _send_content(mock_msg, post)

    mock_msg.answer.assert_awaited_once_with("Hello world", reply_markup=[])


@pytest.mark.asyncio
async def test_send_media_content(menu_node, mock_msg, mock_send_photo_with_cache, mock_send_video_with_cache):
    post = menu_node.content[1]
    await _send_content(mock_msg, post)

    mock_send_photo_with_cache.assert_awaited_once_with(mock_msg, post.media[0], ANY)
    mock_send_video_with_cache.assert_awaited_once_with(mock_msg, post.media[1], ANY)


@pytest.mark.asyncio
async def test_send_menu_content(
    menu_node,
    mock_msg,
    mock_create_keyboard,
    mock_send_photo_with_cache,
    mock_send_video_with_cache,
):

    await _send_content(mock_msg, menu_node)

    mock_create_keyboard.assert_has_calls([call(menu_node.content[0]), call(menu_node.content[1])])
    mock_msg.answer.assert_awaited_once_with("Hello world", reply_markup=[])
    mock_send_photo_with_cache.assert_awaited_once()
    mock_send_video_with_cache.assert_awaited_once()


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
async def test_cmd_help(mock_msg, mock_get_content_by_id):
    await cmd_help(mock_msg)
    mock_msg.answer.assert_awaited_once()
    mock_get_content_by_id.assert_called_once_with("help")


@pytest.mark.asyncio
async def test_handle_text_message(mock_msg, mock_navigate, mock_send_content, mock_cmd_start):
    menu_example = MenuNode(id="id", content=[])
    mock_navigate.return_value = menu_example

    await handle_text_message(mock_msg)

    mock_navigate.assert_called_once_with(Network.TELEGRAM, mock_msg.from_user.id, mock_msg.text)
    mock_send_content.assert_called_once_with(mock_msg, menu_example)
    mock_msg.answer.assert_not_awaited()
    mock_cmd_start.assert_not_awaited()
