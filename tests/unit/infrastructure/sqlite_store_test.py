import asyncio

import pytest

from src.domain.value_objects.network import Network
from src.domain.value_objects.node import NodeName
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
async def test_get_session_returns_none_for_unknown_key(sqlite_store, user_key):
    assert await sqlite_store.get_session(user_key) is None


@pytest.mark.asyncio
async def test_create_or_reset_sets_session(sqlite_store, user_key):
    session = await sqlite_store.create_or_reset(user_key, NodeName.ROOT)
    assert session.user_key == user_key
    assert session.history == [NodeName.ROOT]
    assert await sqlite_store.get_session(user_key) is not None


@pytest.mark.asyncio
async def test_push_node_appends_to_history(sqlite_store, user_key):
    await sqlite_store.create_or_reset(user_key, NodeName.ROOT)
    await sqlite_store.push_node(user_key, "node1")
    await sqlite_store.push_node(user_key, "node2")
    session = await sqlite_store.get_session(user_key)
    assert session.history == [NodeName.ROOT, "node1", "node2"]


@pytest.mark.asyncio
async def test_pop_node_removes_last_and_returns_it(sqlite_store, user_key):
    await sqlite_store.create_or_reset(user_key, NodeName.ROOT)
    await sqlite_store.push_node(user_key, "a")
    await sqlite_store.push_node(user_key, "b")
    popped = await sqlite_store.pop_node(user_key)
    assert popped == "b"
    session = await sqlite_store.get_session(user_key)
    assert session.history == [NodeName.ROOT, "a"]
    popped2 = await sqlite_store.pop_node(user_key)
    assert popped2 == "a"
    session = await sqlite_store.get_session(user_key)
    assert session.history == [NodeName.ROOT]
    popped3 = await sqlite_store.pop_node(user_key)
    assert popped3 is None
    session = await sqlite_store.get_session(user_key)
    assert session.history == [NodeName.ROOT]


@pytest.mark.asyncio
async def test_clear_removes_session(sqlite_store, user_key):
    await sqlite_store.create_or_reset(user_key, NodeName.ROOT)
    assert await sqlite_store.get_session(user_key) is not None
    await sqlite_store.clear(user_key)
    assert await sqlite_store.get_session(user_key) is None


@pytest.mark.asyncio
async def test_isolation_between_different_keys(sqlite_store, user_key):
    key2 = UserKey(Network.VK, "1")
    await sqlite_store.create_or_reset(user_key, NodeName.ROOT)
    await sqlite_store.create_or_reset(key2, "root2")
    assert (await sqlite_store.get_session(user_key)).history == [NodeName.ROOT]
    assert (await sqlite_store.get_session(key2)).history == ["root2"]
    await sqlite_store.push_node(user_key, "nodeA")
    await sqlite_store.push_node(key2, "nodeB")
    assert (await sqlite_store.get_session(user_key)).history == [NodeName.ROOT, "nodeA"]
    assert (await sqlite_store.get_session(key2)).history == ["root2", "nodeB"]


@pytest.mark.asyncio
async def test_persistence_after_reconnect(sqlite_store, user_key, tmp_path):
    await sqlite_store.create_or_reset(user_key, NodeName.ROOT)
    await sqlite_store.push_node(user_key, "node1")
    await sqlite_store.push_node(user_key, "node2")

    await sqlite_store.close()
    SQLiteStateStore._instance = None
    new_store = await SQLiteStateStore.get_instance()

    session = await new_store.get_session(user_key)
    assert session is not None
    assert session.history == [NodeName.ROOT, "node1", "node2"]

    await new_store.close()
