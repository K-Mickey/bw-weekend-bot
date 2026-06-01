import logging
from typing import Iterable

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import (
    FSInputFile,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.media_group import MediaGroupBuilder

from src.application.adapters.base import BaseAdapter
from src.domain.entities import MediaGroup
from src.domain.entities.keyboard import Keyboard
from src.domain.entities.media import MediaType, Photo, Text, Video
from src.domain.value_objects.network import Network
from src.infrastructure.file_cache import MediaCache
from src.infrastructure.file_cache.exceptions import MediaCacheError
from src.infrastructure.file_cache.value_objects.cache_key import CacheKey
from src.infrastructure.file_cache.value_objects.cache_record import CacheRecord
from src.infrastructure.file_provider import get_file_path

logger = logging.getLogger(__name__)


class TelegramAdapter(BaseAdapter):
    def __init__(self, bot: Bot, cache: MediaCache):
        self.bot = bot
        self.cache = cache

    async def send_text(self, recipient_id: int | str, text: Text, reply_markup: Keyboard) -> None:
        try:
            keyboard_markup = self._create_keyboard(reply_markup)
            await self.bot.send_message(chat_id=recipient_id, text=text.text, reply_markup=keyboard_markup)
        except TelegramForbiddenError:
            logger.warning(f"User {recipient_id} blocked the bot.")
        except Exception as e:
            logger.error(f"Error sending text to {recipient_id}: {e}")
            raise

    async def send_photo(self, recipient_id: int | str, photo: Photo, reply_markup: Keyboard) -> None:
        try:
            keyboard_markup = self._create_keyboard(reply_markup)
            media_source, is_from_cache = await self._get_media_source(photo)

            sent_message = await self.bot.send_photo(
                chat_id=recipient_id,
                photo=media_source,
                caption=photo.description,
                reply_markup=keyboard_markup,
            )

            if not is_from_cache:
                await self._safe_update_cache(photo, sent_message)

        except TelegramForbiddenError:
            logger.warning(f"User {recipient_id} blocked the bot.")
        except TelegramBadRequest as e:
            logger.debug(f"Failed to send photo {photo.url}: {e}")
            # Очистка кеша и повторная попытка
            try:
                cache_key = CacheKey.create(photo, Network.TELEGRAM)
                await self.cache.remove(cache_key)
            except Exception as cache_e:
                logger.error(f"Failed to clear cache for photo {photo.url}: {cache_e}")

            # Повторная отправка уже гарантированно из файла
            try:
                keyboard_markup = self._create_keyboard(reply_markup)
                media_source, _ = await self._get_media_source(photo, from_cache=False)

                sent_message = await self.bot.send_photo(
                    chat_id=recipient_id,
                    photo=media_source,
                    caption=photo.description,
                    reply_markup=keyboard_markup,
                )
                await self._safe_update_cache(photo, sent_message)
            except Exception as retry_e:
                logger.error(f"Failed to send photo {photo.url} on retry: {retry_e}")
                raise
        except Exception as e:
            logger.error(f"Error sending photo {photo.url} to {recipient_id}: {e}")
            raise

    async def send_video(self, recipient_id: int | str, video: Video, reply_markup: Keyboard) -> None:
        """Отправляет видео через Telegram с кэшированием."""
        try:
            keyboard_markup = self._create_keyboard(reply_markup)
            media_source, is_from_cache = await self._get_media_source(video)

            sent_message = await self.bot.send_video(
                chat_id=recipient_id,
                video=media_source,
                caption=video.description,
                reply_markup=keyboard_markup,
            )

            if not is_from_cache:
                await self._safe_update_cache(video, sent_message)

        except TelegramForbiddenError:
            logger.warning(f"User {recipient_id} blocked the bot.")
        except TelegramBadRequest as e:
            logger.debug(f"Failed to send video {video.url}: {e}")
            # Очистка кеша и повторная попытка
            try:
                cache_key = CacheKey.create(video, Network.TELEGRAM)
                await self.cache.remove(cache_key)
            except Exception as cache_e:
                logger.error(f"Failed to clear cache for video {video.url}: {cache_e}")

            # Повторная отправка уже гарантированно из файла
            try:
                keyboard_markup = self._create_keyboard(reply_markup) if reply_markup else None
                media_source, _ = await self._get_media_source(video, from_cache=False)

                sent_message = await self.bot.send_video(
                    chat_id=recipient_id,
                    video=media_source,
                    caption=video.description,
                    reply_markup=keyboard_markup,
                )
                await self._safe_update_cache(video, sent_message)
            except Exception as retry_e:
                logger.error(f"Failed to send video {video.url} on retry: {retry_e}")
                raise
        except Exception as e:
            logger.error(f"Error sending video {video.url} to {recipient_id}: {e}")
            raise

    async def send_media_group(self, recipient_id: int | str, media_group: MediaGroup) -> None:
        """Отправляет группу медиа через Telegram с кэшированием."""
        try:
            album, is_from_cache = await self._build_album(media_group, from_cache=True)
            try:
                sent_messages = await self.bot.send_media_group(chat_id=recipient_id, media=album.build())
                if not is_from_cache:
                    await self._safe_update_cache(media_group, sent_messages)
            except TelegramBadRequest:
                # Очистка кеша и повторная попытка
                for node in media_group:
                    try:
                        cache_key = CacheKey.create(node, Network.TELEGRAM)
                        await self.cache.remove(cache_key)
                    except Exception as cache_e:
                        logger.error(f"Failed to clear cache for {node.__class__.__name__}: {cache_e}")

                album, _ = await self._build_album(media_group, from_cache=False)
                sent_messages = await self.bot.send_media_group(chat_id=recipient_id, media=album.build())
                await self._safe_update_cache(media_group, sent_messages)
        except TelegramForbiddenError:
            logger.warning(f"User {recipient_id} blocked the bot.")
        except Exception as e:
            logger.error(f"Error sending media group to {recipient_id}: {e}")
            raise

    @staticmethod
    def _create_keyboard(keyboard: Keyboard) -> ReplyKeyboardMarkup:
        rows = []
        for row in keyboard:
            buttons = [KeyboardButton(text=btn.text) for btn in row]
            rows.append(buttons)
        return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

    async def _get_media_source(self, media: MediaType, from_cache: bool = True) -> tuple[str | FSInputFile, bool]:
        cache_key = CacheKey.create(media, Network.TELEGRAM)
        if from_cache:
            try:
                cache_record = await self.cache.get(cache_key)
                return cache_record.file_id, True
            except MediaCacheError as e:
                logger.debug(e)

        file_path = get_file_path(media)
        return FSInputFile(file_path), False

    async def _build_album(
        self,
        media: MediaGroup,
        from_cache: bool = False,
    ) -> tuple[MediaGroupBuilder, bool]:
        """
        :return: (album_builder, is_from_cache) where is_from_cache indicates if any media was taken from cache
        """
        album = MediaGroupBuilder()
        is_from_cache = False
        for node in media:
            media_source, current_from_cache = await self._get_media_source(node, from_cache)
            is_from_cache = is_from_cache or current_from_cache

            match node:
                case Photo():
                    album.add_photo(media_source, caption=node.description)
                case Video():
                    album.add_video(media_source, caption=node.description)
                case _:
                    raise ValueError(f"Unsupported media type: {node}")

        return album, is_from_cache

    async def _safe_update_cache(
        self,
        media: MediaType | Iterable[MediaType],
        message: Message | Iterable[Message],
    ) -> None:
        media_list = media if isinstance(media, list) else [media]
        message_list = message if isinstance(message, list) else [message]
        try:
            await self._update_cache_from_messages(media_list, message_list)
        except Exception as e:
            logger.error(f"Failed to update cache for media: {e}")

    async def _update_cache_from_messages(
        self,
        media: Iterable[MediaType],
        messages: Iterable[Message],
    ) -> None:

        for message, node in zip(messages, media):
            cache_key = CacheKey.create(node, Network.TELEGRAM)

            if message.photo:
                new_file_id = message.photo[-1].file_id
            elif message.video:
                new_file_id = message.video.file_id
            else:
                logger.warning(f"No media found in message: {message}")
                continue

            record = CacheRecord.from_file(file_id=new_file_id, file_path=get_file_path(node))
            await self.cache.add(cache_key, record)
