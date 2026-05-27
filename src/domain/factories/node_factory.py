from ..aggregates import Content
from ..aggregates.menu_node import MenuNode
from ..aggregates.post_node import PostNode


def node_factory(raw: dict) -> Content:
    print(raw)
    match raw:
        case {"content": _}:
            return MenuNode(**raw)
        case {"media": _}:
            return PostNode(**raw)
        case _:
            raise ValueError("Invalid node")
