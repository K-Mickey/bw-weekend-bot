from pydantic import BaseModel, Field, field_validator


class Photo(BaseModel):
    local_path: str = Field(...)
    description: str | None = None

    def __hash__(self):
        return hash((self.local_path, self.description))

    def __repr__(self):
        return f"PhotoNode({self.local_path}, {self.description})"

    @field_validator("description")
    @classmethod
    def check_description_length(cls, v: str | None) -> str | None:
        if v is not None and len(v) > 1024:
            raise ValueError("description length must not exceed 1024 characters")
        return v
