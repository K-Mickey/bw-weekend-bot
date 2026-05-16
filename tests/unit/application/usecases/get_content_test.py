from unittest.mock import patch

import pytest

from src.application.usecases.get_content import get_content
from src.domain.aggregates.post_node import PostNode


def test_get_content_returns_content_response():
    node_id = "test_node"
    mock_node = PostNode(id=node_id, media=[])

    with patch("src.infrastructure.content_repository.ContentRepository.get_node") as mock_get_node:
        mock_get_node.return_value = mock_node
        result = get_content(node_id)

        mock_get_node.assert_called_once_with(node_id)
        assert result == mock_node


def test_get_content_raises_error_when_node_not_found():
    node_id = "nonexistent"

    with patch("src.infrastructure.content_repository.ContentRepository.get_node") as mock_get_node:
        mock_get_node.return_value = None

        with pytest.raises(Exception) as exc_info:
            get_content(node_id)

        assert "Node not found" in str(exc_info.value)
