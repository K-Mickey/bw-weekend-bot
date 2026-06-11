from unittest.mock import AsyncMock, patch

import pytest

from src.application.usecases.start_conversation import start_conversation
from src.domain.value_objects.node import NodeName
from src.infrastructure.content_repository import ContentNotFoundException

PREFIX = "src.application.usecases.start_conversation"


@pytest.fixture
def mock_get_current_content():
    with patch(f"{PREFIX}.get_current_content", AsyncMock()) as mock_get_current_content:
        yield mock_get_current_content


@pytest.fixture
def mock_state_store():
    yield AsyncMock()


@pytest.mark.asyncio
async def test_start_conversation_creates_session_and_returns_content(
    user_key,
    post,
    mock_state_store,
    mock_get_current_content,
):
    post.id = NodeName.ROOT
    mock_get_current_content.return_value = post

    result = await start_conversation(mock_state_store, user_key.network, user_key.external_id)

    mock_state_store.create_or_reset.assert_called_once_with(user_key, NodeName.ROOT)
    mock_get_current_content.assert_called_once_with(mock_state_store, user_key)
    assert result == post


@pytest.mark.asyncio
async def test_start_conversation_handles_get_content_error(
    user_key,
    mock_state_store,
    mock_get_current_content,
):
    mock_state_store.create_or_reset.return_value = None
    mock_get_current_content.side_effect = ContentNotFoundException("Content not found")

    with pytest.raises(ContentNotFoundException) as exc_info:
        await start_conversation(mock_state_store, user_key.network, user_key.external_id)

    assert str(exc_info.value) == "Content not found"
    mock_state_store.create_or_reset.assert_called_once_with(user_key, NodeName.ROOT)
