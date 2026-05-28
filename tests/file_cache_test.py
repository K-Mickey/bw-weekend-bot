import asyncio
from datetime import datetime
from pathlib import Path

import pytest

from src.domain.value_objects.network import Network
from src.infrastructure.file_cache.exceptions import MediaCacheExpired, MediaCacheMiss
from src.infrastructure.file_cache.in_memory import InMemoryMediaCache
from src.infrastructure.file_cache.value_objects.cache_key import CacheKey
from src.infrastructure.file_cache.value_objects.cache_media_type import CacheMediaType
from src.infrastructure.file_cache.value_objects.cache_record import CacheRecord


@pytest.fixture
def cache() -> InMemoryMediaCache:
    return InMemoryMediaCache()


@pytest.fixture
def cache_key() -> CacheKey:
    return CacheKey(media_type=CacheMediaType.PHOTO, network=Network.TELEGRAM, key="temp")


@pytest.fixture
def temp_file(photo_dir) -> Path:
    return photo_dir / "exist.jpg"


@pytest.mark.asyncio
async def test_get_instance():
    instance = await InMemoryMediaCache.get_instance()
    assert instance._instance is not None

    same_instance = await InMemoryMediaCache.get_instance()
    assert instance is same_instance


@pytest.mark.asyncio
async def test_add_and_get(cache, temp_file, cache_key):
    record = CacheRecord.from_file(file_id="123", file_path=temp_file)
    await cache.add(cache_key, record)
    fetched = await cache.get(cache_key)
    assert fetched.file_id == "123"
    assert fetched.mtime == temp_file.stat().st_mtime
    assert fetched.updated_at is not None


@pytest.mark.asyncio
async def test_duplicate_add(cache, temp_file, cache_key):
    records = (
        CacheRecord.from_file(file_id="123", file_path=temp_file),
        CacheRecord.from_file(file_id="234", file_path=temp_file),
    )
    for record in records:
        await cache.add(cache_key, record)

    store = cache._store
    assert len(store) == 1
    assert store[cache_key].file_id == records[-1].file_id


@pytest.mark.asyncio
async def test_get_miss_raises(cache, cache_key):
    with pytest.raises(MediaCacheMiss):
        await cache.get(cache_key)


@pytest.mark.asyncio
async def test_expiration(cache, temp_file, cache_key):
    record = CacheRecord.from_file(file_id="exp", file_path=temp_file, expires=1)
    await cache.add(cache_key, record)
    fetched = await cache.get(cache_key)
    assert fetched.file_id == "exp"
    await asyncio.sleep(1.1)

    with pytest.raises(MediaCacheExpired):
        await cache.get(cache_key)


@pytest.mark.asyncio
async def test_new_updated_at(cache, temp_file, cache_key):
    updated_at = datetime(2000, 1, 1)
    record = CacheRecord(
        file_id="exp",
        mtime=1,
        expires=None,
        updated_at=updated_at,
    )
    await cache.add(cache_key, record)
    fetched = await cache.get(cache_key)
    assert fetched.updated_at != updated_at


@pytest.mark.asyncio
async def test_remove_and_all_entries(cache, temp_file, cache_key):
    record = CacheRecord.from_file(file_id="del", file_path=temp_file)
    await cache.add(cache_key, record)

    other_key = CacheKey(media_type=CacheMediaType.PHOTO, network=Network.TELEGRAM, key="other")
    other_record = CacheRecord.from_file(file_id="other", file_path=temp_file)
    await cache.add(other_key, other_record)

    entries = await cache.all_entries()

    assert len(entries) == 2
    assert cache_key in entries
    assert entries[cache_key].file_id == record.file_id
    assert other_key in entries
    assert entries[other_key].file_id == other_record.file_id

    await cache.remove(cache_key)

    entries = await cache.all_entries()
    assert len(entries) == 1
    assert cache_key not in entries
    with pytest.raises(MediaCacheMiss):
        await cache.get(cache_key)
