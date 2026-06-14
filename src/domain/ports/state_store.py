from abc import ABC, abstractmethod
from typing import Self

from src.domain.entities.user_session import UserSession
from src.domain.value_objects.user_key import UserKey


class StateStore(ABC):
    @abstractmethod
    async def get_session(self, user_key: UserKey) -> UserSession | None:
        """Retrieve session for the given user key."""
        raise NotImplementedError

    @abstractmethod
    async def create_or_reset(self, user_key: UserKey, root_node_id: str) -> UserSession:
        """Create a new session or reset existing one for the user."""
        raise NotImplementedError

    @abstractmethod
    async def push_node(self, user_key: UserKey, node_id: str) -> None:
        """Push a node ID onto the user's navigation stack."""
        raise NotImplementedError

    @abstractmethod
    async def pop_node(self, user_key: UserKey) -> str | None:
        """Pop the top node ID from the user's navigation stack and return it."""
        raise NotImplementedError

    @abstractmethod
    async def clear(self, user_key: UserKey) -> None:
        """Clear the user's session data."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def get_instance(cls) -> Self:
        """Singleton accessor – concrete classes decide the pattern."""
        raise NotImplementedError
