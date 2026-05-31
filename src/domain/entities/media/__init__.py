from typing import TypeAlias

from .photo import Photo
from .text import Text
from .video import Video

MediaType: TypeAlias = Photo | Video
MediaItem: TypeAlias = Photo | Video | Text
