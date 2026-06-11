from unittest.mock import AsyncMock, patch

import pytest

from src.application.usecases.get_content import get_content_by_id, get_current_content

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
    state_store = AsyncMock()
    state_store.get_session.return_value = session
    yield state_store


@pytest.mark.asyncio
async def test_get_content_returns_content_response(
    session,
    post,
    mock_get_node,
    mock_add_automatic_buttons,
    state_store,
):
    session.push(post.id)
    mock_get_node.return_value = post

    result = await get_current_content(state_store, session.user_key)

    mock_get_node.assert_called_once_with(post.id)
    assert result == post

    mock_add_automatic_buttons.assert_called_once_with(post, session)


@pytest.mark.asyncio
async def test_get_content_raises_error_when_node_not_found(
    session,
    mock_get_node,
    mock_add_automatic_buttons,
    state_store,
):
    node_id = "nonexistent"
    session.push(node_id)

    mock_get_node.return_value = None

    with pytest.raises(Exception) as exc_info:
        await get_current_content(state_store, session.user_key)

    assert "Node not found" in str(exc_info.value)

    mock_add_automatic_buttons.assert_not_called()


def test_get_content_by_id(mock_get_node, post):
    mock_get_node.return_value = post
    result = get_content_by_id(post.id)
    mock_get_node.assert_called_once_with(post.id)
    assert result == post
