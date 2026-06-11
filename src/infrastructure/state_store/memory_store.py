import asyncio
from typing import Self

from src.domain.entities.user_session import UserSession
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store.base import StateStore


class InMemoryStateStore(StateStore):
    _instance: Self | None = None
    _lock = asyncio.Lock()

    def __init__(self):
        self._sessions: dict[UserKey, UserSession] = {}
        self._store_lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls) -> Self:
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def get_session(self, user_key: UserKey) -> UserSession | None:
        async with self._store_lock:
            return self._sessions.get(user_key)

    async def create_or_reset(self, user_key: UserKey, root_node_id: str) -> UserSession:
        async with self._store_lock:
            session = UserSession(user_key=user_key, history=[root_node_id])
            self._sessions[user_key] = session
            return session

    async def push_node(self, user_key: UserKey, node_id: str) -> None:
        async with self._store_lock:
            if session := self._sessions.get(user_key):
                session.push(node_id)

    async def pop_node(self, user_key: UserKey) -> str | None:
        async with self._store_lock:
            if session := self._sessions.get(user_key):
                return session.pop()
            return None

    async def clear(self, user_key: UserKey) -> None:
        async with self._store_lock:
            if user_key in self._sessions:
                del self._sessions[user_key]
