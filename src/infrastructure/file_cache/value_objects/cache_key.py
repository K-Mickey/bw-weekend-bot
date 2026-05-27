from typing import NamedTuple

from src.domain.value_objects.network import Network
from src.infrastructure.file_cache.value_objects.cache_media_type import CacheMediaType


class CacheKey(NamedTuple):
    media_type: CacheMediaType
    network: Network
    key: str

    def __str__(self) -> str:
        return f"{self.media_type}/{self.network}/{self.key}"
