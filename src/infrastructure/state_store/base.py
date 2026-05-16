from abc import ABC, abstractmethod

from src.domain.value_objects.user_key import UserKey
from src.domain.value_objects.user_session import UserSession


class StateStore(ABC):
    @abstractmethod
    def get_session(self, user_key: UserKey) -> UserSession | None:
        """Retrieve session for the given user key."""
        pass

    @abstractmethod
    def create_or_reset(self, user_key: UserKey, root_node_id: str) -> UserSession:
        """Create a new session or reset existing one for the user."""
        pass

    @abstractmethod
    def push_node(self, user_key: UserKey, node_id: str) -> None:
        """Push a node ID onto the user's navigation stack."""
        pass

    @abstractmethod
    def pop_node(self, user_key: UserKey) -> str | None:
        """Pop the top node ID from the user's navigation stack and return it."""
        pass

    @abstractmethod
    def clear(self, user_key: UserKey) -> None:
        """Clear the user's session data."""
        pass
