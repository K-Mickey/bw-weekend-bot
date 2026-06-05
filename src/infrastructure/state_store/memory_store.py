from typing import Self

from src.domain.entities.user_session import UserSession
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store.base import StateStore


class InMemoryStateStore(StateStore):
    _instance: Self | None = None

    def __init__(self):
        self._sessions: dict[UserKey, UserSession] = {}

    @classmethod
    def get_instance(cls) -> Self:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_session(self, user_key: UserKey) -> UserSession | None:
        return self._sessions.get(user_key)

    def create_or_reset(self, user_key: UserKey, root_node_id: str) -> UserSession:
        session = UserSession(user_key=user_key, root_node_id=root_node_id)
        self._sessions[user_key] = session
        return session

    def push_node(self, user_key: UserKey, node_id: str) -> None:
        if session := self.get_session(user_key):
            session.push(node_id)

    def pop_node(self, user_key: UserKey) -> str | None:
        if session := self.get_session(user_key):
            return session.pop()
        return None

    def clear(self, user_key: UserKey) -> None:
        if user_key in self._sessions:
            del self._sessions[user_key]
