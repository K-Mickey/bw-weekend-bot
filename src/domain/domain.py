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

    @field_validator("text")
    @classmethod
    def truncate_long_text(cls, v: str) -> str:
        if len(v) > 35:
            return f"{v[:32]}..."
        return v


class PhotoNode(BaseModel):
    url: str = Field(...)
    description: str | None = None

    @field_validator("description")
    @classmethod
    def check_description_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 1024:
            raise ValueError("description length must not exceed 1024 characters")
        return v


class VideoNode(BaseModel):
    url: str = Field(...)
    description: str | None = None

    @field_validator("description")
    @classmethod
    def check_description_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 1024:
            raise ValueError("description length must not exceed 1024 characters")
        return v


class TextNode(BaseModel):
    text: str = Field(...)

    @field_validator("text")
    @classmethod
    def check_max_length(cls, v: str) -> str:
        if len(v) > 4096:
            raise ValueError("text length must not exceed 4096 characters")
        return v


MediaItem: TypeAlias = PhotoNode | VideoNode | TextNode


class PostNode(BaseModel):
    id: str = Field(...)
    media: list[MediaItem] = Field(...)
    available_from: datetime | None = None
    available_to: datetime | None = None
    flags: list[str] | None = None

    @field_validator("available_to")
    @classmethod
    def check_dates(cls, v: datetime | None, values):
        from_date = values.get("available_from")
        if v and from_date and v <= from_date:
            raise ValueError("available_to must be greater than available_from")
        return v

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


class MenuNodeFlags(BaseModel):
    is_back: bool = True
    is_main: bool = True
    build: bool = True


class MenuNode(BaseModel):
    id: str = Field(...)
    content: list[PostNode] = Field(...)
    keyboard: list[list[KeyboardButton]] = Field(default_factory=list)
    flags: MenuNodeFlags = Field(default_factory=MenuNodeFlags)


def node_factory(raw: dict) -> BaseModel:
    match raw:
        case {"keyboard": _}:
            return MenuNode(**raw)
        case {"media": _}:
            return PostNode(**raw)
        case _:
            raise ValueError("Invalid node")
