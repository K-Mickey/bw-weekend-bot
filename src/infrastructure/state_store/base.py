from abc import ABC, abstractmethod
from typing import Self

from src.domain.entities.user_session import UserSession
from src.domain.value_objects.user_key import UserKey


class StateStore(ABC):
    @abstractmethod
    async def get_session(self, user_key: UserKey) -> UserSession | None:
        """Retrieve session for the given user key."""
        pass

    @abstractmethod
    async def create_or_reset(self, user_key: UserKey, root_node_id: str) -> UserSession:
        """Create a new session or reset existing one for the user."""
        pass

    @abstractmethod
    async def push_node(self, user_key: UserKey, node_id: str) -> None:
        """Push a node ID onto the user's navigation stack."""
        pass

    @abstractmethod
    async def pop_node(self, user_key: UserKey) -> str | None:
        """Pop the top node ID from the user's navigation stack and return it."""
        pass

    @abstractmethod
    async def clear(self, user_key: UserKey) -> None:
        """Clear the user's session data."""
        pass

    @classmethod
    @abstractmethod
    async def get_instance(cls) -> Self:
        """Singleton accessor – concrete classes decide the pattern."""
        pass
