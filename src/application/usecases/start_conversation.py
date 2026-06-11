from src.application.usecases.get_content import get_current_content
from src.domain.aggregates import Content
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store import StateStore


async def start_conversation(state_store: StateStore, network: Network, external_user_id: int | str) -> Content:
    """
    Start a new conversation for the user identified by network and external_user_id.
    Returns the content for the root node (defined as 'main').
    """
    user_key = UserKey(network, str(external_user_id))
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    return await get_current_content(state_store, user_key)
