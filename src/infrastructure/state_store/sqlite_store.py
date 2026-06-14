import asyncio
import uuid
from datetime import time
from typing import Self

import aiosqlite
from aiosqlite import Connection

from src.domain.entities.user_session import UserSession
from src.domain.ports import StateStore
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.exceptions import LostConnectionError


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
                session_id TEXT NOT NULL,
                PRIMARY KEY(network, external_id),
                UNIQUE(session_id)
            )
            """
        )
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS session_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE CASCADE
            )
            """
        )
        await self._connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_session_history_session_id
            ON session_history(session_id)
            """
        )
        await self._connection.commit()

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def get_session(self, user_key: UserKey) -> UserSession | None:
        if not self._connection:
            raise LostConnectionError()

        session_id = await self._get_session_id(user_key)
        if not session_id:
            return None

        history: list[str] = []
        async with self._connection.execute(
            """
            SELECT name
            FROM session_history
            WHERE session_id = ?
            ORDER BY created_at
            """,
            (session_id,),
        ) as cursor:
            async for row in cursor:
                history.append(row[0])

        return UserSession(user_key, history)

    async def create_or_reset(self, user_key: UserKey, root_node_id: str) -> UserSession:
        if not self._connection:
            raise LostConnectionError()

        session_id = await self._get_session_id(user_key)
        if not session_id:
            session_id = str(uuid.uuid4())
        else:
            await self.clear(user_key)

        await self._connection.execute(
            """
            INSERT INTO user_sessions (session_id, network, external_id)
            VALUES (?, ?, ?)
            """,
            (session_id, user_key.network, user_key.external_id),
        )

        created_at = time()
        await self._connection.execute(
            """
            INSERT INTO session_history (session_id, name, created_at)
            VALUES (?, ?, ?)
            """,
            (session_id, root_node_id, created_at),
        )
        await self._connection.commit()

        return UserSession(user_key, [root_node_id])

    async def push_node(self, user_key: UserKey, node_id: str) -> None:
        if not self._connection:
            raise LostConnectionError()

        current_time = time()
        await self._connection.execute(
            """
            INSERT INTO session_history (session_id, name, created_at)
            SELECT session_id, ?, ?
            FROM user_sessions
            WHERE network = ? AND external_id = ?
            """,
            (node_id, current_time, user_key.network, user_key.external_id),
        )
        await self._connection.commit()

    async def pop_node(self, user_key: UserKey) -> str | None:
        if not self._connection:
            raise LostConnectionError()

        async with self._connection.execute(
            """
            DELETE FROM session_history
            WHERE id IN (
                SELECT id FROM session_history
                JOIN user_sessions USING(session_id)
                WHERE network = ? AND external_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            )
            RETURNING name;
            """,
            (user_key.network, user_key.external_id),
        ) as cursor:
            row = await cursor.fetchone()
            popped_node = row[0] if row else None

        await self._connection.commit()
        return popped_node

    async def clear(self, user_key: UserKey) -> None:
        if not self._connection:
            raise LostConnectionError()

        await self._connection.execute(
            """
            DELETE FROM user_sessions
            WHERE network = ? AND external_id = ?
            """,
            (user_key.network, user_key.external_id),
        )
        await self._connection.commit()

    async def _get_session_id(self, user_key: UserKey) -> str | None:
        async with self._connection.execute(
            """
            SELECT session_id FROM user_sessions
            WHERE network = ? AND external_id = ?
            """,
            (user_key.network, user_key.external_id),
        ) as cursor:
            row = await cursor.fetchone()
        return row[0] if row else None
