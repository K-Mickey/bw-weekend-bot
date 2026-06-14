import pytest

from src.domain.aggregates import Post, PostGroup
from src.domain.exceptions import NotSupportedTypeError
from src.domain.factories import content_factory
from src.domain.value_objects.button import ButtonType
from src.domain.value_objects.media import Text


def test_content_factory_with_post(get_test_data):
    json = get_test_data("post_main.yaml")
    post = content_factory(json)
    assert isinstance(post, Post)
    assert isinstance(post.media, Text)
    assert post.media.text == "Hello world"
    assert post.keyboard[0].buttons
    button = post.keyboard[0].buttons[0]
    assert button.text == "Main"
    assert button.target == "main"
    assert button.type == ButtonType.MAIN_MENU


def test_content_factory_with_group_posts(get_test_data):
    json = get_test_data("menu_ok.yaml")
    post_group = content_factory(json)
    assert isinstance(post_group, PostGroup)
    assert len(post_group.posts) == 1
    assert post_group.posts[0].id == "post_ok"


def test_content_factory_with_invalid_post(get_test_data):
    json = get_test_data("post_invalid_fields.yaml")
    with pytest.raises(NotSupportedTypeError):
        content_factory(json)
