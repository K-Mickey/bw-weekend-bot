class MediaCacheError(BaseException):
    """Base exception for cache‑related problems."""


class MediaCacheMiss(MediaCacheError):
    """Raised when a requested cache entry does not exist."""


class MediaCacheExpired(MediaCacheError):
    """Raised when a requested cache entry has expired."""
