import asyncio

import pytest

from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store.sqlite_store import SQLiteStateStore


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


@pytest.mark.asyncio
async def test_get_instance(sqlite_store):
    instance = await SQLiteStateStore.get_instance()
    assert instance._instance is not None

    same_instance = await SQLiteStateStore.get_instance()
    assert instance is same_instance


@pytest.mark.asyncio
async def test_get_empty_history(sqlite_store, user_key):
    assert await sqlite_store.get_history(user_key) == ()


@pytest.mark.asyncio
async def test_set_history(sqlite_store, user_key):
    await sqlite_store.set_history(user_key, ("root", "node1", "node2"))
    assert await sqlite_store.get_history(user_key) == ("root", "node1", "node2")


@pytest.mark.asyncio
async def test_get_current_state(sqlite_store, user_key):
    await sqlite_store.set_history(user_key, ("root", "node1"))
    state = await sqlite_store.get_current_state(user_key)
    assert state == "node1"


@pytest.mark.asyncio
async def test_get_current_state_returns_none_for_unknown_key(sqlite_store, user_key):
    assert await sqlite_store.get_current_state(user_key) is None


@pytest.mark.asyncio
async def test_push_node_appends_to_history(sqlite_store, user_key):
    await sqlite_store.append(user_key, "node1")
    await sqlite_store.append(user_key, "node2")
    history = await sqlite_store.get_history(user_key)
    assert history == ("node1", "node2")


@pytest.mark.asyncio
async def test_pop_node_removes_last_and_returns_it(sqlite_store, user_key):
    await sqlite_store.append(user_key, "a")
    await sqlite_store.append(user_key, "b")
    popped = await sqlite_store.pop(user_key)
    assert popped == "b"
    history = await sqlite_store.get_history(user_key)
    assert history == ("a",)
    popped2 = await sqlite_store.pop(user_key)
    assert popped2 == "a"
    history = await sqlite_store.get_history(user_key)
    assert history == ()
    popped3 = await sqlite_store.pop(user_key)
    assert popped3 is None


@pytest.mark.asyncio
async def test_clear_removes_session(sqlite_store, user_key):
    await sqlite_store.set_history(user_key, ("root", "node1"))
    assert await sqlite_store.get_current_state(user_key) is not None
    await sqlite_store.clear(user_key)
    assert await sqlite_store.get_current_state(user_key) is None


@pytest.mark.asyncio
async def test_isolation_between_different_keys(sqlite_store, user_key):
    key2 = UserKey(Network.VK, "1")
    await sqlite_store.set_history(user_key, ("root",))
    await sqlite_store.set_history(key2, ("root2",))

    assert await sqlite_store.get_current_state(user_key) == "root"
    assert await sqlite_store.get_current_state(key2) == "root2"
    await sqlite_store.append(user_key, "nodeA")
    await sqlite_store.append(key2, "nodeB")
    assert await sqlite_store.get_history(user_key) == ("root", "nodeA")
    assert await sqlite_store.get_history(key2) == ("root2", "nodeB")


@pytest.mark.asyncio
async def test_persistence_after_reconnect(sqlite_store, user_key, tmp_path):
    await sqlite_store.set_history(user_key, ("root", "node1"))

    await sqlite_store.close()
    SQLiteStateStore._instance = None
    new_store = await SQLiteStateStore.get_instance()

    assert await new_store.get_history(user_key) == ("root", "node1")

    await new_store.close()
