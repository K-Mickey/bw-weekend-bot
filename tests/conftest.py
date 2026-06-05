from pathlib import Path

import pytest
from ruamel.yaml import YAML

from src.config import settings
from src.domain.aggregates import Post, PostGroup
from src.domain.entities.media import Text
from src.domain.entities.user_session import UserSession
from src.domain.factories import content_factory
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey


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
def session(user_key) -> UserSession:
    return UserSession(user_key=user_key, root_node_id="main")


@pytest.fixture
def post() -> Post:
    return Post(
        id="test",
        media=Text(text="description"),
    )


@pytest.fixture
def post_group() -> PostGroup:
    return PostGroup(id="test", posts=[])
