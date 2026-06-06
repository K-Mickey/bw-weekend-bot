from asyncio import sleep
from unittest.mock import AsyncMock, Mock

import pytest
from vkbottle import Keyboard as VKKeyboard
from vkbottle.bot import Message

from src.application.services import MessageSender
from src.application.services.vk_message_sender import VKMessageSender
from src.domain.entities import MediaGroup
from src.domain.entities.keyboard import Keyboard, KeyboardButton, KeyboardRow
from src.domain.entities.media import Photo, Text, Video
from src.domain.value_objects.button import BaseButton, ButtonType
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.infrastructure.file_cache import InMemoryMediaCache
from src.infrastructure.file_cache.exceptions import MediaCacheError
from src.infrastructure.file_cache.value_objects.cache_key import CacheKey
from src.infrastructure.file_cache.value_objects.cache_record import CacheRecord
from src.infrastructure.file_provider import get_file_path


class AnyVKKeyboard:
    def __eq__(self, other):
        return isinstance(other, VKKeyboard)

    def __repr__(self):
        return "AnyVKKeyboard()"


@pytest.fixture
def message_sender() -> MessageSender:
    cache = InMemoryMediaCache()
    bot = Mock()
    sender = VKMessageSender(bot, cache)
    uploader = Mock()
    uploader.upload = AsyncMock(return_value="new_file_id")
    sender.photo_uploader = uploader
    return sender


@pytest.fixture
def message() -> Message:
    message = Mock(spec=Message)
    message.peer_id = 123456789
    message.answer = AsyncMock()
    return message


@pytest.fixture
def photo() -> Photo:
    return Photo(local_path="exist.jpg", description="photo description")


@pytest.fixture
def video() -> Video:
    video = Video(
        local_path="exist.mp4",
        description="video description",
        vk_url="https://vk.com/video-1234_1234",
    )
    return video


@pytest.fixture
def media_group(photo, video) -> MediaGroup:
    return MediaGroup(items=[photo, video])


@pytest.fixture
def reply_markup() -> Keyboard:
    return Keyboard(
        rows=[
            KeyboardRow(
                buttons=[
                    KeyboardButton(text=BaseButton.MAIN_MENU, target=NodeName.ROOT, type=ButtonType.MAIN_MENU),
                    KeyboardButton(text=BaseButton.BACK, target=NodeName.ROOT, type=ButtonType.BACK),
                ]
            ),
            KeyboardRow(buttons=[KeyboardButton(text="Some button", target="some_id")]),
        ]
    )


def test_build_reply_markup(message_sender, reply_markup):
    result = message_sender._create_keyboard(reply_markup)
    assert isinstance(result, VKKeyboard)
    assert result.buttons[0][0].get_data().get("action").get("label") == BaseButton.MAIN_MENU
    assert result.buttons[0][1].get_data().get("action").get("label") == BaseButton.BACK
    assert result.buttons[1][0].get_data().get("action").get("label") == "Some button"


@pytest.mark.asyncio
async def test_send_text(message_sender, message):
    text = Text(text="test")
    await message_sender.send_text(message, text, Keyboard())
    message.answer.assert_called_once_with(text.text, keyboard=AnyVKKeyboard())


@pytest.mark.asyncio
async def test_send_photo(message_sender, message, photo):
    cache_key = CacheKey.create(photo, Network.VK)

    with pytest.raises(MediaCacheError):
        await message_sender.cache.get(cache_key)

    await message_sender.send_photo(message, photo, Keyboard())

    message.answer.assert_called_once_with(
        attachment="new_file_id",
        message=photo.description,
        keyboard=AnyVKKeyboard(),
    )
    message_sender.photo_uploader.upload.assert_called_once()
    cache_record = await message_sender.cache.get(cache_key)
    assert cache_record is not None


@pytest.mark.asyncio
async def test_send_photo_with_cache(message_sender, message, photo):
    cache_key = CacheKey.create(photo, Network.VK)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=get_file_path(photo))
    await message_sender.cache.add(cache_key, cache_record)

    await message_sender.send_photo(message, photo, Keyboard())
    message.answer.assert_called_once_with(attachment="1234", message=photo.description, keyboard=AnyVKKeyboard())
    message_sender.photo_uploader.upload.assert_not_called()


@pytest.mark.asyncio
async def test_send_photo_expired(message_sender, message, photo):
    cache_key = CacheKey.create(photo, Network.VK)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=get_file_path(photo), expires=1)
    await message_sender.cache.add(cache_key, cache_record)

    await sleep(1.1)

    await message_sender.send_photo(message, photo, Keyboard())
    message.answer.assert_called_once_with(
        attachment="new_file_id",
        message=photo.description,
        keyboard=AnyVKKeyboard(),
    )
    message_sender.photo_uploader.upload.assert_called_once()

    new_cache_record = await message_sender.cache.get(cache_key)
    assert new_cache_record.file_id != cache_record.file_id


@pytest.mark.asyncio
async def test_send_video(message_sender, message, video):
    await message_sender.send_video(message, video, Keyboard())
    message.answer.assert_called_once_with(
        attachment=video.vk_video_id, message=video.description, keyboard=AnyVKKeyboard()
    )


@pytest.mark.asyncio
async def test_send_media_group(message_sender, message, media_group, photo, video):
    cache_key = CacheKey.create(photo, Network.VK)
    with pytest.raises(MediaCacheError):
        await message_sender.cache.get_many(cache_key)

    await message_sender.send_media_group(message, media_group)

    expected_attachment = f"new_file_id,{video.vk_video_id}"
    message.answer.assert_called_once_with(attachment=expected_attachment)

    message_sender.photo_uploader.upload.assert_called_once()
    cache_record = await message_sender.cache.get(cache_key)
    assert cache_record is not None


@pytest.mark.asyncio
async def test_send_media_group_with_cache(message_sender, message, media_group, photo, video):
    cache_key = CacheKey.create(photo, Network.VK)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=get_file_path(photo))
    await message_sender.cache.add(cache_key, cache_record)

    await message_sender.send_media_group(message, media_group)

    expected_attachment = f"{cache_record.file_id},{video.vk_video_id}"
    message.answer.assert_called_once_with(attachment=expected_attachment)
    message_sender.photo_uploader.upload.assert_not_called()

    current_record = await message_sender.cache.get(cache_key)
    assert current_record.file_id == cache_record.file_id
