from datetime import datetime
from typing import Mapping, TypeAlias

from pydantic import BaseModel, Field, field_validator, model_validator

from ..entities.media.photo_node import PhotoNode
from ..entities.media.text_node import TextNode
from ..entities.media.video_node import VideoNode
from ..entities.node_kind import NodeKind

# Local alias for the union of media entity types
MediaItem: TypeAlias = PhotoNode | VideoNode | TextNode


class PostNode(BaseModel):
    id: str = Field(...)
    media: list[MediaItem] = Field(...)
    available_from: datetime | None = None
    available_to: datetime | None = None
    flags: list[str] | None = None

    @model_validator(mode="after")
    def check_dates(self):
        if self.available_to and self.available_from and self.available_to <= self.available_from:
            raise ValueError("available_to must be greater than available_from")
        return self

    @classmethod
    def _parse_media_item(cls, raw: Mapping) -> MediaItem:
        kind = NodeKind(raw["type"])
        match kind:
            case NodeKind.PHOTO:
                return PhotoNode(**raw)
            case NodeKind.VIDEO:
                return VideoNode(**raw)
            case NodeKind.TEXT:
                return TextNode(**raw)
            case _:
                raise ValueError(f"Unsupported media type: {kind}")

    @classmethod
    def _parse_media_list(cls, raw_list: list[Mapping] | None) -> list[MediaItem]:
        if not raw_list:
            return []
        return [cls._parse_media_item(item) for item in raw_list]

    @field_validator("media", mode="before")
    @classmethod
    def media_validator(cls, v: list[Mapping] | None):
        if not v:
            return []
        parsed = cls._parse_media_list(v)
        has_text = any(isinstance(item, TextNode) for item in parsed)
        has_media = any(isinstance(item, (PhotoNode, VideoNode)) for item in parsed)
        if has_text and has_media:
            raise ValueError("PostNode cannot contain TextNode together with PhotoNode or VideoNode")
        return parsed
