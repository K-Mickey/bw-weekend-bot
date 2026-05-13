from datetime import datetime
from enum import StrEnum
from typing import List, Mapping, TypeAlias

from pydantic import BaseModel, Field


class NodeKind(StrEnum):
    POST = "post"
    PHOTO = "photo"
    VIDEO = "video"
    TEXT = "text"


class KeyboardButton(BaseModel):
    text: str = Field(...)
    target: str = Field(...)


class PhotoNode(BaseModel):
    url: str = Field(...)
    description: str | None = None


class VideoNode(BaseModel):
    url: str = Field(...)
    description: str | None = None


class TextNode(BaseModel):
    text: str = Field(...)


MediaItem: TypeAlias = PhotoNode | VideoNode | TextNode


class PostNode(BaseModel):
    id: str = Field(...)
    keyboard: List[List[KeyboardButton]] | None = None
    media: List[MediaItem] | None = None
    available_from: datetime | None = None
    available_to: datetime | None = None
    flags: List[str] | None = None


def node_factory(raw: Mapping) -> BaseModel:
    kind = NodeKind(raw["type"])
    match kind:
        case NodeKind.POST:
            return PostNode(**raw)
        case NodeKind.PHOTO:
            return PhotoNode(**raw)
        case NodeKind.VIDEO:
            return VideoNode(**raw)
        case NodeKind.TEXT:
            return TextNode(**raw)
        case _:
            raise ValueError(f"Unsupported node type: {raw.get('type')}")
