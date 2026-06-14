from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import NamedTuple, Self

from ..exceptions import NotSupportedTypeError
from .media import Photo, Video
from .network import Network


class CacheMediaType(StrEnum):
    PHOTO = "photo"
    VIDEO = "video"


class CacheKey(NamedTuple):
    media_type: CacheMediaType
    network: Network
    key: str

    def __str__(self) -> str:
        return f"{self.media_type}/{self.network}/{self.key}"

    @classmethod
    def create(cls, media: Photo | Video, network: Network) -> Self:
        match media:
            case Photo():
                media_type = CacheMediaType.PHOTO
            case Video():
                media_type = CacheMediaType.VIDEO
            case _:
                raise NotSupportedTypeError(media)

        return cls(
            media_type=media_type,
            network=network,
            key=media.local_path,
        )


class CacheRecord(NamedTuple):
    file_id: str
    mtime: float
    expires: float | None
    updated_at: datetime

    @classmethod
    def from_file(
        cls,
        file_id: str,
        file_path: Path | str,
        expires: float | None = None,
        updated_at: datetime | None = None,
    ) -> Self:
        mtime = Path(file_path).stat().st_mtime
        return cls(
            file_id=file_id,
            mtime=mtime,
            expires=expires,
            updated_at=updated_at or datetime.now(),
        )
