from pydantic import BaseModel, Field, field_validator

from src.domain.entities.button_type import ButtonType


class KeyboardButton(BaseModel):
    text: str = Field(...)
    target: str = Field(...)
    type: ButtonType = Field(ButtonType.DEFAULT)

    @field_validator("text")
    @classmethod
    def truncate_long_text(cls, v: str) -> str:
        if len(v) > 35:
            return f"{v[:32]}..."
        return v
