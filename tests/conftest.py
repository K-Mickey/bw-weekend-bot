from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.types import Message as TgMessage
from ruamel.yaml import YAML
from vkbottle.bot import Message as VkMessage

from src.config import settings
from src.domain.aggregates import Post, PostGroup
from src.domain.factories import content_factory
from src.domain.ports import StateStore
from src.domain.ports.content_repository import ContentRepository
from src.domain.value_objects.media import MediaGroup, Photo, Text, Video
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.content_repository import LocalContentRepository
from src.infrastructure.state_store import MemoryStateStore


@pytest.fixture
def root_dir() -> Path:
    return settings.base_dir / "tests" / "test_data"


@pytest.fixture(autouse=True)
def override_content_dirs(monkeypatch, root_dir):
    test_content_dir = root_dir / "content"
    monkeypatch.setattr(settings, "content_dir", test_content_dir)
    monkeypatch.setattr(settings, "content_data_dir", test_content_dir / "data")
    monkeypatch.setattr(settings, "content_photo_dir", test_content_dir / "photo")
    monkeypatch.setattr(settings, "content_video_dir", test_content_dir / "video")


@pytest.fixture
def get_test_data():
    def _get(name: str):
        full_path = settings.content_data_dir / name
        yaml = YAML(typ="safe")
        with full_path.open("r", encoding="utf-8") as f:
            return yaml.load(f)

    return _get


@pytest.fixture
def get_content():
    def _get(name: str):
        full_path = settings.content_data_dir / name
        yaml = YAML(typ="safe")
        file = full_path.read_text(encoding="utf-8")
        return content_factory(yaml.load(file))

    return _get


@pytest.fixture
def user_key() -> UserKey:
    return UserKey(Network.TELEGRAM, "123")


@pytest.fixture
def state_store() -> StateStore:
    return MemoryStateStore()


@pytest.fixture
def content_repository() -> ContentRepository:
    return LocalContentRepository()


@pytest.fixture
def post() -> Post:
    return Post(
        id="test",
        media=Text(text="description"),
    )


@pytest.fixture
def post_group() -> PostGroup:
    return PostGroup(id="test", posts=[])


@pytest.fixture
def photo() -> Photo:
    return Photo(local_path="exist.jpg", description="photo description")


@pytest.fixture
def video() -> Video:
    video = Video(
        local_path="exist.mp4",
        description="video description",
        vk_url="https://vk.com/video-1234_1234",
    )
    return video


@pytest.fixture
def media_group(photo, video) -> MediaGroup:
    return MediaGroup(items=(photo, video))


@pytest.fixture
def tg_message():
    message = Mock(spec=TgMessage)
    message.from_user = Mock()
    message.from_user.id = 123456789

    message.text = "test"

    photo_msg = Mock(spec=TgMessage)
    photo_msg.photo = [Mock(file_id="cached_photo_id")]
    photo_msg.video = None

    video_msg = Mock(spec=TgMessage)
    video_msg.video = Mock(file_id="cached_video_id")
    video_msg.photo = None

    message.answer = AsyncMock()
    message.answer_photo = AsyncMock(return_value=photo_msg)
    message.answer_video = AsyncMock(return_value=video_msg)

    message.answer_media_group = AsyncMock(return_value=[photo_msg, video_msg])

    return message


@pytest.fixture
def vk_message():
    message = Mock(spec=VkMessage)
    message.from_id = 123456789
    message.peer_id = 123456789
    message.text = "test"
    message.answer = AsyncMock()
    return message
