from typing import TypeAlias

from .post import Post
from .post_group import PostGroup

Content: TypeAlias = PostGroup | Post
