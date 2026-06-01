from abc import ABC, abstractmethod

from src.domain.entities import MediaGroup
from src.domain.entities.keyboard import Keyboard
from src.domain.entities.media import Photo, Text, Video


class BaseAdapter(ABC):
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
