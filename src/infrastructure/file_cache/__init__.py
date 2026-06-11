"""Convenient public interface for the file‑cache subsystem.

The package provides:
    - :class:`MediaCache` and :class:`MediaCacheMiss` from ``base``.
    - A default in‑memory implementation (:class:`InMemoryMediaCache`).
    - An SQLite implementation (:class:`SQLiteMediaCache`).
    - An async helper ``get_cache()`` that returns a singleton instance of the
      in‑memory cache.  This mirrors the pattern used by ``InMemoryStateStore``.
"""

from .base import MediaCache
from .in_memory import InMemoryMediaCache
from .sqlite import SQLiteMediaCache
