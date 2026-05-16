from src.domain.aggregates import Content
from src.infrastructure.content_repository import ContentRepository


def get_content(node_id: str) -> Content:
    """
    Retrieve content for the given node ID and present it as a ContentResponse.
    Raises an exception if the node is not found.
    """
    node = ContentRepository.get_node(node_id)
    if node is None:
        raise ValueError(f"Node not found: {node_id}")
    return node
