from datetime import datetime
from enum import StrEnum
from typing import Mapping, TypeAlias

from pydantic import BaseModel, Field, field_validator


class NodeKind(StrEnum):
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
    media: list[MediaItem] | None = None
    available_from: datetime | None = None
    available_to: datetime | None = None
    flags: list[str] | None = None

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
    def _parse_media_list(cls, raw_list: list[Mapping] | None) -> list[MediaItem] | None:
        if not raw_list:
            return None
        return [cls._parse_media_item(item) for item in raw_list]

    @field_validator("media", mode="before")
    @classmethod
    def validate_media(cls, v):
        return cls._parse_media_list(v)


class MenuNode(BaseModel):
    id: str = Field(...)
    content: PostNode = Field(...)
    keyboard: list[list[KeyboardButton]]
    flags: list[str] | None = None

    @field_validator("keyboard", mode="before")
    @classmethod
    def ensure_keyboard(cls, v):
        # Accept both list of list of dicts and already parsed KeyboardButton objects
        if not v:
            raise ValueError("keyboard must contain at least one row")
        # If inner items are dicts, pydantic will convert them automatically when returning
        return v


def node_factory(raw: Mapping) -> BaseModel:
    """Factory that decides which domain object to instantiate.
    - Presence of ``keyboard`` → MenuNode (expects a nested ``content`` dict).
    - Presence of ``media``   → PostNode.
    - Otherwise, treat as a media item (photo, video, text).
    """
    if "keyboard" in raw:
        # ``content`` will be parsed by pydantic as PostNode using its validators
        return MenuNode(**raw)
    if "media" in raw:
        return PostNode(**raw)
    # Media item case
    kind = NodeKind(raw["type"])
    match kind:
        case NodeKind.PHOTO:
            return PhotoNode(**raw)
        case NodeKind.VIDEO:
            return VideoNode(**raw)
        case NodeKind.TEXT:
            return TextNode(**raw)
        case _:
            raise ValueError(f"Unsupported node type: {kind}")
