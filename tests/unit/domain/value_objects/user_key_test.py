from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey


def test_user_key_creation():
    key = UserKey(Network.TELEGRAM, "123")
    assert key.network == Network.TELEGRAM
    assert key.external_id == "123"


def test_user_key_equality():
    key1 = UserKey(Network.TELEGRAM, "123")
    key2 = UserKey(Network.TELEGRAM, "123")
    key3 = UserKey(Network.VK, "123")
    key4 = UserKey(Network.TELEGRAM, "456")
    assert key1 == key2
    assert key1 != key3
    assert key1 != key4


def test_user_key_hashable():
    key = UserKey(Network.TELEGRAM, "123")
    # Should be able to put in a set/dict as key
    s = {key}
    d = {key: "value"}
    assert key in s
    assert d[key] == "value"


def test_user_key_repr():
    key = UserKey(Network.VK, "999")
    repr_str = repr(key)
    assert "UserKey" in repr_str
    assert "Network.VK" in repr_str or "'vk'" in repr_str
    assert "999" in repr_str
