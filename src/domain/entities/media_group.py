from typing import Iterator

from pydantic import BaseModel, Field

from .media import MediaType


class MediaGroup(BaseModel):
    items: tuple[MediaType, ...] = Field(...)

    def __iter__(self) -> Iterator[MediaType]:
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return f"MediaGroup({self.items})"

    def __getitem__(self, index: int) -> MediaType:
        return self.items[index]
