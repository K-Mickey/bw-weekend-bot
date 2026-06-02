from abc import ABC, abstractmethod

from src.application.usecases.get_content import get_content_by_id
from src.domain.aggregates import Content, PostGroup
from src.domain.entities import MediaGroup
from src.domain.entities.keyboard import Keyboard
from src.domain.entities.media import Photo, Text, Video
from src.domain.value_objects.node import NodeName


class MessageSender(ABC):
    async def send_content(self, recipient_id: int | str, content: Content) -> None:
        posts = content.posts if isinstance(content, PostGroup) else [content]
        for post in posts:
            media = post.media
            match media:
                case MediaGroup():
                    await self.send_media_group(recipient_id, post.media)
                case Text():
                    await self.send_text(recipient_id, post.media, post.keyboard)
                case Photo():
                    await self.send_photo(recipient_id, post.media, post.keyboard)
                case Video():
                    await self.send_video(recipient_id, post.media, post.keyboard)
                case _:
                    raise ValueError(f"Unsupported media type: {media}")

    async def send_error_message(self, recipient_id: int | str) -> None:
        content = get_content_by_id(NodeName.ERROR)
        await self.send_content(recipient_id, content)

    @abstractmethod
    async def send_text(self, recipient_id: int | str, text: Text, reply_markup: Keyboard) -> None:
        pass

    @abstractmethod
    async def send_photo(self, recipient_id: int | str, photo: Photo, reply_markup: Keyboard) -> None:
        pass

    @abstractmethod
    async def send_video(self, recipient_id: int | str, video: Video, reply_markup: Keyboard) -> None:
        pass

    @abstractmethod
    async def send_media_group(self, recipient_id: int | str, media_group: MediaGroup) -> None:
        pass
