from pathlib import Path

from src.config import settings
from src.domain.entities.media import MediaItem, Photo, Video


class FileProviderError(RuntimeError):
    """Base error for all file‑provider related problems."""


class FileNotFound(FileProviderError):
    """Raised when the underlying file cannot be located."""


def get_file_path(media: MediaItem) -> Path:
    match media:
        case Photo():
            folder = settings.content_photo_dir
        case Video():
            folder = settings.content_video_dir
        case _:
            raise FileProviderError(f"Unsupported media type: {media}")

    file_path = folder / media.url
    if not file_path.is_file():
        raise FileNotFound(f"File not found: {file_path}")

    return file_path
