import asyncio
from datetime import datetime
from typing import Iterable, Self

from src.infrastructure.file_cache.base import (
    CacheRecord,
    MediaCache,
)
from src.infrastructure.file_cache.exceptions import MediaCacheExpired, MediaCacheMiss
from src.infrastructure.file_cache.value_objects.cache_key import CacheKey


class InMemoryMediaCache(MediaCache):
    _instance: Self | None = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        self._store: dict[CacheKey, CacheRecord] = {}
        self._store_lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls) -> Self:
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def get(self, cache_key: CacheKey) -> CacheRecord:
        async with self._store_lock:
            return self._get_unsafe(cache_key)

    async def get_many(self, cache_keys: Iterable[CacheKey]) -> dict[CacheKey, CacheRecord]:
        async with self._store_lock:
            return {key: self._get_unsafe(key) for key in cache_keys}

    def _get_unsafe(self, cache_key: CacheKey) -> CacheRecord:
        try:
            record = self._store[cache_key]
            if not self.check_expiration(record):
                raise MediaCacheExpired(f"Cache miss for {cache_key}")
            return record
        except KeyError:
            raise MediaCacheMiss(f"Cache miss for {cache_key}")

    async def add(self, cache_key: CacheKey, cache_record: CacheRecord) -> None:
        async with self._store_lock:
            cache_record = cache_record._replace(updated_at=datetime.now())
            self._store[cache_key] = cache_record

    async def remove(self, cache_key: CacheKey) -> None:
        async with self._store_lock:
            self._store.pop(cache_key, None)

    async def all_entries(self) -> dict[CacheKey, CacheRecord]:
        async with self._store_lock:
            return self._store.copy()
