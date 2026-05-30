from typing import NamedTuple, Self

from src.domain.entities.media import PhotoNode, VideoNode
from src.domain.value_objects.network import Network
from src.infrastructure.file_cache.value_objects.cache_media_type import CacheMediaType


class CacheKey(NamedTuple):
    media_type: CacheMediaType
    network: Network
    key: str

    def __str__(self) -> str:
        return f"{self.media_type}/{self.network}/{self.key}"

    @classmethod
    def create(cls, media: PhotoNode | VideoNode, network: Network) -> Self:
        match media:
            case PhotoNode():
                media_type = CacheMediaType.PHOTO
            case VideoNode():
                media_type = CacheMediaType.VIDEO
            case _:
                raise ValueError(f"Unsupported media type: {media}")

        return cls(
            media_type=media_type,
            network=network,
            key=media.url,
        )
