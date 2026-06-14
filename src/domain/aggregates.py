from typing import Mapping

from pydantic import BaseModel, Field, field_validator, model_validator

from src.domain.exceptions import NotSupportedKeyboardError
from src.domain.value_objects.keyboard import Keyboard
from src.domain.value_objects.media import DataItem, MediaContent, MediaGroup
from src.domain.value_objects.post_flag import PostFlag


class Content(BaseModel):
    id: str = Field(...)


class Post(Content):
    media: MediaContent = Field(...)
    keyboard: Keyboard = Field(default_factory=Keyboard)
    flags: PostFlag = Field(default_factory=PostFlag)

    @field_validator("media", mode="before")
    @classmethod
    def media_validator(cls, values: list[Mapping] | DataItem):
        from src.domain.factories import media_factory

        if isinstance(values, DataItem):
            return values

        is_media_group = len(values) > 1
        if not is_media_group:
            return media_factory(values[0])

        parsed_items = tuple(media_factory(item) for item in values)
        return MediaGroup(items=parsed_items)

    @model_validator(mode="after")
    def check_keyboard(self):
        if self.keyboard and isinstance(self.media, MediaGroup):
            raise NotSupportedKeyboardError("Post cannot have keyboard if there is MediaGroup")
        return self


class PostGroup(Content):
    posts: list[Post] = Field(...)

    def __get_item__(self, item: int) -> Post:
        return self.posts[item]
