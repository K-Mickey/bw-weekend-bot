import asyncio
from datetime import datetime
from typing import Iterable, Self

import aiosqlite
from aiosqlite import Connection

from src.config import settings
from src.domain.exceptions import CacheExpiredError, CacheMissError
from src.domain.ports import MediaCache
from src.domain.value_objects.cache import CacheKey, CacheMediaType, CacheRecord
from src.domain.value_objects.network import Network
from src.infrastructure.exceptions import LostConnectionError


class SQLiteMediaCache(MediaCache):
    _instance: Self | None = None
    _lock = asyncio.Lock()
    _connection: Connection | None = None
    _db_path: str = settings.media_cache_db

    @classmethod
    async def get_instance(cls) -> Self:
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._init()
        return cls._instance

    async def _init(self) -> None:
        self._connection = await aiosqlite.connect(self._db_path)
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_entries (
                media_type TEXT NOT NULL,
                network TEXT NOT NULL,
                key TEXT NOT NULL,
                file_id TEXT NOT NULL,
                mtime REAL NOT NULL,
                expires REAL,
                updated_at REAL NOT NULL,
                PRIMARY KEY (media_type, network, key)
            )
            """
        )
        await self._connection.commit()

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def get(self, cache_key: CacheKey) -> CacheRecord:
        if not self._connection:
            raise LostConnectionError()

        async with self._connection.execute(
            """
            SELECT file_id, mtime, expires, updated_at
            FROM cache_entries
            WHERE media_type = ? AND network = ? AND key = ?
            """,
            (cache_key.media_type, cache_key.network, cache_key.key),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            raise CacheMissError(cache_key)

        file_id, mtime, expires, updated_at = row
        updated_at_dt = datetime.fromtimestamp(updated_at)
        record = CacheRecord(
            file_id=file_id,
            mtime=mtime,
            expires=expires,
            updated_at=updated_at_dt,
        )

        if not self.check_expiration(record):
            raise CacheExpiredError(cache_key)

        return record

    async def get_many(self, cache_keys: Iterable[CacheKey]) -> dict[CacheKey, CacheRecord]:
        if not self._connection:
            raise LostConnectionError()
        return {key: await self.get(key) for key in cache_keys}

    async def add(self, cache_key: CacheKey, cache_record: CacheRecord) -> None:
        if not self._connection:
            raise LostConnectionError()

        updated_at = datetime.now()
        cache_record = cache_record._replace(updated_at=updated_at)

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO cache_entries
            (media_type, network, key, file_id, mtime, expires, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cache_key.media_type,
                cache_key.network,
                cache_key.key,
                cache_record.file_id,
                cache_record.mtime,
                cache_record.expires,
                cache_record.updated_at.timestamp(),
            ),
        )
        await self._connection.commit()

    async def remove(self, cache_key: CacheKey) -> None:
        if not self._connection:
            raise LostConnectionError()

        await self._connection.execute(
            """
            DELETE FROM cache_entries
            WHERE media_type = ? AND network = ? AND key = ?
            """,
            (cache_key.media_type, cache_key.network, cache_key.key),
        )
        await self._connection.commit()

    async def all_entries(self) -> dict[CacheKey, CacheRecord]:
        if not self._connection:
            raise LostConnectionError()

        async with self._connection.execute(
            """
            SELECT media_type, network, key, file_id, mtime, expires, updated_at
            FROM cache_entries
            """
        ) as cursor:
            rows = await cursor.fetchall()

        result: dict[CacheKey, CacheRecord] = {}
        for row in rows:
            media_type, network, key, file_id, mtime, expires, updated_at = row

            media_type_enum = CacheMediaType(media_type)
            network_enum = Network(network)
            cache_key_obj = CacheKey(media_type_enum, network_enum, key)

            updated_at_dt = datetime.fromtimestamp(updated_at)
            record = CacheRecord(
                file_id=file_id,
                mtime=mtime,
                expires=expires,
                updated_at=updated_at_dt,
            )
            result[cache_key_obj] = record
        return result
