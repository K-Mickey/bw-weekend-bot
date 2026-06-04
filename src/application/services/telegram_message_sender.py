import logging
from pathlib import Path
from typing import Iterable

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import (
    FSInputFile,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.media_group import MediaGroupBuilder

from src.application.services import MessageSender
from src.domain.entities import MediaGroup
from src.domain.entities.keyboard import Keyboard
from src.domain.entities.media import Photo, Text, Video
from src.domain.value_objects.network import Network
from src.infrastructure.file_cache import MediaCache
from src.infrastructure.file_cache.exceptions import MediaCacheError
from src.infrastructure.file_cache.value_objects.cache_key import CacheKey
from src.infrastructure.file_cache.value_objects.cache_record import CacheRecord
from src.infrastructure.file_provider import get_file_path

logger = logging.getLogger(__name__)


class TelegramMessageSender(MessageSender):
    def __init__(self, cache: MediaCache):
        self.cache = cache

    async def send_text(self, message: Message, text: Text, reply_markup: Keyboard) -> None:
        try:
            keyboard_markup = self._create_keyboard(reply_markup)
            await message.answer(text.text, reply_markup=keyboard_markup)
        except TelegramForbiddenError:
            logger.warning(f"User {message.from_user.id} blocked the bot.")

    async def send_photo(self, message: Message, photo: Photo, reply_markup: Keyboard) -> None:
        cache_key = CacheKey.create(photo, Network.TELEGRAM)
        keyboard_markup = self._create_keyboard(reply_markup)
        try:
            cache_record = await self.cache.get(cache_key)
            await message.answer_photo(
                cache_record.file_id,
                caption=photo.description,
                reply_markup=keyboard_markup,
            )

        except TelegramForbiddenError:
            logger.warning(f"User {message.from_user.id} blocked the bot.")

        except (TelegramBadRequest, MediaCacheError) as e:
            logger.debug(f"Failed to send photo {photo.local_path}: {e}")
            await self.cache.remove(cache_key)

            file_path = get_file_path(photo)
            file = FSInputFile(file_path)
            sent_message = await message.answer_photo(
                file,
                caption=photo.description,
                reply_markup=keyboard_markup,
            )
            await self._safe_update_cache(
                cache_key=cache_key,
                message=sent_message,
                file_path=file_path,
            )

    async def send_video(self, message: Message, video: Video, reply_markup: Keyboard) -> None:
        cache_key = CacheKey.create(video, Network.TELEGRAM)
        keyboard_markup = self._create_keyboard(reply_markup)
        try:
            cache_record = await self.cache.get(cache_key)
            await message.answer_video(
                cache_record.file_id,
                caption=video.description,
                reply_markup=keyboard_markup,
            )

        except TelegramForbiddenError:
            logger.warning(f"User {message.from_user.id} blocked the bot.")

        except (TelegramBadRequest, MediaCacheError) as e:
            logger.debug(f"Failed to send video {video.local_path}: {e}")
            await self.cache.remove(cache_key)

            file_path = get_file_path(video)
            file = FSInputFile(file_path)
            sent_message = await message.answer_video(
                file,
                caption=video.description,
                reply_markup=keyboard_markup,
            )
            await self._safe_update_cache(
                cache_key=cache_key,
                message=sent_message,
                file_path=file_path,
            )

    async def send_media_group(self, message: Message, media_group: MediaGroup) -> None:
        cache_keys = tuple(CacheKey.create(media, Network.TELEGRAM) for media in media_group)
        try:
            cache_records = await self.cache.get_many(cache_keys)
            media_source = (cache_records[cache_key].file_id for cache_key in cache_keys)
            album = await self._build_album(media_group, media_source)
            await message.answer_media_group(media=album.build())

        except TelegramForbiddenError:
            logger.warning(f"User {message.from_user.id} blocked the bot.")

        except (TelegramBadRequest, MediaCacheError) as e:
            logger.debug(f"Failed to send media group {media_group}: {e}")
            for cache_key in cache_keys:
                await self.cache.remove(cache_key)

            file_paths = tuple(get_file_path(media) for media in media_group)
            files = (FSInputFile(file_path) for file_path in file_paths)

            album = await self._build_album(media_group, files)
            sent_messages = await message.answer_media_group(media=album.build())
            for cache_key, message, file_path in zip(cache_keys, sent_messages, file_paths):
                await self._safe_update_cache(
                    cache_key=cache_key,
                    message=message,
                    file_path=file_path,
                )

    @staticmethod
    def _create_keyboard(keyboard: Keyboard) -> ReplyKeyboardMarkup:
        rows = []
        for row in keyboard:
            buttons = [KeyboardButton(text=btn.text) for btn in row]
            rows.append(buttons)
        return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

    @staticmethod
    async def _build_album(
        media_group: MediaGroup,
        media_source: Iterable[str | FSInputFile],
    ) -> MediaGroupBuilder:
        album = MediaGroupBuilder()
        for media, source in zip(media_group, media_source):
            match media:
                case Photo():
                    album.add_photo(source, caption=media.description)
                case Video():
                    album.add_video(source, caption=media.description)
                case _:
                    raise ValueError(f"Unsupported media type: {type(media)}")

        return album

    async def _safe_update_cache(
        self,
        cache_key: CacheKey,
        message: Message,
        file_path: str | Path,
    ) -> None:
        if message.photo:
            new_file_id = message.photo[-1].file_id
        elif message.video:
            new_file_id = message.video.file_id
        else:
            logger.warning(f"No media found in message: {message}")
            return

        try:
            record = CacheRecord.from_file(file_id=new_file_id, file_path=file_path)
            await self.cache.add(cache_key, record)
        except Exception as e:
            logger.error(f"Failed to update cache for media: {e}")
