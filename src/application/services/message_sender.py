from abc import ABC, abstractmethod

from src.domain.aggregates import Content, PostGroup
from src.domain.ports.content_repository import ContentRepository
from src.domain.value_objects.keyboard import Keyboard
from src.domain.value_objects.media import MediaGroup, Photo, Text, Video
from src.domain.value_objects.node import NodeName


class MessageSender(ABC):
    def __init__(self, content_repository: ContentRepository):
        self.content_repository = content_repository

    async def send_content(self, message, content: Content) -> None:
        posts = content.posts if isinstance(content, PostGroup) else [content]
        for post in posts:
            media = post.media
            match media:
                case MediaGroup():
                    await self.send_media_group(message, post.media)
                case Text():
                    await self.send_text(message, post.media, post.keyboard)
                case Photo():
                    await self.send_photo(message, post.media, post.keyboard)
                case Video():
                    await self.send_video(message, post.media, post.keyboard)
                case _:
                    raise ValueError(f"Unsupported media type: {media}")

    async def send_error_message(self, message) -> None:
        content = self.content_repository.get_content(NodeName.ERROR)
        await self.send_content(message, content)

    @abstractmethod
    async def send_text(self, message, text: Text, reply_markup: Keyboard) -> None:
        pass

    @abstractmethod
    async def send_photo(self, message, photo: Photo, reply_markup: Keyboard) -> None:
        pass

    @abstractmethod
    async def send_video(self, message, video: Video, reply_markup: Keyboard) -> None:
        pass

    @abstractmethod
    async def send_media_group(self, message, media_group: MediaGroup) -> None:
        pass
