import logging
from pathlib import Path

import yaml

from src.config import settings
from src.domain.aggregates import Content
from src.domain.factories import content_factory

logger = logging.getLogger(__name__)


class ContentException(Exception):
    pass


class ContentNotFoundException(ContentException):
    pass


class ContentRepository:
    def __init__(self):
        self.data_dir = settings.content_data_dir

    def get_node(self, node_id: str) -> Content | None:
        """
        Retrieve a content node by its ID.
        Returns None if the node is not found.
        """
        file_path = self.data_dir / f"{node_id}.yaml"
        if not file_path.exists():
            return None
        return self._create_content_from_file(file_path)

    def get_file(self, file_name: str | Path) -> Content | None:
        file_path = self.data_dir / file_name
        if not file_path.exists():
            return None
        return self._create_content_from_file(file_path)

    @staticmethod
    def _create_content_from_file(file_path: Path) -> Content | None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            return content_factory(raw)
        except Exception as e:
            logger.error(f"Failed to load content from {file_path}: {e}")
            return None
