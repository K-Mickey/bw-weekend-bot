import pytest

from src.domain.ports import StateStore
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store.memory_store import MemoryStateStore


@pytest.fixture
def state_store():
    return MemoryStateStore()


@pytest.mark.asyncio
async def test_get_instance():
    instance = await MemoryStateStore.get_instance()
    assert instance._instance is not None

    same_instance = await MemoryStateStore.get_instance()
    assert instance is same_instance


@pytest.mark.asyncio
async def test_in_memory_state_store_can_be_instantiated(state_store):
    assert isinstance(state_store, StateStore)
    assert isinstance(state_store, MemoryStateStore)


@pytest.mark.asyncio
async def test_get_empty_history(state_store, user_key):
    assert await state_store.get_history(user_key) == ()


@pytest.mark.asyncio
async def test_set_history(state_store, user_key):
    await state_store.set_history(user_key, ("root", "node1", "node2"))
    assert await state_store.get_history(user_key) == ("root", "node1", "node2")


@pytest.mark.asyncio
async def test_get_current_state(state_store, user_key):
    await state_store.set_history(user_key, ("root", "node1"))
    state = await state_store.get_current_state(user_key)
    assert state == "node1"


@pytest.mark.asyncio
async def test_get_current_state_returns_none_for_unknown_key(state_store, user_key):
    assert await state_store.get_current_state(user_key) is None


@pytest.mark.asyncio
async def test_push_node_appends_to_history(state_store, user_key):
    await state_store.append(user_key, "node1")
    await state_store.append(user_key, "node2")
    history = await state_store.get_history(user_key)
    assert history == ("node1", "node2")


@pytest.mark.asyncio
async def test_pop_node_removes_last_and_returns_it(state_store, user_key):
    await state_store.append(user_key, "a")
    await state_store.append(user_key, "b")
    popped = await state_store.pop(user_key)
    assert popped == "b"
    history = await state_store.get_history(user_key)
    assert history == ("a",)
    popped2 = await state_store.pop(user_key)
    assert popped2 == "a"
    history = await state_store.get_history(user_key)
    assert history == ()
    popped3 = await state_store.pop(user_key)
    assert popped3 is None


@pytest.mark.asyncio
async def test_clear_removes_session(state_store, user_key):
    await state_store.set_history(user_key, ("root", "node1"))
    assert await state_store.get_current_state(user_key) is not None
    await state_store.clear(user_key)
    assert await state_store.get_current_state(user_key) is None


@pytest.mark.asyncio
async def test_isolation_between_different_keys(state_store, user_key):
    key2 = UserKey(Network.VK, "1")
    await state_store.set_history(user_key, ("root",))
    await state_store.set_history(key2, ("root2",))

    assert await state_store.get_current_state(user_key) == "root"
    assert await state_store.get_current_state(key2) == "root2"
    await state_store.append(user_key, "nodeA")
    await state_store.append(key2, "nodeB")
    assert await state_store.get_history(user_key) == ("root", "nodeA")
    assert await state_store.get_history(key2) == ("root2", "nodeB")
