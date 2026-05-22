from unittest.mock import patch

import pytest

from src.application.usecases.navigate import navigate
from src.domain.aggregates.menu_node import MenuNode
from src.domain.entities.button_type import ButtonType
from src.domain.entities.keyboard_button import KeyboardButton


@pytest.fixture
def mock_store():
    with patch("src.application.usecases.navigate.state_store") as mock:
        yield mock


@pytest.fixture
def mock_get_content():
    with patch("src.application.usecases.navigate.get_content") as mock:
        yield mock


def empty_node(node_id: str) -> MenuNode:
    return MenuNode(
        id=node_id,
        content=[],
        keyboard=[[]],
    )


def test_navigate_forward(user_key, session, mock_store, mock_get_content):
    current_node_id = "node_a"
    button_label = "Go to B"
    target_node_id = "node_b"

    mock_session = session
    mock_session.history = ["main", current_node_id]

    mock_current_node = MenuNode(
        id=current_node_id,
        content=[],
        keyboard=[
            [
                KeyboardButton(text=button_label, target=target_node_id, type=ButtonType.DEFAULT),
                KeyboardButton(text="Other", target="node_c"),
            ]
        ],
    )

    mock_target_response = empty_node(target_node_id)

    mock_store.get_session.return_value = mock_session
    mock_get_content.side_effect = [mock_current_node, mock_target_response]

    result = navigate(user_key.network, user_key.external_id, button_label)

    mock_store.push_node.assert_called_once_with(user_key, target_node_id)
    assert result == mock_target_response


def test_navigate_back(user_key, session, mock_store, mock_get_content):
    current_node_id = "node_x"
    button_label = "Back"
    mock_session = session
    mock_session.history = ["main", "node_a", current_node_id]

    mock_current_node = MenuNode(
        id=current_node_id,
        content=[],
        keyboard=[[KeyboardButton(text=button_label, target="node_a", type=ButtonType.BACK)]],
    )

    mock_expected_response = empty_node("node_a")

    mock_store.get_session.return_value = mock_session

    def mock_pop_node(key):
        if mock_session.history:
            return mock_session.history.pop()
        return None

    mock_store.pop_node.side_effect = mock_pop_node
    mock_get_content.side_effect = [mock_current_node, mock_expected_response]

    result = navigate(user_key.network, user_key.external_id, button_label)

    mock_store.pop_node.assert_called_once_with(user_key)
    assert result == mock_expected_response


def test_navigate_back_at_root(user_key, session, mock_store, mock_get_content):
    current_node_id = "main"
    button_label = "Back"

    mock_session = session
    mock_session.history = ["main"]

    mock_response = MenuNode(
        id=current_node_id,
        content=[],
        keyboard=[[KeyboardButton(text=button_label, target="main", type=ButtonType.BACK)]],
    )

    mock_store.get_session.return_value = mock_session
    mock_store.pop_node.return_value = None
    mock_get_content.side_effect = [mock_response, mock_response]

    result = navigate(user_key.network, user_key.external_id, button_label)

    mock_store.pop_node.assert_called_once_with(user_key)
    assert result == mock_response


def test_navigate_invalid_button(user_key, session, mock_store, mock_get_content):
    current_node_id = "node_id"
    button_label = "NonExistentButton"
    mock_session = session
    mock_session.history = ["main", current_node_id]

    mock_current_node = empty_node(current_node_id)

    mock_store.get_session.return_value = mock_session
    mock_get_content.return_value = mock_current_node

    with pytest.raises(ValueError) as exc_info:
        navigate(user_key.network, user_key.external_id, button_label)

    assert "Button not found" in str(exc_info.value)
    mock_store.push_node.assert_not_called()
