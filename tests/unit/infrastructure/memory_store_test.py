import pytest

from src.domain.entities.user_session import UserSession
from src.domain.ports import StateStore
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store.memory_store import MemoryStateStore

ROOT_NODE = "root"


@pytest.fixture
def state_store():
    return MemoryStateStore()


def test_state_store_is_abstract():
    with pytest.raises(TypeError):
        StateStore()


@pytest.mark.asyncio
async def test_in_memory_state_store_can_be_instantiated(state_store):
    assert isinstance(state_store, StateStore)
    assert isinstance(state_store, MemoryStateStore)


@pytest.mark.asyncio
async def test_create_or_reset_sets_session(state_store, user_key):
    session = await state_store.create_or_reset(user_key, ROOT_NODE)
    assert isinstance(session, UserSession)
    assert session.user_key == user_key
    assert session.history == [ROOT_NODE]
    assert await state_store.get_session(user_key) is session


@pytest.mark.asyncio
async def test_get_session_returns_none_for_unknown_key(state_store, user_key):
    assert await state_store.get_session(user_key) is None


@pytest.mark.asyncio
async def test_push_node_appends_to_history(state_store, user_key):
    await state_store.create_or_reset(user_key, ROOT_NODE)
    await state_store.push_node(user_key, "node1")
    await state_store.push_node(user_key, "node2")
    session = await state_store.get_session(user_key)
    assert session.history == [ROOT_NODE, "node1", "node2"]


@pytest.mark.asyncio
async def test_pop_node_removes_last_and_returns_it(state_store, user_key):
    await state_store.create_or_reset(user_key, ROOT_NODE)
    await state_store.push_node(user_key, "a")
    await state_store.push_node(user_key, "b")
    popped = await state_store.pop_node(user_key)
    assert popped == "b"
    session = await state_store.get_session(user_key)
    assert session.history == [ROOT_NODE, "a"]
    popped2 = await state_store.pop_node(user_key)
    assert popped2 == "a"
    session = await state_store.get_session(user_key)
    assert session.history == [ROOT_NODE]
    popped3 = await state_store.pop_node(user_key)
    assert popped3 is None
    session = await state_store.get_session(user_key)
    assert session.history == [ROOT_NODE]


@pytest.mark.asyncio
async def test_clear_removes_session(state_store, user_key):
    await state_store.create_or_reset(user_key, ROOT_NODE)
    assert await state_store.get_session(user_key) is not None
    await state_store.clear(user_key)
    assert await state_store.get_session(user_key) is None


@pytest.mark.asyncio
async def test_isolation_between_different_keys(state_store, user_key):
    key2 = UserKey(Network.VK, "1")
    await state_store.create_or_reset(user_key, ROOT_NODE)
    await state_store.create_or_reset(key2, "root2")

    assert (await state_store.get_session(user_key)).history == [ROOT_NODE]
    assert (await state_store.get_session(key2)).history == ["root2"]
    await state_store.push_node(user_key, "nodeA")
    await state_store.push_node(key2, "nodeB")
    assert (await state_store.get_session(user_key)).history == [ROOT_NODE, "nodeA"]
    assert (await state_store.get_session(key2)).history == ["root2", "nodeB"]
