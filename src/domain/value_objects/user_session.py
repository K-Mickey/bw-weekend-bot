from .user_key import UserKey


class UserSession:
    def __init__(self, user_key: UserKey, root_node_id: str):
        self.user_key = user_key
        self.history: list[str] = [root_node_id]

    @property
    def current(self) -> str:
        return self.history[-1]

    def push(self, node_id: str) -> None:
        self.history.append(node_id)

    def pop(self) -> str | None:
        if len(self.history) <= 1:
            return None
        return self.history.pop()

    def __str__(self) -> str:
        return f"UserKey: {self.user_key}, History: {self.history}"
