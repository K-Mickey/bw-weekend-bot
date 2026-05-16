from src.domain.value_objects.network import Network


def test_network_enum_has_expected_values():
    assert Network.TELEGRAM.value == "tg"
    assert Network.VK.value == "vk"


def test_network_enum_string_representation():
    assert str(Network.TELEGRAM) == "tg"
    assert str(Network.VK) == "vk"


def test_network_enum_is_unique():
    assert Network.TELEGRAM != Network.VK
