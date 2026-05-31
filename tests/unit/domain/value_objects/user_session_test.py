from src.domain.entities.user_session import UserSession
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey


def test_user_session_creation():
    key = UserKey(Network.TELEGRAM, "user1")
    session = UserSession(user_key=key, root_node_id="root")
    assert session.user_key == key
    assert session.history == ["root"]


def test_user_session_current():
    key = UserKey(Network.VK, "user2")
    session = UserSession(user_key=key, root_node_id="home")
    assert session.current == "home"
    session.history.append("node1")
    assert session.current == "node1"


def test_user_session_push():
    key = UserKey(Network.TELEGRAM, "user3")
    session = UserSession(user_key=key, root_node_id="start")
    session.push("nodeA")
    session.push("nodeB")
    assert session.history == ["start", "nodeA", "nodeB"]


def test_user_session_pop():
    key = UserKey(Network.TELEGRAM, "user4")
    session = UserSession(user_key=key, root_node_id="root")
    session.push("a")
    session.push("b")
    popped = session.pop()
    assert popped == "b"
    assert session.history == ["root", "a"]
    popped2 = session.pop()
    assert popped2 == "a"
    assert session.history == ["root"]
    popped3 = session.pop()
    assert popped3 is None
    assert session.history == ["root"]  # unchanged


def test_user_session_cannot_pop_below_root():
    key = UserKey(Network.VK, "user5")
    session = UserSession(user_key=key, root_node_id="base")
    assert session.pop() is None
    assert session.history == ["base"]
