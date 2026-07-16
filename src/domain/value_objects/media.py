from __future__ import annotations

import re
from typing import Iterator, Literal, TypeAlias

from pydantic import BaseModel, Field, field_validator

from src.domain.exceptions import TooLongFieldError, VideoValidationError


class MediaGroup(BaseModel):
    items: tuple[MediaType, ...] = Field(...)

    def __iter__(self) -> Iterator[MediaType]:
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return f"MediaGroup({self.items})"

    def __getitem__(self, index: int) -> MediaType:
        return self.items[index]


class Text(BaseModel):
    type: Literal["text"] = "text"
    text: str = Field(...)

    def __repr__(self):
        return f"Text({self.text})"

    @field_validator("text")
    @classmethod
    def check_max_length(cls, v: str) -> str:
        if len(v) > 4096:
            raise TooLongFieldError("Text length must not exceed 4096 characters")
        return v


class Photo(BaseModel):
    type: Literal["photo"] = "photo"
    local_path: str = Field(...)
    description: str | None = None

    def __repr__(self):
        return f"Photo({self.local_path}, {self.description})"

    def __hash__(self):
        return hash((self.local_path, self.description))

    @field_validator("description")
    @classmethod
    def check_description_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 1024:
            raise TooLongFieldError("Description length must not exceed 1024 characters")
        return v


class Video(BaseModel):
    type: Literal["video"] = "video"
    vk_url: str = Field(default="")
    local_path: str = Field(...)
    description: str | None = None

    def __repr__(self):
        return f"Video({self.local_path}, {self.description})"

    def __hash__(self):
        return hash((self.local_path, self.description))

    @field_validator("description")
    @classmethod
    def check_description_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 1024:
            raise TooLongFieldError("Description length must not exceed 1024 characters")
        return v

    @field_validator("vk_url")
    @classmethod
    def check_vk_url(cls, v: str) -> str:
        if not v:
            return v

        correct_urls = ("https://vkvideo.ru", "https://vk.com", "https://vk.ru")
        if not any(v.startswith(url) for url in correct_urls):
            raise VideoValidationError(f"vk_url must start with one of {correct_urls}")
        return v

    @property
    def vk_video_id(self) -> str:
        pattern = r"(?:video|clip)(-?\d+)_(\d+)"
        match = re.search(pattern, self.vk_url)
        if match:
            return match.group(0)
        else:
            raise VideoValidationError("Не удалось извлечь ID видео из ссылки")


MediaType: TypeAlias = Photo | Video
