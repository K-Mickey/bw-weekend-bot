from pydantic import BaseModel, Field, field_validator


class KeyboardButton(BaseModel):
    text: str = Field(...)
    target: str = Field(...)

    @field_validator("text")
    @classmethod
    def truncate_long_text(cls, v: str) -> str:
        if len(v) > 35:
            return f"{v[:32]}..."
        return v
