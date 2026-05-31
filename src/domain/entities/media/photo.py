from pydantic import BaseModel, Field, field_validator


class Photo(BaseModel):
    url: str = Field(...)
    description: str | None = None

    def __repr__(self):
        return f"PhotoNode({self.url}, {self.description})"

    @field_validator("description")
    @classmethod
    def check_description_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 1024:
            raise ValueError("description length must not exceed 1024 characters")
        return v
