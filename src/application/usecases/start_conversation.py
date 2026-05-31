from src.application.usecases.get_content import get_current_content
from src.domain.aggregates import Content
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store import state_store


def start_conversation(network: Network, external_user_id: int | str) -> Content:
    """
    Start a new conversation for the user identified by network and external_user_id.
    Returns the content for the root node (defined as 'main').
    """
    user_key = UserKey(network, str(external_user_id))
    state_store.create_or_reset(user_key, NodeName.ROOT)
    return get_current_content(user_key)
