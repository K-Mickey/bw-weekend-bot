from abc import ABC, abstractmethod
from pathlib import Path

from src.domain.aggregates import Content
from src.domain.value_objects.media import MediaType


class ContentRepository(ABC):
    @abstractmethod
    def get_content(self, file_name: Path | str) -> Content:
        raise NotImplementedError

    @abstractmethod
    def get_content_path(self, file_name: Path | str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def get_media_path(self, media_item: MediaType) -> Path:
        raise NotImplementedError
