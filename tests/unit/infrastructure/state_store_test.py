import pytest

from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.domain.value_objects.user_session import UserSession
from src.infrastructure.state_store.base import StateStore
from src.infrastructure.state_store.memory_store import InMemoryStateStore


def test_state_store_is_abstract():
    with pytest.raises(TypeError):
        StateStore()


def test_in_memory_state_store_can_be_instantiated():
    store = InMemoryStateStore()
    assert isinstance(store, StateStore)
    assert isinstance(store, InMemoryStateStore)


def test_create_or_reset_sets_session():
    store = InMemoryStateStore()
    user_key = UserKey(Network.TELEGRAM, "123")
    root_node_id = "root"
    session = store.create_or_reset(user_key, root_node_id)
    assert isinstance(session, UserSession)
    assert session.user_key == user_key
    assert session.history == [root_node_id]
    assert store.get_session(user_key) is session


def test_get_session_returns_none_for_unknown_key():
    store = InMemoryStateStore()
    assert store.get_session(UserKey(Network.TELEGRAM, "unknown")) is None


def test_push_node_appends_to_history():
    store = InMemoryStateStore()
    user_key = UserKey(Network.VK, "456")
    root = "start"
    store.create_or_reset(user_key, root)
    store.push_node(user_key, "node1")
    store.push_node(user_key, "node2")
    session = store.get_session(user_key)
    assert session.history == [root, "node1", "node2"]


def test_pop_node_removes_last_and_returns_it():
    store = InMemoryStateStore()
    user_key = UserKey(Network.TELEGRAM, "789")
    root = "home"
    store.create_or_reset(user_key, root)
    store.push_node(user_key, "a")
    store.push_node(user_key, "b")
    popped = store.pop_node(user_key)
    assert popped == "b"
    session = store.get_session(user_key)
    assert session.history == [root, "a"]
    popped2 = store.pop_node(user_key)
    assert popped2 == "a"
    session = store.get_session(user_key)
    assert session.history == [root]
    popped3 = store.pop_node(user_key)
    assert popped3 is None
    session = store.get_session(user_key)
    assert session.history == [root]


def test_clear_removes_session():
    store = InMemoryStateStore()
    user_key = UserKey(Network.TELEGRAM, "111")
    store.create_or_reset(user_key, "root")
    assert store.get_session(user_key) is not None
    store.clear(user_key)
    assert store.get_session(user_key) is None


def test_isolation_between_different_keys():
    store = InMemoryStateStore()
    key1 = UserKey(Network.TELEGRAM, "1")
    key2 = UserKey(Network.VK, "1")
    store.create_or_reset(key1, "root1")
    store.create_or_reset(key2, "root2")
    assert store.get_session(key1).history == ["root1"]
    assert store.get_session(key2).history == ["root2"]
    store.push_node(key1, "nodeA")
    store.push_node(key2, "nodeB")
    assert store.get_session(key1).history == ["root1", "nodeA"]
    assert store.get_session(key2).history == ["root2", "nodeB"]
