import abc
from datetime import datetime, timedelta
from typing import Iterable, Self

from src.domain.value_objects.cache import CacheKey, CacheRecord


class MediaCache(abc.ABC):
    """Abstract interface for a media‑file cache.

    Concrete implementations may keep data in memory, SQLite, Redis, etc.
    All methods are async to allow I/O‑heavy back‑ends.
    """

    @abc.abstractmethod
    async def get(self, cache_key: CacheKey) -> CacheRecord:
        """Return the cached record.

        Raises
        ------
        MediaCacheMiss
            If the key is not present in the cache.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_many(self, cache_keys: Iterable[CacheKey]) -> dict[CacheKey, CacheRecord]:
        raise NotImplementedError

    @abc.abstractmethod
    async def add(self, cache_key: CacheKey, cache_record: CacheRecord) -> None:
        """Insert or replace a cache entry. No existence check is performed."""
        raise NotImplementedError

    @abc.abstractmethod
    async def remove(self, cache_key: CacheKey) -> None:
        """Delete an entry if it exists; otherwise do nothing."""
        raise NotImplementedError

    @abc.abstractmethod
    async def all_entries(self) -> dict[CacheKey, CacheRecord]:
        """Return a list of all records – used by validation scripts."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def get_instance(cls) -> Self:
        """Singleton accessor – concrete classes decide the pattern."""
        raise NotImplementedError

    @abc.abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @staticmethod
    def check_expiration(record: CacheRecord) -> bool:
        if record.expires:
            expires_at = record.updated_at + timedelta(seconds=record.expires)
            if expires_at < datetime.now():
                return False
        return True
