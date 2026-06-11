from src.domain.entities.user_session import UserSession
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey


def test_user_session_creation():
    key = UserKey(Network.TELEGRAM, "user1")
    session = UserSession(user_key=key, history=["root"])
    assert session.user_key == key
    assert session.history == ["root"]


def test_user_session_current(session: UserSession):
    assert session.current == "main"
    session.history.append("node1")
    assert session.current == "node1"


def test_user_session_push(session: UserSession):
    session.push("nodeA")
    session.push("nodeB")
    assert session.history == ["main", "nodeA", "nodeB"]


def test_user_session_pop(session: UserSession):
    session.push("a")
    session.push("b")
    popped = session.pop()
    assert popped == "b"
    assert session.history == ["main", "a"]
    popped2 = session.pop()
    assert popped2 == "a"
    assert session.history == ["main"]
    popped3 = session.pop()
    assert popped3 is None
    assert session.history == ["main"]  # unchanged


def test_user_session_cannot_pop_below_root(session: UserSession):
    assert session.pop() is None
    assert session.history == ["main"]
