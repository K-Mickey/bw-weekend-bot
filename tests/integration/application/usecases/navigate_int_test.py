import pytest

from src.application.usecases.navigate import ButtonNotFoundException, navigate
from src.domain.aggregates import Content, Post
from src.domain.entities.media import Text
from src.domain.value_objects.button import BaseButton
from src.domain.value_objects.node import NodeName
from src.infrastructure.content_repository import ContentNotFoundException

PRICE_LABEL = "Цены"
PRICE_ID = "prices"
CONTACTS_LABEL = "Контакты"
CONTACTS_ID = "contacts"


@pytest.mark.asyncio
async def test_navigate_forward(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    assert (await state_store.get_session(user_key)).current == NodeName.ROOT

    content = await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)

    assert isinstance(content, Content)
    session = await state_store.get_session(user_key)
    assert session.current == PRICE_ID
    assert session.history == [NodeName.ROOT, PRICE_ID]


@pytest.mark.asyncio
async def test_navigate_forward_content(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    content = await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)

    assert isinstance(content, Post)
    assert content.id == PRICE_ID
    assert content.media == Text(text="Prices")

    assert len(content.keyboard) == 2
    assert len(content.keyboard[0]) == 1
    assert content.keyboard[0][0].text == CONTACTS_LABEL

    assert len(content.keyboard[1]) == 1
    assert content.keyboard[1][0].text == BaseButton.MAIN_MENU


@pytest.mark.asyncio
async def test_navigate_unexpected_button(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    with pytest.raises(ButtonNotFoundException):
        await navigate(state_store, user_key.network, user_key.external_id, "unexpected_button")


@pytest.mark.asyncio
async def test_navigate_not_found_content(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    with pytest.raises(ContentNotFoundException):
        await navigate(state_store, user_key.network, user_key.external_id, "Локации")


@pytest.mark.asyncio
async def test_navigate_second_forward(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)

    content = await navigate(state_store, user_key.network, user_key.external_id, CONTACTS_LABEL)

    assert (await state_store.get_session(user_key)).current == CONTACTS_ID
    assert (await state_store.get_session(user_key)).history == [NodeName.ROOT, PRICE_ID, CONTACTS_ID]

    assert isinstance(content, Post)
    assert content.id == CONTACTS_ID
    assert content.media == Text(text="Contacts")

    assert len(content.keyboard) == 1
    assert len(content.keyboard[0]) == 2
    assert content.keyboard[0][0].text == BaseButton.MAIN_MENU
    assert content.keyboard[0][1].text == BaseButton.BACK


@pytest.mark.asyncio
async def test_navigate_main_menu(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)
    await navigate(state_store, user_key.network, user_key.external_id, CONTACTS_LABEL)

    await navigate(state_store, user_key.network, user_key.external_id, BaseButton.MAIN_MENU)

    assert (await state_store.get_session(user_key)).current == NodeName.ROOT
    assert (await state_store.get_session(user_key)).history == [NodeName.ROOT]


@pytest.mark.asyncio
async def test_navigate_back(state_store, user_key):
    await state_store.create_or_reset(user_key, NodeName.ROOT)
    await navigate(state_store, user_key.network, user_key.external_id, PRICE_LABEL)
    await navigate(state_store, user_key.network, user_key.external_id, CONTACTS_LABEL)

    await navigate(state_store, user_key.network, user_key.external_id, BaseButton.BACK)

    assert (await state_store.get_session(user_key)).current == PRICE_ID
    assert (await state_store.get_session(user_key)).history == [NodeName.ROOT, PRICE_ID]
