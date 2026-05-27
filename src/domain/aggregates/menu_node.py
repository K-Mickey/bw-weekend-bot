from pydantic import BaseModel, Field

from ..aggregates.post_node import PostNode


class MenuNode(BaseModel):
    id: str = Field(...)
    content: list[PostNode] = Field(...)
