from typing import TypeAlias

from src.domain.entities.media.photo_node import PhotoNode
from src.domain.entities.media.text_node import TextNode
from src.domain.entities.media.video_node import VideoNode

MediaItem: TypeAlias = PhotoNode | VideoNode | TextNode
