from abc import ABC, abstractmethod

from src.domain.entities import MediaGroup
from src.domain.entities.keyboard import Keyboard
from src.domain.entities.media import Photo, Text, Video


class BaseAdapter(ABC):
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
