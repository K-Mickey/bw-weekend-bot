import pytest

from src.application.services import NavigationService
from src.domain.aggregates import Content, Post
from src.domain.exceptions import ContentNotFoundError, HistoryNotFoundError
from src.domain.ports import StateStore
from src.domain.ports.content_repository import ContentRepository
from src.domain.value_objects.button import BaseButton
from src.domain.value_objects.media import Text
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.domain.value_objects.user_key import UserKey


@pytest.fixture
def navigation_service(state_store: StateStore, content_repository: ContentRepository):
    return NavigationService(state_store, content_repository)


def test_get_content_by_id(navigation_service: NavigationService):
    node_id = NodeName.ROOT
    content = navigation_service.get_content_by_id(node_id)
    assert content.id == node_id
    assert isinstance(content, Content)


def test_get_content_by_id_not_found(navigation_service: NavigationService):
    node_id = "not_found"
    with pytest.raises(ContentNotFoundError):
        navigation_service.get_content_by_id(node_id)


@pytest.mark.parametrize(
    "history, expected_content_id, expected_history, len_buttons",
    (
        ((NodeName.HELP,), NodeName.HELP, (NodeName.HELP,), 0),
        ((NodeName.HELP, NodeName.ROOT), NodeName.ROOT, (NodeName.HELP, NodeName.ROOT), 7),
        (
            (NodeName.ERROR, NodeName.HELP, NodeName.ROOT),
            NodeName.ROOT,
            (NodeName.ERROR, NodeName.HELP, NodeName.ROOT),
            8,
        ),
    ),
)
async def test_build_current_content(
    navigation_service: NavigationService,
    user_key: UserKey,
    history: tuple,
    expected_content_id: NodeName,
    expected_history: tuple,
    len_buttons: int,
):
    await navigation_service.state_store.set_history(user_key, history)

    content = await navigation_service.build_current_content(user_key)

    assert content.id == expected_content_id
    assert isinstance(content, Post)
    assert len(content.keyboard.get_buttons()) == len_buttons
    assert await navigation_service.state_store.get_history(user_key) == expected_history


async def test_build_current_content_without_history(navigation_service: NavigationService, user_key: UserKey):
    with pytest.raises(HistoryNotFoundError):
        await navigation_service.build_current_content(user_key)


async def test_build_current_content_wrong_history(navigation_service: NavigationService, user_key: UserKey):
    await navigation_service.state_store.set_history(user_key, ["not_found"])
    with pytest.raises(ContentNotFoundError):
        await navigation_service.build_current_content(user_key)


@pytest.mark.parametrize(
    "network, external_user_id",
    [
        (Network.TELEGRAM, 1),
        (Network.TELEGRAM, "1"),
        (Network.VK, 1),
        (Network.VK, "1"),
    ],
)
async def test_start_conversation(
    navigation_service: NavigationService,
    network: Network,
    external_user_id: int | str,
):
    content = await navigation_service.start_conversation(network, external_user_id)
    assert isinstance(content, Content)
    assert content.id == NodeName.ROOT

    user_key = UserKey(network, str(external_user_id))
    history = await navigation_service.state_store.get_history(user_key)
    assert history == (NodeName.ROOT,)


async def test_start_conversation_with_history(navigation_service: NavigationService):
    user_key = UserKey(Network.TELEGRAM, "1")
    await navigation_service.state_store.set_history(user_key, (NodeName.HELP, NodeName.ERROR))

    await navigation_service.start_conversation(user_key.network, user_key.external_id)
    assert await navigation_service.state_store.get_history(user_key) == (NodeName.ROOT,)


async def test_start_conversation_different_networks(navigation_service: NavigationService):
    user_key1 = UserKey(Network.TELEGRAM, "1")
    content1 = await navigation_service.start_conversation(user_key1.network, user_key1.external_id)
    await navigation_service.state_store.append(user_key1, "some")

    user_key2 = UserKey(Network.VK, "1")
    content2 = await navigation_service.start_conversation(user_key2.network, user_key2.external_id)

    assert await navigation_service.state_store.get_history(user_key1) == (NodeName.ROOT, "some")
    assert await navigation_service.state_store.get_history(user_key2) == (NodeName.ROOT,)
    assert content1 == content2
    assert content1 is not content2


async def test_start_conversation_different_user_ids(navigation_service: NavigationService):
    user_key1 = UserKey(Network.TELEGRAM, "1")
    await navigation_service.start_conversation(user_key1.network, user_key1.external_id)
    history1 = await navigation_service.state_store.get_history(user_key1)

    user_key2 = UserKey(Network.TELEGRAM, "2")
    await navigation_service.start_conversation(user_key2.network, user_key2.external_id)
    await navigation_service.state_store.append(user_key2, "some")
    history2 = await navigation_service.state_store.get_history(user_key2)

    assert history1 == (NodeName.ROOT,)
    assert history2 == (NodeName.ROOT, "some")


PRICE_LABEL = "Цены"
PRICE_ID = "prices"
CONTACTS_LABEL = "Контакты"
CONTACTS_ID = "contacts"


async def test_navigate_forward(navigation_service: NavigationService, user_key: UserKey):
    await navigation_service.state_store.set_history(user_key, (NodeName.ROOT,))

    content = await navigation_service.navigate(user_key.network, user_key.external_id, PRICE_LABEL)

    assert isinstance(content, Content)
    assert await navigation_service.state_store.get_history(user_key) == (NodeName.ROOT, PRICE_ID)


async def test_navigate_unexpected_button(navigation_service: NavigationService, user_key: UserKey):
    await navigation_service.state_store.set_history(user_key, (NodeName.ROOT,))
    content = await navigation_service.navigate(user_key.network, user_key.external_id, "unexpected_button")

    assert content.id == NodeName.RETRY
    assert await navigation_service.state_store.get_history(user_key) == (NodeName.ROOT,)


async def test_navigate_not_found_content(navigation_service: NavigationService, user_key: UserKey):
    await navigation_service.state_store.set_history(user_key, (NodeName.ROOT,))
    with pytest.raises(ContentNotFoundError):
        await navigation_service.navigate(user_key.network, user_key.external_id, "Локации")


async def test_navigate_without_history(navigation_service: NavigationService, user_key: UserKey):
    content = await navigation_service.navigate(user_key.network, user_key.external_id, PRICE_LABEL)
    assert content.id == NodeName.ROOT
    assert await navigation_service.state_store.get_history(user_key) == (NodeName.ROOT,)


async def test_navigate_second_forward(navigation_service: NavigationService, user_key: UserKey):
    await navigation_service.state_store.set_history(user_key, (NodeName.ROOT,))

    await navigation_service.navigate(user_key.network, user_key.external_id, PRICE_LABEL)
    content = await navigation_service.navigate(user_key.network, user_key.external_id, CONTACTS_LABEL)

    assert isinstance(content, Post)
    assert content.id == CONTACTS_ID
    assert content.media == Text(text="Contacts")

    assert await navigation_service.state_store.get_current_state(user_key) == CONTACTS_ID
    assert await navigation_service.state_store.get_history(user_key) == (NodeName.ROOT, PRICE_ID, CONTACTS_ID)


async def test_navigate_main_menu(navigation_service: NavigationService, user_key: UserKey):
    await navigation_service.state_store.set_history(user_key, (NodeName.ROOT, PRICE_ID, CONTACTS_ID))
    await navigation_service.navigate(user_key.network, user_key.external_id, BaseButton.MAIN_MENU)
    assert await navigation_service.state_store.get_history(user_key) == (NodeName.ROOT,)


async def test_navigate_back(navigation_service: NavigationService, user_key: UserKey):
    await navigation_service.state_store.set_history(user_key, (NodeName.ROOT, PRICE_ID, CONTACTS_ID))
    await navigation_service.navigate(user_key.network, user_key.external_id, BaseButton.BACK)
    assert await navigation_service.state_store.get_history(user_key) == (NodeName.ROOT, PRICE_ID)
