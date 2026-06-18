import pytest

from src.domain.aggregates import Post, PostGroup
from src.domain.factories import content_factory
from src.domain.value_objects.button import ButtonType
from src.domain.value_objects.media import Photo, Text, Video


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
    with pytest.raises(ValueError):
        content_factory(json)


def test_media_factory_photo(get_test_data):
    json = get_test_data("media_photo.yaml")
    media = content_factory(json)
    assert isinstance(media, Photo)
    assert media.local_path == "some_photo.jpg"
    assert media.description == "real photo"


def test_media_factory_text(get_test_data):
    json = get_test_data("media_text.yaml")
    media = content_factory(json)
    assert isinstance(media, Text)
    assert media.text == "Hello world"


def test_media_factory_video(get_test_data):
    json = get_test_data("media_video.yaml")
    media = content_factory(json)
    assert isinstance(media, Video)
    assert media.local_path == "some_video.mp4"
    assert media.description == "real video"


def test_media_factory_invalid(get_test_data):
    json = get_test_data("media_invalid.yaml")
    with pytest.raises(ValueError) as e:
        content_factory(json)

    assert str(e.value) == "'image' is not a valid NodeKind"
