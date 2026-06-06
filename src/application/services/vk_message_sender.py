import asyncio
import logging
from json import JSONDecodeError
from pathlib import Path

from vkbottle import Bot, PhotoMessageUploader, VKAPIError
from vkbottle import Keyboard as VKKeyboard
from vkbottle import Text as VKText
from vkbottle.bot import Message

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


class VKMessageSender(MessageSender):
    def __init__(self, bot: Bot, cache: MediaCache):
        self.bot = bot
        self.cache = cache
        self.photo_uploader = PhotoMessageUploader(bot.api)

    async def send_text(self, message: Message, text: Text, reply_markup: Keyboard) -> None:
        keyboard_markup = self._create_keyboard(reply_markup)
        await message.answer(text.text, keyboard=keyboard_markup)

    async def send_photo(self, message: Message, photo: Photo, reply_markup: Keyboard) -> None:
        cache_key = CacheKey.create(photo, Network.VK)
        keyboard_markup = self._create_keyboard(reply_markup)
        try:
            cache_record = await self.cache.get(cache_key)
            await message.answer(
                attachment=cache_record.file_id,
                message=photo.description,
                keyboard=keyboard_markup,
            )

        except (VKAPIError, MediaCacheError) as e:
            logger.debug(f"Failed to send photo {photo.local_path}: {e}")
            attachment = await self._update_photo_from_local(
                photo=photo,
                cache_key=cache_key,
                peer_id=message.peer_id,
            )

            await message.answer(
                attachment=attachment,
                message=photo.description,
                keyboard=keyboard_markup,
            )

    async def send_video(self, message: Message, video: Video, reply_markup: Keyboard) -> None:
        keyboard_markup = self._create_keyboard(reply_markup)
        await message.answer(
            attachment=video.vk_video_id,
            message=video.description,
            keyboard=keyboard_markup,
        )

    async def send_media_group(self, message: Message, media_group: MediaGroup) -> None:
        photos = filter(lambda x: isinstance(x, Photo), media_group)
        cache_keys = {photo: CacheKey.create(photo, Network.VK) for photo in photos}
        try:
            cache_records = await self.cache.get_many(cache_keys.values())
            attachments = []
            for media in media_group:
                match media:
                    case Photo():
                        key = cache_keys[media]
                        record = cache_records[key]
                        attachments.append(record.file_id)
                    case Video():
                        attachments.append(media.vk_video_id)

            attachment = ",".join(attachments)
            await message.answer(attachment=attachment)

        except (VKAPIError, MediaCacheError) as e:
            logger.debug(f"Failed to send media group: {e}")

            logger.debug("Uploading media group...")
            attachments = []
            for media in media_group:
                match media:
                    case Photo():
                        cache_key = cache_keys.get(media)
                        attachment = await self._update_photo_from_local(
                            photo=media,
                            cache_key=cache_key,
                            peer_id=message.peer_id,
                        )

                    case Video():
                        attachment = media.vk_video_id
                        logger.debug(f"Video id extracted: {attachment}")

                    case _:
                        raise ValueError(f"Unsupported media type: {type(media)}")

                attachments.append(attachment)

            attachment = ",".join(attachments)
            logger.debug(f"Media group {attachment} uploaded")
            await message.answer(attachment=attachment)

    async def _update_photo_from_local(self, photo: Photo, cache_key: CacheKey, peer_id: int) -> str:
        await self.cache.remove(cache_key)

        file_path = str(get_file_path(photo))
        retries = 3
        for retry in range(retries):
            try:
                attachment = await self.photo_uploader.upload(
                    file_source=file_path,
                    peer_id=peer_id,
                )
                break
            except JSONDecodeError:
                logger.debug(f"Unexpected JSON response from VK API; retry {retry + 1} of {retries}")
                if retry == retries - 1:
                    raise

                await asyncio.sleep(1)

        logger.debug(f"Photo {photo.local_path} uploaded")
        logger.debug(f"Attachment: {attachment}")
        await self._safe_update_cache(
            cache_key=cache_key,
            attachment=attachment,
            file_path=file_path,
        )

        return attachment

    @staticmethod
    def _create_keyboard(keyboard: Keyboard) -> VKKeyboard:
        vk_keyboard = VKKeyboard()
        for row in keyboard:
            for button in row:
                vk_keyboard.add(VKText(button.text))
            vk_keyboard.row()
        return vk_keyboard

    async def _safe_update_cache(
        self,
        cache_key: CacheKey,
        attachment: str,
        file_path: str | Path,
    ) -> None:
        try:
            record = CacheRecord.from_file(file_id=attachment, file_path=file_path)
            await self.cache.add(cache_key, record)
        except Exception as e:
            logger.error(f"Failed to update cache for media: {e}")
