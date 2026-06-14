import pytest

from src.application.services import NavigationService
from src.domain.aggregates import Content
from src.domain.exceptions import ContentNotFoundError
from src.domain.ports import StateStore
from src.domain.ports.content_repository import ContentRepository


@pytest.fixture
def navigate_service(state_store: StateStore, content_repository: ContentRepository):
    return NavigationService(state_store, content_repository)


def test_get_content_by_id(navigate_service: NavigationService):
    node_id = "main"
    content = navigate_service.get_content_by_id(node_id)
    assert content.id == node_id
    assert isinstance(content, Content)


def test_get_content_by_id_not_found(navigate_service: NavigationService):
    node_id = "not_found"
    with pytest.raises(ContentNotFoundError):
        navigate_service.get_content_by_id(node_id)


"""
fact:

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

"""
"""
references:


PRICE_LABEL = "Цены"
PRICE_ID = "prices"
CONTACTS_LABEL = "Контакты"
CONTACTS_ID = "contacts"


@pytest.mark.asyncio
async def test_navigate_forward(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    assert (await state_store.get_session(user_key)).current == NodeName.ROOT

    content = await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)

    assert isinstance(content, Content)
    session = await state_store.get_session(user_key)
    assert session.current == PRICE_ID
    assert session.history == [NodeName.ROOT, PRICE_ID]


@pytest.mark.asyncio
async def test_navigate_forward_content(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    content = await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)

    assert isinstance(content, Post)
    assert content.id == PRICE_ID
    assert content.media == Text(text="Prices")

    assert len(content.keyboard) == 2
    assert len(content.keyboard[0]) == 1
    assert content.keyboard[0][0].text == CONTACTS_LABEL

    assert len(content.keyboard[1]) == 1
    assert content.keyboard[1][0].text == BaseButton.MAIN_MENU


@pytest.mark.asyncio
async def test_navigate_unexpected_button(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    with pytest.raises(ButtonNotFoundException):
        await navigate(state_store, user_key.network, user_key.external_id, "unexpected_button")


@pytest.mark.asyncio
async def test_navigate_not_found_content(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    with pytest.raises(ContentNotFoundException):
        await navigate(state_store, user_key.network, user_key.external_id, "Локации")


@pytest.mark.asyncio
async def test_navigate_second_forward(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)

    content = await navigate(state_store, user_key.network, user_key.external_id, CONTACTS_LABEL)

    assert (await state_store.get_session(user_key)).current == CONTACTS_ID
    assert (await state_store.get_session(user_key)).history == [NodeName.ROOT, PRICE_ID, CONTACTS_ID]

    assert isinstance(content, Post)
    assert content.id == CONTACTS_ID
    assert content.media == Text(text="Contacts")

    assert len(content.keyboard) == 1
    assert len(content.keyboard[0]) == 2
    assert content.keyboard[0][0].text == BaseButton.MAIN_MENU
    assert content.keyboard[0][1].text == BaseButton.BACK


@pytest.mark.asyncio
async def test_navigate_main_menu(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)
    await navigate(state_store, user_key.network, user_key.external_id, CONTACTS_LABEL)

    await navigate(state_store, user_key.network, user_key.external_id, BaseButton.MAIN_MENU)

    assert (await state_store.get_session(user_key)).current == NodeName.ROOT
    assert (await state_store.get_session(user_key)).history == [NodeName.ROOT]


@pytest.mark.asyncio
async def test_navigate_back(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)
    await navigate(state_store, user_key.network, user_key.external_id, CONTACTS_LABEL)

    await navigate(state_store, user_key.network, user_key.external_id, BaseButton.BACK)

    assert (await state_store.get_session(user_key)).current == PRICE_ID
    assert (await state_store.get_session(user_key)).history == [NodeName.ROOT, PRICE_ID]


@pytest.mark.parametrize(
    "network, external_user_id",
    [
        (Network.TELEGRAM, 1),
        (Network.TELEGRAM, "1"),
        (Network.VK, 1),
        (Network.VK, "1"),
    ],
)
@pytest.mark.asyncio
async def test_start_conversation(network, external_user_id, state_store):
    content = await start_conversation(state_store, network, external_user_id)
    assert isinstance(content, Content)

    user_key = UserKey(network, str(external_user_id))
    session = await state_store.get_session(user_key)
    assert session is not None
    assert session.current == NodeName.ROOT


@pytest.mark.asyncio
async def test_start_conversation_with_history(state_store):
    user_key = UserKey(Network.TELEGRAM, "1")
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    await state_store.push_node(user_key, "some")
    await state_store.push_node(user_key, "some2")
    assert (await state_store.get_session(user_key)).history == [NodeName.ROOT, "some", "some2"]

    await start_conversation(state_store, user_key.network, user_key.external_id)
    assert (await state_store.get_session(user_key)).history == [NodeName.ROOT]


@pytest.mark.asyncio
async def test_start_conversation_different_networks(state_store):
    user_key1 = UserKey(Network.TELEGRAM, "1")
    content1 = await start_conversation(state_store, user_key1.network, user_key1.external_id)
    await state_store.push_node(user_key1, "some")

    user_key2 = UserKey(Network.VK, "1")
    content2 = await start_conversation(state_store, user_key2.network, user_key2.external_id)

    assert (await state_store.get_session(user_key1)).history == [NodeName.ROOT, "some"]
    assert (await state_store.get_session(user_key2)).history == [NodeName.ROOT]
    assert content1 == content2
    assert content1 is not content2


@pytest.mark.asyncio
async def test_start_conversation_different_user_ids(state_store):
    user_key1 = UserKey(Network.TELEGRAM, "1")
    await start_conversation(state_store, user_key1.network, user_key1.external_id)
    history1 = (await state_store.get_session(user_key1)).history

    user_key2 = UserKey(Network.TELEGRAM, "2")
    await start_conversation(state_store, user_key2.network, user_key2.external_id)
    await state_store.push_node(user_key2, "some")
    history2 = (await state_store.get_session(user_key2)).history

    assert history1 is not history2
    assert history1 == [NodeName.ROOT]
    assert history2 == [NodeName.ROOT, "some"]

"""
