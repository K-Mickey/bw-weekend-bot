from pathlib import Path

import pytest

from src.domain.aggregates import Content
from src.domain.exceptions import ContentNotFoundError, MediaNotFoundError
from src.domain.value_objects.media import MediaType, Photo, Video
from src.infrastructure.content_repository import LocalContentRepository


@pytest.fixture
def content_repository():
    return LocalContentRepository()


def test_content_repository_get_content(content_repository: LocalContentRepository):
    content = content_repository.get_content("main.yaml")
    assert isinstance(content, Content)


@pytest.mark.parametrize("file_name", ("main.yaml", "main", Path("main.yaml"), Path("main")))
def test_content_repository_get_content_path(content_repository: LocalContentRepository, file_name: Path | str):
    path = content_repository.get_content_path(file_name)
    assert path.exists()


def test_content_repository_nonexistent_content_path(content_repository: LocalContentRepository):
    with pytest.raises(ContentNotFoundError):
        content_repository.get_content_path("nonexistent_content.yaml")


@pytest.mark.parametrize("media", (Photo(local_path="exist.jpg"), Video(local_path="exist.mp4")))
def test_content_repository_get_media_path(content_repository: LocalContentRepository, media: MediaType):
    media_path = content_repository.get_media_path(media)
    assert media_path.exists()


def test_content_repository_get_media_path_not_found(content_repository: LocalContentRepository):
    media = Photo(local_path="non_exist.jpg")
    with pytest.raises(MediaNotFoundError):
        content_repository.get_media_path(media)
