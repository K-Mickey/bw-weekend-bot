import pytest

from src.domain.aggregates import MenuNode, PostNode
from src.domain.entities.keyboard import Keyboard, KeyboardButton, KeyboardRow
from src.domain.entities.media.text_node import TextNode
from src.domain.value_objects.menu_node_flags import PostNodeFlags
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

    media = content.media[0]
    assert isinstance(media, TextNode)
    assert media.text == "Hello world"

    assert content.keyboard == Keyboard(
        rows=[
            KeyboardRow(buttons=[KeyboardButton(text="settings", target="menu_settings")]),
            KeyboardRow(buttons=[KeyboardButton(text="help", target="menu_help")]),
        ]
    )

    assert content.flags == PostNodeFlags(
        is_back=False,
        is_main=True,
        build=True,
    )
