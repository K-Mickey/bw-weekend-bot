from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from src.domain.exceptions import NotSupportedKeyboardError
from src.domain.value_objects.keyboard import Keyboard
from src.domain.value_objects.media import MediaGroup, Photo, Text, Video
from src.domain.value_objects.post_flag import PostFlag


class Content(BaseModel):
    id: str = Field(...)


class Post(Content):
    type: Literal["post"] = "post"
    media: Text | Photo | Video | MediaGroup = Field(...)
    keyboard: Keyboard = Field(default_factory=Keyboard)
    flags: PostFlag = Field(default_factory=PostFlag)

    @field_validator("media", mode="before")
    @classmethod
    def media_validator(cls, values):
        if isinstance(values, list):
            return MediaGroup(items=tuple(values))
        return values

    @model_validator(mode="after")
    def check_keyboard(self):
        if self.keyboard and isinstance(self.media, MediaGroup):
            raise NotSupportedKeyboardError("Post cannot have keyboard if there is MediaGroup")
        return self


class PostGroup(Content):
    type: Literal["post_group"] = "post_group"
    posts: list[Post] = Field(...)

    def __get_item__(self, item: int) -> Post:
        return self.posts[item]
