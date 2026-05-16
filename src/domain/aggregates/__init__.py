from typing import TypeAlias

from src.domain.aggregates.menu_node import MenuNode
from src.domain.aggregates.post_node import PostNode

Content: TypeAlias = MenuNode | PostNode
