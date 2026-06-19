import asyncio
import uuid
from datetime import datetime
from typing import Iterable, Self

import aiosqlite
from aiosqlite import Connection

from src.domain.ports import StateStore
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.exceptions import LostConnectionError


class SQLiteStateStore(StateStore):
    _instance: Self | None = None
    _lock = asyncio.Lock()
    _connection: Connection | None = None
    _db_path: str = "state_store.db"

    async def get_current_state(self, user_key: UserKey) -> str | None:
        if not self._connection:
            raise LostConnectionError()

        if session_id := await self._get_session_id(user_key):
            async with self._connection.execute(
                """
                SELECT name
                FROM session_history
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (session_id,),
            ) as cursor:
                if row := await cursor.fetchone():
                    return row[0]

        return None

    async def get_history(self, user_key: UserKey) -> tuple[str, ...]:
        if not self._connection:
            raise LostConnectionError()

        if session_id := await self._get_session_id(user_key):
            async with self._connection.execute(
                """
                SELECT name
                FROM session_history
                WHERE session_id = ?
                ORDER BY created_at
                """,
                (session_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return tuple(row[0] for row in rows)

        return ()

    async def set_history(self, user_key: UserKey, history: Iterable[str]) -> tuple[str, ...]:
        if not self._connection:
            raise LostConnectionError()

        session_id = await self._get_session_id(user_key)
        if not session_id:
            session_id = await self._create_user(user_key)

        sessions = [(session_id, name, self._get_time()) for name in history]
        await self._connection.executemany(
            """
            INSERT INTO session_history (session_id, name, created_at)
            VALUES (?, ?, ?)
            """,
            sessions,
        )
        await self._connection.commit()
        return tuple(history)

    async def append(self, user_key: UserKey, state: str) -> None:
        if not self._connection:
            raise LostConnectionError()

        session_id = await self._get_session_id(user_key)
        if not session_id:
            session_id = await self._create_user(user_key)

        current_time = self._get_time()
        await self._connection.execute(
            """
            INSERT INTO session_history (session_id, name, created_at)
            VALUES (?, ?, ?)
            """,
            (session_id, state, current_time),
        )
        await self._connection.commit()

    async def pop(self, user_key: UserKey) -> str | None:
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
            popped = row[0] if row else None

        await self._connection.commit()
        return popped

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

    @classmethod
    async def get_instance(cls) -> Self:
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._init()
        return cls._instance

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
            self._connection = None

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

    async def _create_user(self, user_key: UserKey) -> str:
        session_id = self._create_user_id()

        await self._connection.execute(
            """
            INSERT INTO user_sessions (session_id, network, external_id)
            VALUES (?, ?, ?)
            """,
            (session_id, user_key.network, user_key.external_id),
        )
        await self._connection.commit()
        return session_id

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

    @staticmethod
    def _create_user_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _get_time() -> float:
        return datetime.now().timestamp()
