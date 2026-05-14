from pydantic import BaseModel, Field

from ..aggregates.post_node import PostNode
from ..entities.keyboard_button import KeyboardButton
from ..value_objects.menu_node_flags import MenuNodeFlags


class MenuNode(BaseModel):
    id: str = Field(...)
    content: list[PostNode] = Field(...)
    keyboard: list[list[KeyboardButton]] = Field(default_factory=list)
    flags: MenuNodeFlags = Field(default_factory=MenuNodeFlags)
