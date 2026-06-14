from src.application.keyboard_helper import add_automatic_buttons, find_target_button_in_content
from src.domain.aggregates import Content
from src.domain.exceptions import ButtonNotFoundError, ContentNotFoundError
from src.domain.ports import StateStore
from src.domain.ports.content_repository import ContentRepository
from src.domain.value_objects.button import ButtonType
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.domain.value_objects.user_key import UserKey


class NavigationService:
    def __init__(self, state_store: StateStore, content_repository: ContentRepository):
        self.state_store = state_store
        self.content_repository = content_repository

    def get_content_by_id(self, node_id: str) -> Content:
        node = self.content_repository.get_content(node_id)
        if node is None:
            raise ContentNotFoundError(node_id)
        return node

    async def get_current_content(self, user_key: UserKey) -> Content:
        session = await self.state_store.get_session(user_key)
        node_id = session.current

        node = self.get_content_by_id(node_id)
        add_automatic_buttons(node, session)

        return node

    async def start_conversation(self, network: Network, external_user_id: int | str) -> Content:
        user_key = UserKey(network, str(external_user_id))
        await self.state_store.create_or_reset(user_key, NodeName.ROOT)
        return await self.get_current_content(user_key)

    async def navigate(
        self,
        network: Network,
        external_user_id: int | str,
        button_label: str,
    ) -> Content:
        user_key = UserKey(network, str(external_user_id))
        current_node = await self.get_current_content(user_key)

        button = find_target_button_in_content(current_node, button_label)
        if not button:
            raise ButtonNotFoundError(button_label)

        match button.type:
            case ButtonType.MAIN_MENU:
                await self.state_store.create_or_reset(user_key, NodeName.ROOT)

            case ButtonType.BACK:
                await self.state_store.pop_node(user_key)

            case _:
                await self.state_store.push_node(user_key, button.target)

        return await self.get_current_content(user_key)
