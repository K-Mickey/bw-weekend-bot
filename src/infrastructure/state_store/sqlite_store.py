import asyncio
import json
from typing import Self

import aiosqlite
from aiosqlite import Connection

from src.domain.entities.user_session import UserSession
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store.base import StateStore


class SQLiteStateStoreError(Exception):
    pass


class SQLiteRuntimeError(SQLiteStateStoreError):
    def __init__(self, *args):
        super().__init__(*args)
        self.message = "Database connection not initialized. Call get_instance first."


class SQLiteStateStore(StateStore):
    _instance: Self | None = None
    _lock = asyncio.Lock()
    _connection: Connection | None = None
    _db_path: str = "state_store.db"

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
            CREATE TABLE IF NOT EXISTS user_sessions (
                network TEXT NOT NULL,
                external_id TEXT NOT NULL,
                history_json TEXT NOT NULL,
                PRIMARY KEY (network, external_id)
            )
            """
        )
        await self._connection.commit()

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None

    def _row_to_session(self, network: str, external_id: str, history_json: str) -> UserSession:
        user_key = UserKey(Network(network), external_id)
        history = json.loads(history_json)
        session = UserSession(user_key, history)
        return session

    async def get_session(self, user_key: UserKey) -> UserSession | None:
        if not self._connection:
            raise SQLiteRuntimeError

        async with self._connection.execute(
            """
            SELECT network, external_id, history_json
            FROM user_sessions
            WHERE network = ? AND external_id = ?
            """,
            (user_key.network, user_key.external_id),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            return None

        return self._row_to_session(*row)

    async def create_or_reset(self, user_key: UserKey, root_node_id: str) -> UserSession:
        if not self._connection:
            raise SQLiteRuntimeError

        history = [root_node_id]
        history_json = json.dumps(history)

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO user_sessions
            (network, external_id, history_json)
            VALUES (?, ?, ?)
            """,
            (user_key.network, user_key.external_id, history_json),
        )
        await self._connection.commit()

        return UserSession(user_key, history)

    async def push_node(self, user_key: UserKey, node_id: str) -> None:
        if not self._connection:
            raise SQLiteRuntimeError

        async with self._connection.execute(
            """
            SELECT history_json FROM user_sessions
            WHERE network = ? AND external_id = ?
            """,
            (user_key.network, user_key.external_id),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            return

        history = json.loads(row[0])
        history.append(node_id)
        history_json = json.dumps(history)

        await self._connection.execute(
            """
            UPDATE user_sessions
            SET history_json = ?
            WHERE network = ? AND external_id = ?
            """,
            (history_json, user_key.network, user_key.external_id),
        )
        await self._connection.commit()

    async def pop_node(self, user_key: UserKey) -> str | None:
        if not self._connection:
            raise SQLiteRuntimeError

        async with self._connection.execute(
            """
            SELECT history_json FROM user_sessions
            WHERE network = ? AND external_id = ?
            """,
            (user_key.network, user_key.external_id),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            return None

        history = json.loads(row[0])
        if len(history) <= 1:
            return None

        popped = history.pop()
        history_json = json.dumps(history)

        await self._connection.execute(
            """
            UPDATE user_sessions
            SET history_json = ?
            WHERE network = ? AND external_id = ?
            """,
            (history_json, user_key.network, user_key.external_id),
        )
        await self._connection.commit()

        return popped

    async def clear(self, user_key: UserKey) -> None:
        if not self._connection:
            raise SQLiteRuntimeError

        await self._connection.execute(
            """
            DELETE FROM user_sessions
            WHERE network = ? AND external_id = ?
            """,
            (user_key.network, user_key.external_id),
        )
        await self._connection.commit()
