from src.application.button_helper import add_automatic_buttons
from src.domain.aggregates import Content
from src.domain.value_objects.user_session import UserSession
from src.infrastructure.content_repository import ContentRepository


def get_content(session: UserSession) -> Content:
    """
    Retrieve content for the given node ID and present it as a ContentResponse.
    Raises an exception if the node is not found.
    If session is provided, applies automatic button logic for MenuNodes.
    """
    node_id = session.current

    node = ContentRepository.get_node(node_id)
    if node is None:
        raise ValueError(f"Node not found: {node_id}")

    add_automatic_buttons(node, session)

    return node
