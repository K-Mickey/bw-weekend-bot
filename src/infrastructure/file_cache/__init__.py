"""Convenient public interface for the file‑cache subsystem.

The package provides:
    - :class:`MediaCache` and :class:`MediaCacheMiss` from ``base``.
    - A default in‑memory implementation (:class:`InMemoryMediaCache`).
    - An async helper ``get_cache()`` that returns a singleton instance of the
      in‑memory cache.  This mirrors the pattern used by ``InMemoryStateStore``.
"""

from .base import MediaCache
from .in_memory import InMemoryMediaCache


async def get_cache() -> MediaCache:
    """Return the singleton in‑memory cache instance.

    If a different implementation is desired later (e.g. SQLite), replace the
    body of this function accordingly.
    """
    return await InMemoryMediaCache.get_instance()
