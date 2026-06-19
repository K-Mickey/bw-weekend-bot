from asyncio import sleep
from unittest.mock import AsyncMock, Mock

import pytest
from vkbottle import Keyboard as VKKeyboard

from src.application.services import MessageSender
from src.application.services.vk_message_sender import VKMessageSender
from src.domain.exceptions import CacheError
from src.domain.value_objects.button import BaseButton, ButtonType
from src.domain.value_objects.cache import CacheKey, CacheRecord
from src.domain.value_objects.keyboard import Keyboard, KeyboardButton, KeyboardRow
from src.domain.value_objects.media import Text
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.infrastructure.file_cache import MemoryMediaCache


class AnyVKKeyboard:
    def __eq__(self, other):
        return isinstance(other, VKKeyboard)

    def __repr__(self):
        return "AnyVKKeyboard()"


@pytest.fixture
def message_sender(content_repository) -> MessageSender:
    cache = MemoryMediaCache()
    bot = Mock()
    sender = VKMessageSender(bot, cache, content_repository)
    uploader = Mock()
    uploader.upload = AsyncMock(return_value="new_file_id")
    sender.photo_uploader = uploader
    return sender


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
async def test_send_text(message_sender, vk_message):
    text = Text(text="test")
    await message_sender.send_text(vk_message, text, Keyboard())
    vk_message.answer.assert_called_once_with(text.text, keyboard=AnyVKKeyboard())


@pytest.mark.asyncio
async def test_send_photo(message_sender, vk_message, photo):
    cache_key = CacheKey.create(photo, Network.VK)

    with pytest.raises(CacheError):
        await message_sender.cache.get(cache_key)

    await message_sender.send_photo(vk_message, photo, Keyboard())

    vk_message.answer.assert_called_once_with(
        attachment="new_file_id",
        message=photo.description,
        keyboard=AnyVKKeyboard(),
    )
    message_sender.photo_uploader.upload.assert_called_once()
    cache_record = await message_sender.cache.get(cache_key)
    assert cache_record is not None


@pytest.mark.asyncio
async def test_send_photo_with_cache(message_sender, vk_message, photo, content_repository):
    cache_key = CacheKey.create(photo, Network.VK)
    file_path = content_repository.get_media_path(photo)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=file_path)
    await message_sender.cache.add(cache_key, cache_record)

    await message_sender.send_photo(vk_message, photo, Keyboard())
    vk_message.answer.assert_called_once_with(attachment="1234", message=photo.description, keyboard=AnyVKKeyboard())
    message_sender.photo_uploader.upload.assert_not_called()


@pytest.mark.asyncio
async def test_send_photo_expired(message_sender, vk_message, photo, content_repository):
    cache_key = CacheKey.create(photo, Network.VK)
    file_path = content_repository.get_media_path(photo)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=file_path, expires=1)
    await message_sender.cache.add(cache_key, cache_record)

    await sleep(1.1)

    await message_sender.send_photo(vk_message, photo, Keyboard())
    vk_message.answer.assert_called_once_with(
        attachment="new_file_id",
        message=photo.description,
        keyboard=AnyVKKeyboard(),
    )
    message_sender.photo_uploader.upload.assert_called_once()

    new_cache_record = await message_sender.cache.get(cache_key)
    assert new_cache_record.file_id != cache_record.file_id


@pytest.mark.asyncio
async def test_send_video(message_sender, vk_message, video):
    await message_sender.send_video(vk_message, video, Keyboard())
    vk_message.answer.assert_called_once_with(
        attachment=video.vk_video_id, message=video.description, keyboard=AnyVKKeyboard()
    )


@pytest.mark.asyncio
async def test_send_media_group(message_sender, vk_message, media_group, photo, video):
    cache_key = CacheKey.create(photo, Network.VK)
    with pytest.raises(CacheError):
        await message_sender.cache.get_many(cache_key)

    await message_sender.send_media_group(vk_message, media_group)

    expected_attachment = f"new_file_id,{video.vk_video_id}"
    vk_message.answer.assert_called_once_with(attachment=expected_attachment)

    message_sender.photo_uploader.upload.assert_called_once()
    cache_record = await message_sender.cache.get(cache_key)
    assert cache_record is not None


@pytest.mark.asyncio
async def test_send_media_group_with_cache(message_sender, vk_message, media_group, photo, video, content_repository):
    cache_key = CacheKey.create(photo, Network.VK)
    file_path = content_repository.get_media_path(photo)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=file_path)
    await message_sender.cache.add(cache_key, cache_record)

    await message_sender.send_media_group(vk_message, media_group)

    expected_attachment = f"{cache_record.file_id},{video.vk_video_id}"
    vk_message.answer.assert_called_once_with(attachment=expected_attachment)
    message_sender.photo_uploader.upload.assert_not_called()

    current_record = await message_sender.cache.get(cache_key)
    assert current_record.file_id == cache_record.file_id
