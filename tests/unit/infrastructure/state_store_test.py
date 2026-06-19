import asyncio

import pytest

from src.domain.ports import StateStore
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store import SQLiteStateStore
from src.infrastructure.state_store.memory_store import MemoryStateStore


@pytest.fixture
def memory_store():
    return MemoryStateStore()


@pytest.fixture
def sqlite_store(tmp_path):
    original_path = SQLiteStateStore._db_path
    SQLiteStateStore._db_path = str(tmp_path / "test_state.db")
    store = asyncio.run(SQLiteStateStore.get_instance())
    try:
        yield store
    finally:
        asyncio.run(store.close())
        SQLiteStateStore._instance = None
        SQLiteStateStore._db_path = original_path


@pytest.fixture(params=["memory_store", "sqlite_store"])
def state_store(request):
    fixture_value = request.getfixturevalue(request.param)
    return fixture_value


@pytest.mark.parametrize("state_cls", [MemoryStateStore, SQLiteStateStore])
async def test_get_memory_instance(state_cls):
    instance = await state_cls.get_instance()
    assert instance._instance is not None

    same_instance = await state_cls.get_instance()
    assert instance is same_instance


async def test_in_memory_state_store_can_be_instantiated(state_store):
    assert isinstance(state_store, StateStore)


async def test_get_empty_history(state_store, user_key):
    assert await state_store.get_history(user_key) == ()


async def test_set_history(state_store, user_key):
    await state_store.set_history(user_key, ("root", "node1", "node2"))
    assert await state_store.get_history(user_key) == ("root", "node1", "node2")


async def test_get_current_state(state_store, user_key):
    await state_store.set_history(user_key, ("root", "node1"))
    state = await state_store.get_current_state(user_key)
    assert state == "node1"


async def test_get_current_state_returns_none_for_unknown_key(state_store, user_key):
    assert await state_store.get_current_state(user_key) is None


async def test_push_node_appends_to_history(state_store, user_key):
    await state_store.append(user_key, "node1")
    await state_store.append(user_key, "node2")
    history = await state_store.get_history(user_key)
    assert history == ("node1", "node2")


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


async def test_clear_removes_session(state_store, user_key):
    await state_store.set_history(user_key, ("root", "node1"))
    assert await state_store.get_current_state(user_key) is not None
    await state_store.clear(user_key)
    assert await state_store.get_current_state(user_key) is None


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


async def test_persistence_after_reconnect(sqlite_store, user_key):
    await sqlite_store.set_history(user_key, ("root", "node1"))
    await sqlite_store.close()

    sqlite_store.__class__._instance = None
    new_store = await sqlite_store.get_instance()

    history = await new_store.get_history(user_key)
    assert history == ("root", "node1")
    await new_store.close()
