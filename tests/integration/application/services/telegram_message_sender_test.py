from asyncio import sleep
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import FSInputFile, Message, ReplyKeyboardMarkup
from aiogram.utils.media_group import MediaType as TMediaType

from src.application.services import MessageSender, TelegramMessageSender
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


class AnyReplyKeyboard:
    def __eq__(self, other):
        return isinstance(other, ReplyKeyboardMarkup)

    def __repr__(self):
        return "AnyReplyKeyboard()"


class AnyFSInputFile:
    def __eq__(self, other):
        return isinstance(other, FSInputFile)

    def __repr__(self):
        return "AnyFSInputFile()"


class AnyMediaGroup:
    def __eq__(self, other):
        return isinstance(other, list) and all(isinstance(item, TMediaType) for item in other)

    def __repr__(self):
        return "AnyMediaGroup()"


@pytest.fixture
def message_sender() -> MessageSender:
    cache = InMemoryMediaCache()
    return TelegramMessageSender(cache)


@pytest.fixture
def message() -> Message:
    message = Mock(spec=Message)
    message.from_user = Mock()
    message.from_user.id = 123456789

    photo_msg = Mock(spec=Message)
    photo_msg.photo = [Mock(file_id="cached_photo_id")]
    photo_msg.video = None

    video_msg = Mock(spec=Message)
    video_msg.video = Mock(file_id="cached_video_id")
    video_msg.photo = None

    message.answer = AsyncMock()
    message.answer_photo = AsyncMock(return_value=photo_msg)
    message.answer_video = AsyncMock(return_value=video_msg)

    message.answer_media_group = AsyncMock(return_value=[photo_msg, video_msg])

    return message


@pytest.fixture
def photo() -> Photo:
    return Photo(local_path="exist.jpg", description="photo description")


@pytest.fixture
def video() -> Video:
    return Video(local_path="exist.mp4", description="video description")


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
    assert isinstance(result, ReplyKeyboardMarkup)
    assert result.keyboard[0][0].text == BaseButton.MAIN_MENU
    assert result.keyboard[0][1].text == BaseButton.BACK
    assert result.keyboard[1][0].text == "Some button"
    assert result.resize_keyboard is True


@pytest.mark.asyncio
async def test_send_text(message_sender, message):
    text = Text(text="test")
    await message_sender.send_text(message, text, Keyboard())
    message.answer.assert_called_once_with(text.text, reply_markup=AnyReplyKeyboard())


@pytest.mark.asyncio
async def test_send_photo(message_sender, message, photo):
    cache_key = CacheKey.create(photo, Network.TELEGRAM)

    with pytest.raises(MediaCacheError):
        await message_sender.cache.get(cache_key)

    await message_sender.send_photo(message, photo, Keyboard())

    message.answer_photo.assert_called_once_with(
        AnyFSInputFile(), caption=photo.description, reply_markup=AnyReplyKeyboard()
    )
    cache_record = await message_sender.cache.get(cache_key)
    assert cache_record is not None


@pytest.mark.asyncio
async def test_send_photo_with_cache(message_sender, message, photo):
    cache_key = CacheKey.create(photo, Network.TELEGRAM)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=get_file_path(photo))
    await message_sender.cache.add(cache_key, cache_record)

    await message_sender.send_photo(message, photo, Keyboard())
    message.answer_photo.assert_called_once_with(
        cache_record.file_id, caption=photo.description, reply_markup=AnyReplyKeyboard()
    )


@pytest.mark.asyncio
async def test_send_photo_expired(message_sender, message, photo):
    cache_key = CacheKey.create(photo, Network.TELEGRAM)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=get_file_path(photo), expires=1)
    await message_sender.cache.add(cache_key, cache_record)

    await sleep(1.1)

    await message_sender.send_photo(message, photo, Keyboard())
    message.answer_photo.assert_called_once_with(
        AnyFSInputFile(), caption=photo.description, reply_markup=AnyReplyKeyboard()
    )
    new_cache_record = await message_sender.cache.get(cache_key)
    assert new_cache_record.file_id != cache_record.file_id


@pytest.mark.asyncio
async def test_send_video(message_sender, message, video):
    cache_key = CacheKey.create(video, Network.TELEGRAM)

    with pytest.raises(MediaCacheError):
        await message_sender.cache.get(cache_key)

    await message_sender.send_video(message, video, Keyboard())

    message.answer_video.assert_called_once_with(
        AnyFSInputFile(), caption=video.description, reply_markup=AnyReplyKeyboard()
    )
    cache_record = await message_sender.cache.get(cache_key)
    assert cache_record is not None


@pytest.mark.asyncio
async def test_send_video_with_cache(message_sender, message, video):
    cache_key = CacheKey.create(video, Network.TELEGRAM)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=get_file_path(video))
    await message_sender.cache.add(cache_key, cache_record)

    await message_sender.send_video(message, video, Keyboard())
    message.answer_video.assert_called_once_with(
        cache_record.file_id, caption=video.description, reply_markup=AnyReplyKeyboard()
    )


@pytest.mark.asyncio
async def test_send_video_expired(message_sender, message, video):
    cache_key = CacheKey.create(video, Network.TELEGRAM)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=get_file_path(video), expires=1)
    await message_sender.cache.add(cache_key, cache_record)

    await sleep(1.1)

    await message_sender.send_video(message, video, Keyboard())
    message.answer_video.assert_called_once_with(
        AnyFSInputFile(), caption=video.description, reply_markup=AnyReplyKeyboard()
    )
    new_cache_record = await message_sender.cache.get(cache_key)
    assert new_cache_record.file_id != cache_record.file_id


@pytest.mark.asyncio
async def test_send_media_group(message_sender, message, media_group):
    cache_keys = tuple(CacheKey.create(media, Network.TELEGRAM) for media in media_group)
    with pytest.raises(MediaCacheError):
        await message_sender.cache.get_many(cache_keys)

    await message_sender.send_media_group(message, media_group)

    message.answer_media_group.assert_called_once_with(media=AnyMediaGroup())
    cache_records = await message_sender.cache.get_many(cache_keys)
    assert all(cache_record is not None for cache_record in cache_records)


@pytest.mark.asyncio
async def test_send_media_group_with_cache(message_sender, message, media_group):
    cache = {}
    for i, media in enumerate(media_group):
        cache_key = CacheKey.create(media, Network.TELEGRAM)
        cache_record = CacheRecord.from_file(file_id=f"1_{i}", file_path=get_file_path(media))
        await message_sender.cache.add(cache_key, cache_record)
        cache[cache_key] = cache_record

    await message_sender.send_media_group(message, media_group)

    message.answer_media_group.assert_called_once_with(media=AnyMediaGroup())
    cache_records = await message_sender.cache.get_many(cache.keys())
    assert all(record.file_id == cache[key].file_id for key, record in cache_records.items())


@pytest.mark.asyncio
async def test_send_media_group_expired(message_sender, message, media_group):
    cache = {}
    for i, media in enumerate(media_group):
        cache_key = CacheKey.create(media, Network.TELEGRAM)
        cache_record = CacheRecord.from_file(file_id=f"1_{i}", file_path=get_file_path(media), expires=1)
        await message_sender.cache.add(cache_key, cache_record)
        cache[cache_key] = cache_record

    await sleep(1.1)

    await message_sender.send_media_group(message, media_group)

    message.answer_media_group.assert_called_once_with(media=AnyMediaGroup())
    cache_records = await message_sender.cache.get_many(cache.keys())
    assert all(record.file_id != cache[key].file_id for key, record in cache_records.items())
