from unittest.mock import Mock, patch

import pytest

from src.application.usecases.get_content import get_content_by_id, get_current_content
from src.domain.aggregates.post_node import PostNode

PREFIX = "src.application.usecases.get_content"


@pytest.fixture
def mock_get_node():
    with patch("src.infrastructure.content_repository.ContentRepository.get_node") as mock_get_node:
        yield mock_get_node


@pytest.fixture
def mock_add_automatic_buttons():
    with patch(f"{PREFIX}.add_automatic_buttons") as mock_add_automatic_buttons:
        yield mock_add_automatic_buttons


@pytest.fixture
def state_store(session):
    with patch(f"{PREFIX}.state_store", Mock()) as state_store:
        state_store.get_session.return_value = session
        yield state_store


def test_get_content_returns_content_response(
    session,
    mock_get_node,
    mock_add_automatic_buttons,
    state_store,
):
    node_id = "test_node"
    mock_node = PostNode(id=node_id, media=[])
    session.push(node_id)
    mock_get_node.return_value = mock_node

    result = get_current_content(session.user_key)

    mock_get_node.assert_called_once_with(node_id)
    assert result == mock_node

    mock_add_automatic_buttons.assert_called_once_with(mock_node, session)


def test_get_content_raises_error_when_node_not_found(
    session,
    mock_get_node,
    mock_add_automatic_buttons,
    state_store,
):
    node_id = "nonexistent"
    session.push(node_id)

    mock_get_node.return_value = None

    with pytest.raises(Exception) as exc_info:
        get_current_content(session.user_key)

    assert "Node not found" in str(exc_info.value)

    mock_add_automatic_buttons.assert_not_called()


def test_get_content_by_id(mock_get_node):
    node_id = "test_node"
    mock_node = PostNode(id=node_id, media=[])
    mock_get_node.return_value = mock_node

    result = get_content_by_id(node_id)

    mock_get_node.assert_called_once_with(node_id)
    assert result == mock_node
