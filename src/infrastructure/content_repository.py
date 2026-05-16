import yaml

from src.config import settings
from src.domain.factories.node_factory import node_factory


class ContentRepository:
    @staticmethod
    def get_node(node_id: str):
        """
        Retrieve a content node by its ID.
        Returns None if the node is not found.
        """
        file_path = settings.content_data_dir / f"{node_id}.yaml"
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
            return node_factory(raw)
        except Exception:
            # In case of YAML parsing error or factory error, return None
            return None
