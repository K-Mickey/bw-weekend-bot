from pydantic import BaseModel, Field


class PostNodeFlags(BaseModel):
    is_back: bool = Field(default=True)
    is_main: bool = Field(default=True)
    build: bool = Field(default=True)
