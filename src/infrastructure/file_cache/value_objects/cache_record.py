from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Self


class CacheRecord(NamedTuple):
    file_id: str
    mtime: float
    expires: float | None
    updated_at: datetime | None

    @classmethod
    def from_file(
        cls,
        file_id: str,
        file_path: Path | str,
        expires: float | None = None,
    ) -> Self:
        file_path = Path(file_path)
        mtime = file_path.stat().st_mtime
        return cls(
            file_id=file_id,
            mtime=mtime,
            expires=expires,
            updated_at=None,
        )
