from typing import Mapping

from pydantic import BaseModel, Field, field_validator, model_validator

from ..entities.keyboard import Keyboard
from ..entities.media import MediaItem
from ..entities.media.photo_node import PhotoNode
from ..entities.media.text_node import TextNode
from ..entities.media.video_node import VideoNode
from ..entities.node_kind import NodeKind
from ..value_objects.menu_node_flags import PostNodeFlags


class PostNode(BaseModel):
    id: str = Field(...)
    media: list[MediaItem] = Field(...)
    keyboard: Keyboard | list[list[dict]] = Field(default_factory=Keyboard)
    flags: PostNodeFlags = Field(default_factory=PostNodeFlags)

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

    @model_validator(mode="after")
    def check_keyboard(self) -> None:
        if self.keyboard and len(self.media) > 1:
            raise ValueError("PostNode cannot have keyboard if there is more than one media item")
        return self
