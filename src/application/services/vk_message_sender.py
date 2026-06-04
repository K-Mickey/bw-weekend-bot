import logging
from pathlib import Path

from vkbottle import Bot, PhotoMessageUploader, VideoUploader, VKAPIError
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
        self.video_uploader = VideoUploader(bot.api)

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
            logger.debug(f"Failed to send photo {photo.url}: {e}")
            await self.cache.remove(cache_key)

            file_path = str(get_file_path(photo))
            attachment = await self.photo_uploader.upload(
                file_source=file_path,
                peer_id=message.peer_id,
            )
            await self._safe_update_cache(
                cache_key=cache_key,
                attachment=attachment,
                file_path=file_path,
            )

            await message.answer(
                attachment=attachment,
                message=photo.description,
                keyboard=keyboard_markup,
            )

    async def send_video(self, message: Message, video: Video, reply_markup: Keyboard) -> None:
        cache_key = CacheKey.create(video, Network.VK)
        keyboard_markup = self._create_keyboard(reply_markup)
        try:
            cache_record = await self.cache.get(cache_key)
            await message.answer(
                attachment=cache_record.file_id,
                message=video.description,
                keyboard=keyboard_markup,
            )

        except (VKAPIError, MediaCacheError) as e:
            logger.debug(f"Failed to send video {video.url}: {e}")
            await self.cache.remove(cache_key)

            logger.warning(f"Video {video.url} is not supported")
            # file_path = str(get_file_path(video))
            # attachment = await self.video_uploader.upload(
            #     file_source=file_path,
            #     description=video.description,
            # )
            # await self._safe_update_cache(
            #     cache_key=cache_key,
            #     attachment=attachment,
            #     file_path=file_path,
            # )
            #
            # await message.answer(
            #     attachment=attachment,
            #     message=video.description,
            #     keyboard=keyboard_markup,
            # )

    async def send_media_group(self, message: Message, media_group: MediaGroup) -> None:
        cache_keys = tuple(CacheKey.create(node, Network.VK) for node in media_group)
        try:
            cache_records = await self.cache.get_many(cache_keys)
            attachment = ",".join(record.file_id for record in cache_records.values())
            await message.answer(attachment=attachment)

        except (VKAPIError, MediaCacheError) as e:
            logger.debug(f"Failed to send media group: {e}")
            for cache_key in cache_keys:
                await self.cache.remove(cache_key)

            logger.debug("Uploading media group...")
            attachments = []
            for media, cache_key in zip(media_group, cache_keys):
                file_path = str(get_file_path(media))

                match media:
                    case Photo():
                        attachment = await self.photo_uploader.upload(
                            file_source=file_path,
                            peer_id=message.peer_id,
                        )
                        logger.debug(f"Photo {media.url} uploaded")
                        await self._safe_update_cache(
                            cache_key=cache_key,
                            attachment=attachment,
                            file_path=file_path,
                        )
                        attachments.append(attachment)

                    case Video():
                        logger.warning(f"Video {media.url} is not supported")
                    case _:
                        raise ValueError(f"Unsupported media type: {media}")

            attachment = ",".join(attachments)
            logger.debug(f"Media group {attachment} uploaded")
            await message.answer(attachment=attachment)

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
