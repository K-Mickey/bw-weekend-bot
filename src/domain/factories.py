from typing import Mapping

from .aggregates import Content, Post, PostGroup
from .value_objects.media import Photo, Text, Video
from .value_objects.node import NodeKind


def content_factory(raw: Mapping) -> Content | Text | Photo | Video:
    kind = NodeKind(raw["type"])
    match kind:
        case NodeKind.PHOTO:
            return Photo(**raw)
        case NodeKind.VIDEO:
            return Video(**raw)
        case NodeKind.TEXT:
            return Text(**raw)
        case NodeKind.POST:
            return Post(**raw)
        case NodeKind.POST_GROUP:
            return PostGroup(**raw)
