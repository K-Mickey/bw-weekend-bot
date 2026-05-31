from unittest.mock import patch

import pytest

from src.application.usecases.start_conversation import start_conversation
from src.domain.value_objects.node import NodeName

PREFIX = "src.application.usecases.start_conversation"


@pytest.fixture
def mock_state_store():
    with patch(f"{PREFIX}.state_store") as mock_state_store:
        yield mock_state_store


@pytest.fixture
def mock_get_current_content():
    with patch(f"{PREFIX}.get_current_content") as mock_get_current_content:
        yield mock_get_current_content


def test_start_conversation_creates_session_and_returns_content(
    user_key,
    post,
    mock_state_store,
    mock_get_current_content,
):
    post.id = NodeName.ROOT
    mock_get_current_content.return_value = post

    result = start_conversation(user_key.network, user_key.external_id)

    mock_state_store.create_or_reset.assert_called_once_with(user_key, NodeName.ROOT)
    mock_get_current_content.assert_called_once_with(user_key)
    assert result == post


def test_start_conversation_handles_get_content_error(
    user_key,
    mock_state_store,
    mock_get_current_content,
):
    mock_state_store.create_or_reset.return_value = None
    mock_get_current_content.side_effect = Exception("Content not found")

    with pytest.raises(Exception) as exc_info:
        start_conversation(user_key.network, user_key.external_id)

    assert str(exc_info.value) == "Content not found"
    mock_state_store.create_or_reset.assert_called_once_with(user_key, NodeName.ROOT)
