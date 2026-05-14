from pydantic import BaseModel, Field, field_validator


class VideoNode(BaseModel):
    url: str = Field(...)
    description: str | None = None

    @field_validator("description")
    @classmethod
    def check_description_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 1024:
            raise ValueError("description length must not exceed 1024 characters")
        return v
