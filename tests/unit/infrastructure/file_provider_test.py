import pytest

from src.config import settings
from src.domain.entities.media import Photo, Video
from src.infrastructure.file_provider import FileNotFound, FileProviderError, get_file_path


class DummyMedia:
    def __init__(self, url: str):
        self.url = url


def test_get_photo_success():
    media = Photo(local_path="exist.jpg")
    result = get_file_path(media)
    assert result == settings.content_photo_dir / "exist.jpg"


def test_get_video_success():
    media = Video(local_path="exist.mp4")
    result = get_file_path(media)
    assert result == settings.content_video_dir / "exist.mp4"


def test_get_unsupported_media():
    media = DummyMedia(url="nonexistent.txt")
    with pytest.raises(FileProviderError):
        get_file_path(media)


@pytest.mark.asyncio
async def test_get_file_not_found():
    media = Photo(local_path="non_exist.jpg")
    with pytest.raises(FileNotFound):
        get_file_path(media)
