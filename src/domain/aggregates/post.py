from typing import Mapping

from pydantic import BaseModel, Field, field_validator, model_validator

from ..entities import MediaContent, MediaItem
from ..entities.keyboard import Keyboard
from ..entities.media_group import MediaGroup
from ..factories import media_factory
from ..value_objects.post_flag import PostFlag


class Post(BaseModel):
    id: str = Field(...)
    media: MediaContent = Field(...)
    keyboard: Keyboard = Field(default_factory=Keyboard)
    flags: PostFlag = Field(default_factory=PostFlag)

    @field_validator("media", mode="before")
    @classmethod
    def media_validator(cls, values: list[Mapping] | MediaItem):
        if isinstance(values, MediaItem):
            return values

        is_media_group = len(values) > 1
        if not is_media_group:
            return media_factory(values[0])

        parsed_items = tuple(media_factory(item) for item in values)
        return MediaGroup(items=parsed_items)

    @model_validator(mode="after")
    def check_keyboard(self):
        if self.keyboard and isinstance(self.media, MediaGroup):
            raise ValueError("Post cannot have keyboard if there is MediaGroup")
        return self
