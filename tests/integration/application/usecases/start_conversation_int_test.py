import pytest

from src.application.usecases.start_conversation import start_conversation
from src.domain.aggregates import Content
from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
from src.domain.value_objects.user_key import UserKey


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
