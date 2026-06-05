import pytest

from src.domain.entities.media import Photo, Text, Video
from src.domain.factories import media_factory


def test_media_factory_photo(get_test_data):
    json = get_test_data("media_photo.yaml")
    media = media_factory(json)
    assert isinstance(media, Photo)
    assert media.local_path == "some_photo.jpg"
    assert media.description == "real photo"


def test_media_factory_text(get_test_data):
    json = get_test_data("media_text.yaml")
    media = media_factory(json)
    assert isinstance(media, Text)
    assert media.text == "Hello world"


def test_media_factory_video(get_test_data):
    json = get_test_data("media_video.yaml")
    media = media_factory(json)
    assert isinstance(media, Video)
    assert media.local_path == "some_video.mp4"
    assert media.description == "real video"


def test_media_factory_invalid(get_test_data):
    json = get_test_data("media_invalid.yaml")
    with pytest.raises(ValueError) as e:
        media_factory(json)

    assert str(e.value) == "'image' is not a valid NodeKind"
