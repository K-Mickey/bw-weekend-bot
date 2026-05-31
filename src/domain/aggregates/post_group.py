from pydantic import BaseModel, Field

from src.domain.aggregates.post import Post


class PostGroup(BaseModel):
    id: str = Field(...)
    posts: list[Post] = Field(...)

    def __get_item__(self, item: int) -> Post:
        return self.posts[item]
