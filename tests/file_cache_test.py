from asyncio import sleep
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


@pytest.fixture
def make_cache_key():
    def _make_cache_key(
        media_type: CacheMediaType = CacheMediaType.PHOTO,
        network: Network = Network.TELEGRAM,
        key: str = "temp",
    ) -> CacheKey:
        return CacheKey(media_type=media_type, network=network, key=key)

    return _make_cache_key


@pytest.fixture
def make_cache_record(temp_file):
    def _make_cache_record(file_id: str = "123", file_path: Path = None, expires: int = None) -> CacheRecord:
        return CacheRecord.from_file(file_id=file_id, file_path=file_path or temp_file, expires=expires)

    return _make_cache_record


@pytest.mark.asyncio
async def test_get_instance():
    instance = await InMemoryMediaCache.get_instance()
    assert instance._instance is not None

    same_instance = await InMemoryMediaCache.get_instance()
    assert instance is same_instance


@pytest.mark.asyncio
async def test_add_and_get(cache, temp_file, cache_key, make_cache_record):
    record = make_cache_record(file_id="123")
    await cache.add(cache_key, record)
    fetched = await cache.get(cache_key)
    assert fetched.file_id == "123"
    assert fetched.mtime == temp_file.stat().st_mtime
    assert fetched.updated_at is not None


@pytest.mark.asyncio
async def test_duplicate_add(cache, cache_key, make_cache_record):
    records = (make_cache_record(file_id="123"), make_cache_record(file_id="234"))
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
async def test_expiration(cache, cache_key, make_cache_record):
    record = make_cache_record(file_id="exp", expires=1)
    await cache.add(cache_key, record)
    fetched = await cache.get(cache_key)
    assert fetched.file_id == "exp"
    await sleep(1.1)

    with pytest.raises(MediaCacheExpired):
        await cache.get(cache_key)


@pytest.mark.asyncio
async def test_new_updated_at(cache, cache_key):
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
async def test_remove_and_all_entries(cache, make_cache_record, make_cache_key):
    cache_keys = (make_cache_key(key="del"), make_cache_key(key="other"))
    records = (make_cache_record(file_id="del"), make_cache_record(file_id="other"))
    for cache_key, record in zip(cache_keys, records):
        await cache.add(cache_key, record)

    entries = await cache.all_entries()
    assert len(entries) == 2

    first_key = cache_keys[0]
    assert first_key in entries
    assert entries[first_key].file_id == records[0].file_id

    second_key = cache_keys[1]
    assert second_key in entries
    assert entries[second_key].file_id == records[1].file_id

    await cache.remove(first_key)

    entries = await cache.all_entries()
    assert len(entries) == 1
    assert first_key not in entries
    with pytest.raises(MediaCacheMiss):
        await cache.get(first_key)


@pytest.mark.asyncio
async def test_get_many(cache, make_cache_key, make_cache_record):
    cache_keys = (
        make_cache_key(key="temp1"),
        make_cache_key(key="temp2"),
        make_cache_key(key="temp3"),
    )
    records = (
        make_cache_record(file_id="123"),
        make_cache_record(file_id="234"),
        make_cache_record(file_id="345"),
    )
    for cache_key, record in zip(cache_keys, records):
        await cache.add(cache_key, record)

    fetched = await cache.get_many(cache_keys[:2])
    assert len(fetched) == 2
    assert fetched[cache_keys[0]].file_id == records[0].file_id
    assert fetched[cache_keys[1]].file_id == records[1].file_id
    assert len(cache._store) == 3


@pytest.mark.asyncio
async def test_get_many_miss_raises(cache, make_cache_key):
    cache_keys = (make_cache_key(key="temp1"), make_cache_key(key="temp2"))
    with pytest.raises(MediaCacheMiss):
        await cache.get_many(cache_keys)


@pytest.mark.asyncio
async def test_get_many_with_expiration(cache, make_cache_key, make_cache_record):
    cache_keys = (make_cache_key(key="temp1"), make_cache_key(key="temp2"))
    records = (make_cache_record(file_id="123"), make_cache_record(file_id="234", expires=1))
    for cache_key, record in zip(cache_keys, records):
        await cache.add(cache_key, record)

    fetched = await cache.get_many(cache_keys)
    assert len(fetched) == 2

    await sleep(1.1)
    with pytest.raises(MediaCacheExpired):
        await cache.get_many(cache_keys)
