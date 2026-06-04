from typing import NamedTuple, Self

from src.domain.entities.media import Photo, Video
from src.domain.value_objects.network import Network
from src.infrastructure.file_cache.value_objects.cache_media_type import CacheMediaType


class CacheKey(NamedTuple):
    media_type: CacheMediaType
    network: Network
    key: str

    def __str__(self) -> str:
        return f"{self.media_type}/{self.network}/{self.key}"

    @classmethod
    def create(cls, media: Photo | Video, network: Network) -> Self:
        match media:
            case Photo():
                media_type = CacheMediaType.PHOTO
            case Video():
                media_type = CacheMediaType.VIDEO
            case _:
                raise ValueError(f"Unsupported media type: {media}")

        return cls(
            media_type=media_type,
            network=network,
            key=media.local_path,
        )
