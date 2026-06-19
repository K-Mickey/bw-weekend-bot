from asyncio import sleep

import pytest
from aiogram.types import FSInputFile, ReplyKeyboardMarkup
from aiogram.utils.media_group import MediaType as TMediaType

from src.application.services import MessageSender, TelegramMessageSender
from src.domain.exceptions import CacheError
from src.domain.value_objects.button import BaseButton, ButtonType
from src.domain.value_objects.cache import CacheKey, CacheRecord
from src.domain.value_objects.keyboard import Keyboard, KeyboardButton, KeyboardRow
from src.domain.value_objects.media import Text
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.infrastructure.file_cache import MemoryMediaCache


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
def message_sender(content_repository) -> MessageSender:
    cache = MemoryMediaCache()
    return TelegramMessageSender(cache, content_repository)


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
async def test_send_text(message_sender, tg_message):
    text = Text(text="test")
    await message_sender.send_text(tg_message, text, Keyboard())
    tg_message.answer.assert_called_once_with(text.text, reply_markup=AnyReplyKeyboard())


@pytest.mark.asyncio
async def test_send_photo(message_sender, tg_message, photo):
    cache_key = CacheKey.create(photo, Network.TELEGRAM)

    with pytest.raises(CacheError):
        await message_sender.cache.get(cache_key)

    await message_sender.send_photo(tg_message, photo, Keyboard())

    tg_message.answer_photo.assert_called_once_with(
        AnyFSInputFile(), caption=photo.description, reply_markup=AnyReplyKeyboard()
    )
    cache_record = await message_sender.cache.get(cache_key)
    assert cache_record is not None


@pytest.mark.asyncio
async def test_send_photo_with_cache(message_sender, tg_message, photo, content_repository):
    cache_key = CacheKey.create(photo, Network.TELEGRAM)
    file_path = content_repository.get_media_path(photo)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=file_path)
    await message_sender.cache.add(cache_key, cache_record)

    await message_sender.send_photo(tg_message, photo, Keyboard())
    tg_message.answer_photo.assert_called_once_with(
        cache_record.file_id, caption=photo.description, reply_markup=AnyReplyKeyboard()
    )


@pytest.mark.asyncio
async def test_send_photo_expired(message_sender, tg_message, photo, content_repository):
    cache_key = CacheKey.create(photo, Network.TELEGRAM)
    file_path = content_repository.get_media_path(photo)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=file_path, expires=1)
    await message_sender.cache.add(cache_key, cache_record)

    await sleep(1.1)

    await message_sender.send_photo(tg_message, photo, Keyboard())
    tg_message.answer_photo.assert_called_once_with(
        AnyFSInputFile(), caption=photo.description, reply_markup=AnyReplyKeyboard()
    )
    new_cache_record = await message_sender.cache.get(cache_key)
    assert new_cache_record.file_id != cache_record.file_id


@pytest.mark.asyncio
async def test_send_video(message_sender, tg_message, video):
    cache_key = CacheKey.create(video, Network.TELEGRAM)

    with pytest.raises(CacheError):
        await message_sender.cache.get(cache_key)

    await message_sender.send_video(tg_message, video, Keyboard())

    tg_message.answer_video.assert_called_once_with(
        AnyFSInputFile(), caption=video.description, reply_markup=AnyReplyKeyboard()
    )
    cache_record = await message_sender.cache.get(cache_key)
    assert cache_record is not None


@pytest.mark.asyncio
async def test_send_video_with_cache(message_sender, tg_message, video, content_repository):
    cache_key = CacheKey.create(video, Network.TELEGRAM)
    file_path = content_repository.get_media_path(video)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=file_path)
    await message_sender.cache.add(cache_key, cache_record)

    await message_sender.send_video(tg_message, video, Keyboard())
    tg_message.answer_video.assert_called_once_with(
        cache_record.file_id, caption=video.description, reply_markup=AnyReplyKeyboard()
    )


@pytest.mark.asyncio
async def test_send_video_expired(message_sender, tg_message, video, content_repository):
    cache_key = CacheKey.create(video, Network.TELEGRAM)
    file_path = content_repository.get_media_path(video)
    cache_record = CacheRecord.from_file(file_id="1234", file_path=file_path, expires=1)
    await message_sender.cache.add(cache_key, cache_record)

    await sleep(1.1)

    await message_sender.send_video(tg_message, video, Keyboard())
    tg_message.answer_video.assert_called_once_with(
        AnyFSInputFile(), caption=video.description, reply_markup=AnyReplyKeyboard()
    )
    new_cache_record = await message_sender.cache.get(cache_key)
    assert new_cache_record.file_id != cache_record.file_id


@pytest.mark.asyncio
async def test_send_media_group(message_sender, tg_message, media_group):
    cache_keys = tuple(CacheKey.create(media, Network.TELEGRAM) for media in media_group)
    with pytest.raises(CacheError):
        await message_sender.cache.get_many(cache_keys)

    await message_sender.send_media_group(tg_message, media_group)

    tg_message.answer_media_group.assert_called_once_with(media=AnyMediaGroup())
    cache_records = await message_sender.cache.get_many(cache_keys)
    assert all(cache_record is not None for cache_record in cache_records)


@pytest.mark.asyncio
async def test_send_media_group_with_cache(message_sender, tg_message, media_group, content_repository):
    cache = {}
    for i, media in enumerate(media_group):
        cache_key = CacheKey.create(media, Network.TELEGRAM)
        file_path = content_repository.get_media_path(media)
        cache_record = CacheRecord.from_file(file_id=f"1_{i}", file_path=file_path)
        await message_sender.cache.add(cache_key, cache_record)
        cache[cache_key] = cache_record

    await message_sender.send_media_group(tg_message, media_group)

    tg_message.answer_media_group.assert_called_once_with(media=AnyMediaGroup())
    cache_records = await message_sender.cache.get_many(cache.keys())
    assert all(record.file_id == cache[key].file_id for key, record in cache_records.items())


@pytest.mark.asyncio
async def test_send_media_group_expired(message_sender, tg_message, media_group, content_repository):
    cache = {}
    for i, media in enumerate(media_group):
        cache_key = CacheKey.create(media, Network.TELEGRAM)
        file_path = content_repository.get_media_path(media)
        cache_record = CacheRecord.from_file(file_id=f"1_{i}", file_path=file_path, expires=1)
        await message_sender.cache.add(cache_key, cache_record)
        cache[cache_key] = cache_record

    await sleep(1.1)

    await message_sender.send_media_group(tg_message, media_group)

    tg_message.answer_media_group.assert_called_once_with(media=AnyMediaGroup())
    cache_records = await message_sender.cache.get_many(cache.keys())
    assert all(record.file_id != cache[key].file_id for key, record in cache_records.items())
