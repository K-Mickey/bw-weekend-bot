import logging
from pathlib import Path

import yaml

from src.config import settings
from src.domain.aggregates import Content
from src.domain.exceptions import ContentNotFoundError, MediaNotFoundError, NotSupportedTypeError
from src.domain.factories import content_factory
from src.domain.ports.content_repository import ContentRepository
from src.domain.value_objects.media import MediaType, Photo, Video

logger = logging.getLogger(__name__)


class LocalContentRepository(ContentRepository):
    def __init__(self):
        self.data_dir = settings.content_data_dir
        self.photo_dir = settings.content_photo_dir
        self.video_dir = settings.content_video_dir

    def get_content(self, file_name: Path | str) -> Content:
        file_path = self.get_content_path(file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            return content_factory(raw)
        except Exception as e:
            logger.exception(f"Failed to load content from {file_path}: {e}")
            raise

    def get_content_path(self, file_name: Path | str) -> Path:
        file_name = self.normalize_yaml_file_name(file_name)
        file_path = self.data_dir / file_name
        if not file_path.exists():
            raise ContentNotFoundError(file_name)
        return file_path

    def get_media_path(self, media_item: MediaType) -> Path:
        match media_item:
            case Photo():
                folder = self.photo_dir
            case Video():
                folder = self.video_dir
            case _:
                raise NotSupportedTypeError(media_item)

        file_path = folder / media_item.local_path
        if not file_path.is_file():
            raise MediaNotFoundError(file_path)
        return file_path

    @staticmethod
    def normalize_yaml_file_name(file_name: Path | str) -> Path:
        if not isinstance(file_name, Path):
            file_name = Path(file_name)
        if file_name.suffix != ".yaml":
            file_name = file_name.with_suffix(".yaml")
        return file_name
