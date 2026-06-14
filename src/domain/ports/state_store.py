from abc import ABC, abstractmethod
from typing import Iterable, Self

from src.domain.value_objects.user_key import UserKey


class StateStore(ABC):
    @abstractmethod
    async def get_current_state(self, user_key: UserKey) -> str | None:
        """Retrieve the current state for the given user key."""
        raise NotImplementedError

    @abstractmethod
    async def get_history(self, user_key: UserKey) -> tuple[str, ...]:
        """Retrieve the history for the given user key."""
        raise NotImplementedError

    @abstractmethod
    async def set_history(self, user_key: UserKey, history: Iterable[str]) -> tuple[str, ...]:
        """Set the history for the given user key."""
        raise NotImplementedError

    @abstractmethod
    async def append(self, user_key: UserKey, state: str) -> str:
        """Push a node ID onto the user's navigation stack."""
        raise NotImplementedError

    @abstractmethod
    async def pop(self, user_key: UserKey) -> str | None:
        """Pop the top node ID from the user's navigation stack and return it."""
        raise NotImplementedError

    @abstractmethod
    async def clear(self, user_key: UserKey) -> bool:
        """Clear the user's session data."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    async def get_instance(cls) -> Self:
        """Singleton accessor – concrete classes decide the pattern."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Close the connection to the database."""
        raise NotImplementedError
