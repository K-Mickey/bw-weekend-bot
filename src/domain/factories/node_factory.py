from pydantic import BaseModel

from ..aggregates.menu_node import MenuNode
from ..aggregates.post_node import PostNode


def node_factory(raw: dict) -> BaseModel:
    match raw:
        case {"keyboard": _}:
            return MenuNode(**raw)
        case {"media": _}:
            return PostNode(**raw)
        case _:
            raise ValueError("Invalid node")
