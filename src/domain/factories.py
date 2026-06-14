from typing import Mapping

from .aggregates import Post, PostGroup
from .exceptions import NotSupportedTypeError
from .value_objects.media import DataItem, Photo, Text, Video
from .value_objects.node import NodeKind


def content_factory(raw: dict):
    match raw:
        case {"posts": _}:
            return PostGroup(**raw)
        case {"media": _}:
            return Post(**raw)
        case _:
            raise NotSupportedTypeError(str(raw))


def media_factory(raw: Mapping) -> DataItem:
    kind = NodeKind(raw["type"])
    match kind:
        case NodeKind.PHOTO:
            return Photo(**raw)
        case NodeKind.VIDEO:
            return Video(**raw)
        case NodeKind.TEXT:
            return Text(**raw)
