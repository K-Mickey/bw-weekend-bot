from unittest.mock import patch

import pytest

from src.application.usecases.navigate import navigate
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.keyboard_button import KeyboardButton
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.domain.value_objects.user_session import UserSession


def test_navigate_forward():
    network = Network.TELEGRAM
    external_user_id = "123"
    user_key = UserKey(network, str(external_user_id))
    current_node_id = "node_a"
    button_label = "Go to B"
    target_node_id = "node_b"

    mock_session = UserSession(user_key=user_key, root_node_id="main")
    mock_session.history = ["main", current_node_id]

    mock_current_node = MenuNode(
        id="main",
        content=[],
        keyboard=[
            [
                KeyboardButton(text=button_label, target=target_node_id),
                KeyboardButton(text="Other", target="node_c"),
            ]
        ],
    )

    mock_target_response = MenuNode(
        id="next_node",
        content=[],
        keyboard=[[]],
    )

    with (
        patch("src.application.usecases.navigate.state_store") as mock_store,
        patch("src.application.usecases.navigate.ContentRepository.get_node") as mock_get_node,
        patch("src.application.usecases.navigate.get_content") as mock_get_content,
    ):
        mock_store.get_session.return_value = mock_session
        mock_get_node.return_value = mock_current_node
        mock_get_content.return_value = mock_target_response

        result = navigate(network, external_user_id, button_label)

        mock_store.push_node.assert_called_once_with(user_key, target_node_id)
        mock_get_content.assert_called_once_with(target_node_id)
        assert result == mock_target_response


def test_navigate_back():
    network = Network.VK
    external_user_id = 456
    user_key = UserKey(network, str(external_user_id))
    current_node_id = "node_x"
    button_label = "Back"
    mock_session = UserSession(user_key=user_key, root_node_id="main")
    mock_session.history = ["main", "node_a", current_node_id]

    expected_node_id = "node_a"
    mock_expected_response = MenuNode(
        id=expected_node_id,
        content=[],
        keyboard=[],
    )

    with (
        patch("src.application.usecases.navigate.state_store") as mock_store,
        patch("src.application.usecases.navigate.get_content") as mock_get_content,
    ):
        mock_store.get_session.return_value = mock_session

        def mock_pop_node(key):
            if mock_session.history:
                return mock_session.history.pop()
            return None

        mock_store.pop_node.side_effect = mock_pop_node
        mock_get_content.return_value = mock_expected_response

        result = navigate(network, external_user_id, button_label)

        mock_store.pop_node.assert_called_once_with(user_key)
        mock_get_content.assert_called_once_with(expected_node_id)
        assert result == mock_expected_response


def test_navigate_back_at_root():
    network = Network.TELEGRAM
    external_user_id = "789"
    user_key = UserKey(network, str(external_user_id))
    current_node_id = "main"
    button_label = "Back"

    mock_session = UserSession(user_key=user_key, root_node_id="main")
    mock_session.history = ["main"]

    mock_response = MenuNode(
        id=current_node_id,
        content=[],
        keyboard=[],
    )

    with (
        patch("src.application.usecases.navigate.state_store") as mock_store,
        patch("src.application.usecases.navigate.get_content") as mock_get_content,
    ):
        mock_store.get_session.return_value = mock_session
        mock_store.pop_node.return_value = None
        mock_get_content.return_value = mock_response

        result = navigate(network, external_user_id, button_label)

        mock_store.pop_node.assert_called_once_with(user_key)
        mock_get_content.assert_called_once_with(current_node_id)
        assert result == mock_response


def test_navigate_invalid_button():
    network = Network.VK
    external_user_id = "999"
    user_key = UserKey(network, str(external_user_id))
    current_node_id = "node_id"
    button_label = "NonExistentButton"
    mock_session = UserSession(user_key=user_key, root_node_id="main")
    mock_session.history = ["main", current_node_id]

    mock_current_node = MenuNode(
        id=current_node_id,
        content=[],
        keyboard=[[]],
    )

    with (
        patch("src.application.usecases.navigate.state_store") as mock_store,
        patch("src.application.usecases.navigate.ContentRepository.get_node") as mock_get_node,
    ):
        mock_store.get_session.return_value = mock_session
        mock_get_node.return_value = mock_current_node

        with pytest.raises(ValueError) as exc_info:
            navigate(network, external_user_id, button_label)

        assert "Button not found" in str(exc_info.value)
        mock_store.push_node.assert_not_called()
