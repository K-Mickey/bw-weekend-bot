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
    return settings.test_data_dir


@pytest.fixture
def data_dir(root_dir) -> Path:
    return root_dir / "content" / "data"


@pytest.fixture
def photo_dir(root_dir) -> Path:
    return root_dir / "content" / "photo"


@pytest.fixture
def video_dir(root_dir) -> Path:
    return root_dir / "content" / "video"


@pytest.fixture
def get_test_data(data_dir):
    def _get(name: str):
        full_path = data_dir / name
        yaml = YAML(typ="safe")
        with full_path.open("r", encoding="utf-8") as f:
            return yaml.load(f)

    return _get


@pytest.fixture
def get_content(data_dir):
    def _get(name: str):
        full_path = data_dir / name
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
