from unittest.mock import patch

import pytest

from src.application.usecases.navigate import navigate


@pytest.fixture
def mock_store():
    with patch("src.application.usecases.navigate.state_store") as mock:
        yield mock


@pytest.fixture
def mock_get_content():
    with patch("src.application.usecases.navigate.get_current_content") as mock:
        yield mock


def test_navigate_forward(
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

    result = navigate(user_key.network, user_key.external_id, button_label)

    mock_store.push_node.assert_called_once_with(user_key, post_group.id)
    assert result == post_group


def test_navigate_back(
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

    result = navigate(user_key.network, user_key.external_id, "Back")

    mock_store.pop_node.assert_called_once_with(user_key)
    assert result == post_group


def test_navigate_back_at_root(
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

    result = navigate(user_key.network, user_key.external_id, "Back")

    mock_store.pop_node.assert_called_once_with(user_key)
    assert result == post


def test_navigate_invalid_button(
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

    with pytest.raises(ValueError) as exc_info:
        navigate(user_key.network, user_key.external_id, button_label)

    assert "Button not found" in str(exc_info.value)
    mock_store.push_node.assert_not_called()
