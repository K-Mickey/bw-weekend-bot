from src.domain.aggregates import Content


class ContentRepository:
    @staticmethod
    def get_node(node_id: str) -> Content | None:
        """
        Retrieve a content node by its ID.
        Returns None if the node is not found.
        """
        return None
