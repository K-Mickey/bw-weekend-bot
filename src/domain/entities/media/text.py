from pydantic import BaseModel, Field, field_validator


class Text(BaseModel):
    text: str = Field(...)

    def __repr__(self):
        return f"TextNode({self.text})"

    @field_validator("text")
    @classmethod
    def check_max_length(cls, v: str) -> str:
        if len(v) > 4096:
            raise ValueError("text length must not exceed 4096 characters")
        return v
