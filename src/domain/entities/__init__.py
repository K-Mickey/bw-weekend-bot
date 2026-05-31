from typing import TypeAlias

from src.domain.entities.media import MediaItem
from src.domain.entities.media_group import MediaGroup

MediaContent: TypeAlias = MediaItem | MediaGroup
