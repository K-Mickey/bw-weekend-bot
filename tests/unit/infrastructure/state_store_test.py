import pytest

from src.domain.entities.user_session import UserSession
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.infrastructure.state_store.base import StateStore
from src.infrastructure.state_store.memory_store import InMemoryStateStore

ROOT_NODE = "root"


@pytest.fixture
def state_store():
    return InMemoryStateStore()


@pytest.fixture
def root_with_session(state_store, user_key):
    state_store.create_or_reset(user_key, ROOT_NODE)
    return state_store


def test_state_store_is_abstract():
    with pytest.raises(TypeError):
        StateStore()


def test_in_memory_state_store_can_be_instantiated(state_store):
    assert isinstance(state_store, StateStore)
    assert isinstance(state_store, InMemoryStateStore)


def test_create_or_reset_sets_session(state_store, user_key):
    session = state_store.create_or_reset(user_key, ROOT_NODE)
    assert isinstance(session, UserSession)
    assert session.user_key == user_key
    assert session.history == [ROOT_NODE]
    assert state_store.get_session(user_key) is session


def test_get_session_returns_none_for_unknown_key(state_store, user_key):
    assert state_store.get_session(user_key) is None


def test_push_node_appends_to_history(root_with_session, user_key):
    root_with_session.push_node(user_key, "node1")
    root_with_session.push_node(user_key, "node2")
    session = root_with_session.get_session(user_key)
    assert session.history == [ROOT_NODE, "node1", "node2"]


def test_pop_node_removes_last_and_returns_it(root_with_session, user_key):
    root_with_session.push_node(user_key, "a")
    root_with_session.push_node(user_key, "b")
    popped = root_with_session.pop_node(user_key)
    assert popped == "b"
    session = root_with_session.get_session(user_key)
    assert session.history == [ROOT_NODE, "a"]
    popped2 = root_with_session.pop_node(user_key)
    assert popped2 == "a"
    session = root_with_session.get_session(user_key)
    assert session.history == [ROOT_NODE]
    popped3 = root_with_session.pop_node(user_key)
    assert popped3 is None
    session = root_with_session.get_session(user_key)
    assert session.history == [ROOT_NODE]


def test_clear_removes_session(root_with_session, user_key):
    assert root_with_session.get_session(user_key) is not None
    root_with_session.clear(user_key)
    assert root_with_session.get_session(user_key) is None


def test_isolation_between_different_keys(root_with_session, user_key):
    key2 = UserKey(Network.VK, "1")
    root_with_session.create_or_reset(key2, "root2")
    assert root_with_session.get_session(user_key).history == [ROOT_NODE]
    assert root_with_session.get_session(key2).history == ["root2"]
    root_with_session.push_node(user_key, "nodeA")
    root_with_session.push_node(key2, "nodeB")
    assert root_with_session.get_session(user_key).history == [ROOT_NODE, "nodeA"]
    assert root_with_session.get_session(key2).history == ["root2", "nodeB"]
