from pydantic import BaseModel, Field, field_validator

from ..aggregates.post_node import PostNode
from ..entities.keyboard_button import KeyboardButton
from ..value_objects.menu_node_flags import MenuNodeFlags


class MenuNode(BaseModel):
    id: str = Field(...)
    content: list[PostNode] = Field(...)
    keyboard: list[list[KeyboardButton]] = Field(default_factory=list)
    flags: MenuNodeFlags = Field(default_factory=MenuNodeFlags)

    @field_validator("keyboard", mode="after")
    def check_unique_buttons(cls, values: list[list[KeyboardButton]]) -> list[list[KeyboardButton]]:
        buttons = [button.text for row in values for button in row]
        if len(buttons) != len(set(buttons)):
            raise ValueError("Duplicate buttons in keyboard")
        return values
