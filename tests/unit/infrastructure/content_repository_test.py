from datetime import datetime

import pytest

from src.domain.aggregates import MenuNode, PostNode
from src.domain.entities.keyboard_button import KeyboardButton
from src.domain.entities.media.text_node import TextNode
from src.domain.value_objects.menu_node_flags import MenuNodeFlags
from src.infrastructure.content_repository import ContentRepository


@pytest.fixture
def patch_dir(data_dir):
    from src.config import settings

    original_dir = settings.content_data_dir
    settings.content_data_dir = settings.base_dir / data_dir

    yield

    settings.content_data_dir = original_dir


def test_content_repository_get_existing_node(patch_dir):
    node = ContentRepository.get_node("menu_ok")
    assert isinstance(node, MenuNode)


def test_content_repository_get_nonexistent_node(patch_dir):
    node = ContentRepository.get_node("nonexistent_node_id")
    assert node is None


def test_content_repository_context(patch_dir):
    node = ContentRepository.get_node("menu_ok")

    content = node.content[0]
    assert isinstance(content, PostNode)
    assert content.available_from == datetime(2025, 1, 1, 0, 0)
    assert content.available_to == datetime(2025, 12, 31, 0, 0)

    media = content.media[0]
    assert isinstance(media, TextNode)
    assert media.text == "Hello world"

    assert node.keyboard == [
        [KeyboardButton(text="settings", target="menu_settings")],
        [KeyboardButton(text="help", target="menu_help")],
    ]

    assert node.flags == MenuNodeFlags(
        is_back=False,
        is_main=True,
        build=True,
    )
