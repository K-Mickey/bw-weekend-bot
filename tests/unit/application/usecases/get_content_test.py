from unittest.mock import patch

import pytest

from src.application.usecases.get_content import get_content
from src.domain.aggregates.post_node import PostNode
from src.domain.value_objects.network import Network
from src.domain.value_objects.nodes import NodeName
from src.domain.value_objects.user_key import UserKey
from src.domain.value_objects.user_session import UserSession


@pytest.fixture
def session():
    user_key = UserKey(Network.TELEGRAM, "123")
    return UserSession(user_key, NodeName.ROOT)


def test_get_content_returns_content_response(session):
    node_id = "test_node"
    mock_node = PostNode(id=node_id, media=[])
    session.push(node_id)

    with patch("src.infrastructure.content_repository.ContentRepository.get_node") as mock_get_node:
        mock_get_node.return_value = mock_node
        result = get_content(session)

        mock_get_node.assert_called_once_with(node_id)
        assert result == mock_node


def test_get_content_raises_error_when_node_not_found(session):
    node_id = "nonexistent"
    session.push(node_id)

    with patch("src.infrastructure.content_repository.ContentRepository.get_node") as mock_get_node:
        mock_get_node.return_value = None

        with pytest.raises(Exception) as exc_info:
            get_content(session)

        assert "Node not found" in str(exc_info.value)
