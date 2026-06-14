import asyncio
from typing import Iterable, Self

from src.domain.ports import StateStore
from src.domain.value_objects.user_key import UserKey


class MemoryStateStore(StateStore):
    _instance: Self | None = None
    _lock = asyncio.Lock()

    def __init__(self):
        self._sessions: dict[UserKey, list[str]] = {}
        self._store_lock = asyncio.Lock()

    async def get_current_state(self, user_key: UserKey) -> str | None:
        async with self._store_lock:
            if session := self._sessions.get(user_key):
                return session[-1]
            return None

    async def get_history(self, user_key: UserKey) -> tuple[str, ...]:
        async with self._store_lock:
            if session := self._sessions.get(user_key):
                return tuple(session)
            return ()

    async def set_history(self, user_key: UserKey, history: Iterable[str]) -> tuple[str, ...]:
        async with self._store_lock:
            self._sessions[user_key] = list(history)
            return tuple(self._sessions[user_key])

    async def append(self, user_key: UserKey, state: str) -> str:
        async with self._store_lock:
            self._sessions.setdefault(user_key, []).append(state)
            return state

    async def pop(self, user_key: UserKey) -> str | None:
        async with self._store_lock:
            if session := self._sessions.get(user_key):
                return session.pop()
            return None

    async def clear(self, user_key: UserKey) -> bool:
        async with self._store_lock:
            if user_key in self._sessions:
                del self._sessions[user_key]
                return True
            return False

    @classmethod
    async def get_instance(cls) -> Self:
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    async def close(self) -> None:
        pass
