from pathlib import Path

import pytest
from ruamel.yaml import YAML

from src.config import settings
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.domain.value_objects.user_session import UserSession


@pytest.fixture
def root_dir() -> Path:
    return settings.test_data_dir


@pytest.fixture
def data_dir(root_dir) -> Path:
    return root_dir / "content" / "data"


@pytest.fixture
def get_test_data(data_dir):
    def _get(name: str):
        full_path = data_dir / name
        yaml = YAML(typ="safe")
        with full_path.open("r", encoding="utf-8") as f:
            return yaml.load(f)

    return _get


@pytest.fixture
def user_key():
    return UserKey(Network.TELEGRAM, "123")


@pytest.fixture
def session(user_key):
    return UserSession(user_key=user_key, root_node_id="main")
