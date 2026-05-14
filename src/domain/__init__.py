"""Domain package public API.

Re‑exports the factory function used throughout the codebase.
"""

from .factories.node_factory import node_factory

__all__ = ["node_factory"]
