import logging

from src.application.keyboard_helper import add_automatic_buttons, find_target_button_in_content
from src.domain.aggregates import Content
from src.domain.exceptions import ButtonNotFoundError, ContentNotFoundError
from src.domain.ports import StateStore
from src.domain.ports.content_repository import ContentRepository
from src.domain.value_objects.button import ButtonType
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.domain.value_objects.user_key import UserKey

logger = logging.getLogger(__name__)


class NavigationService:
    def __init__(self, state_store: StateStore, content_repository: ContentRepository):
        self.state_store = state_store
        self.content_repository = content_repository

    def get_content_by_id(self, content_id: str) -> Content:
        logger.debug(f"Getting content by id: {content_id}")
        content = self.content_repository.get_content(content_id)
        if content is None:
            raise ContentNotFoundError(content_id)
        return content

    async def build_current_content(self, user_key: UserKey) -> Content:
        logger.debug(f"Getting current content for user: {user_key}")

        content_id = await self.state_store.get_current_state(user_key)
        if not content_id:
            logger.debug(f"User {user_key} has no current state, return ROOT content")
            await self.state_store.append(user_key, NodeName.ROOT)
            content_id = NodeName.ROOT

        content = self.get_content_by_id(content_id)

        history = await self.state_store.get_history(user_key)
        add_automatic_buttons(content, history)

        return content

    async def start_conversation(self, network: Network, external_user_id: int | str) -> Content:
        user_key = UserKey(network, str(external_user_id))
        logger.debug(f"Starting conversation for user: {user_key}")
        await self.state_store.clear(user_key)
        return await self.build_current_content(user_key)

    async def navigate(
        self,
        network: Network,
        external_user_id: int | str,
        button_label: str,
    ) -> Content:
        user_key = UserKey(network, str(external_user_id))
        logger.debug(f"Navigating to {button_label} for user: {user_key}")

        start_content = await self.build_current_content(user_key)
        if not start_content:
            logger.warning(f"User {user_key} has no session or current state")
            return await self.build_current_content(user_key)

        button = find_target_button_in_content(start_content, button_label)
        if not button:
            raise ButtonNotFoundError(button_label)

        match button.type:
            case ButtonType.MAIN_MENU:
                return await self.start_conversation(network, external_user_id)

            case ButtonType.BACK:
                await self.state_store.pop(user_key)

            case _:
                await self.state_store.append(user_key, button.target)

        return await self.build_current_content(user_key)
