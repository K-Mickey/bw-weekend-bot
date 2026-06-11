from unittest.mock import AsyncMock, patch

import pytest

from src.application.usecases.navigate import ButtonNotFoundException, navigate


@pytest.fixture
def mock_store():
    yield AsyncMock()


@pytest.fixture
def mock_get_content():
    with patch("src.application.usecases.navigate.get_current_content") as mock:
        yield mock


@pytest.mark.asyncio
async def test_navigate_forward(
    user_key,
    session,
    post_group,
    get_content,
    mock_store,
    mock_get_content,
):
    post = get_content("post_simple.yaml")
    post.keyboard[0][0].target = post_group.id

    button_label = "Settings"

    session.history = ["main", post.id]
    mock_store.get_session.return_value = session
    mock_get_content.side_effect = [post, post_group]

    result = await navigate(mock_store, user_key.network, user_key.external_id, button_label)

    mock_store.push_node.assert_called_once_with(user_key, post_group.id)
    assert result == post_group


@pytest.mark.asyncio
async def test_navigate_back(
    user_key,
    session,
    post_group,
    get_content,
    mock_store,
    mock_get_content,
):
    back_post = get_content("post_back.yaml")
    back_post.keyboard[0][0].target = post_group.id

    session.history = ["main", post_group.id, "other"]
    mock_store.get_session.return_value = session

    def mock_pop_node(key):
        if session.history:
            return session.history.pop()
        return None

    mock_store.pop_node.side_effect = mock_pop_node
    mock_get_content.side_effect = [back_post, post_group]

    result = await navigate(mock_store, user_key.network, user_key.external_id, "Back")

    mock_store.pop_node.assert_called_once_with(user_key)
    assert result == post_group


@pytest.mark.asyncio
async def test_navigate_back_at_root(
    user_key,
    session,
    get_content,
    mock_store,
    mock_get_content,
):
    post = get_content("post_back.yaml")
    post.id = "main"
    post.keyboard[0][0].target = "main"

    mock_session = session
    mock_session.history = ["main"]

    mock_store.get_session.return_value = mock_session
    mock_store.pop_node.return_value = None
    mock_get_content.side_effect = [post, post]

    result = await navigate(mock_store, user_key.network, user_key.external_id, "Back")

    mock_store.pop_node.assert_called_once_with(user_key)
    assert result == post


@pytest.mark.asyncio
async def test_navigate_invalid_button(
    user_key,
    session,
    post_group,
    mock_store,
    mock_get_content,
):
    button_label = "NonExistentButton"
    session.history = ["main", post_group.id]

    mock_store.get_session.return_value = session
    mock_get_content.return_value = post_group

    with pytest.raises(ButtonNotFoundException):
        await navigate(mock_store, user_key.network, user_key.external_id, button_label)

    mock_store.push_node.assert_not_called()
