from src.application.button_helper import add_automatic_buttons
from src.domain.aggregates import Content
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.content_repository import ContentNotFoundException, ContentRepository
from src.infrastructure.state_store import state_store


def get_current_content(user_key: UserKey) -> Content:
    """
    Retrieve content for the current node and present it as a ContentResponse.
    Raises an exception if the node is not found.
    If session is provided, applies automatic button logic for MenuNodes.
    """
    session = state_store.get_session(user_key)
    node_id = session.current

    node = get_content_by_id(node_id)
    add_automatic_buttons(node, session)

    return node


def get_content_by_id(node_id: str) -> Content:
    """
    Retrieve content for the given node ID and present it as a ContentResponse.
    Raises an exception if the node is not found.
    Be aware that automatic button logic is not applied.
    """
    node = ContentRepository.get_node(node_id)
    if node is None:
        raise ContentNotFoundException(f"Node not found: {node_id}")

    return node
