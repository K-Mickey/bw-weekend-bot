from unittest.mock import patch

import pytest

from src.application.usecases.start_conversation import start_conversation
from src.domain.aggregates import PostNode
from src.domain.value_objects.network import Network
from src.domain.value_objects.user_key import UserKey
from src.domain.value_objects.user_session import UserSession


def test_start_conversation_creates_session_and_returns_content():
    network = Network.TELEGRAM
    external_user_id = "123"
    user_key = UserKey(network, str(external_user_id))
    root_node_id = "main"
    root_node = PostNode(id=root_node_id, media=[])

    with (
        patch("src.application.usecases.start_conversation.state_store") as mock_store,
        patch("src.application.usecases.start_conversation.get_content") as mock_get_content,
    ):
        mock_session = UserSession(user_key=user_key, root_node_id=root_node_id)
        mock_store.create_or_reset.return_value = mock_session
        mock_get_content.return_value = root_node

        result = start_conversation(network, external_user_id)

        mock_store.create_or_reset.assert_called_once_with(user_key, root_node_id)
        mock_get_content.assert_called_once_with(root_node_id, mock_session)
        assert result == root_node


def test_start_conversation_handles_get_content_error():
    network = Network.VK
    external_user_id = 456
    user_key = UserKey(network, str(external_user_id))
    root_node_id = "main"

    with (
        patch("src.application.usecases.start_conversation.state_store") as mock_store,
        patch("src.application.usecases.start_conversation.get_content") as mock_get_content,
    ):
        mock_store.create_or_reset.return_value = None
        mock_get_content.side_effect = Exception("Content not found")

        with pytest.raises(Exception) as exc_info:
            start_conversation(network, external_user_id)

        assert str(exc_info.value) == "Content not found"
        mock_store.create_or_reset.assert_called_once_with(user_key, root_node_id)
