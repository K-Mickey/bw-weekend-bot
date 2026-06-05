from typing import Mapping

from src.domain.entities.media import MediaItem, Photo, Text, Video
from src.domain.value_objects.node import NodeKind


def media_factory(raw: Mapping) -> MediaItem:
    kind = NodeKind(raw["type"])
    match kind:
        case NodeKind.PHOTO:
            return Photo(**raw)
        case NodeKind.VIDEO:
            return Video(**raw)
        case NodeKind.TEXT:
            return Text(**raw)
