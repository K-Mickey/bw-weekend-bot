from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from content import States, MESSAGES

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    state_title = States.START
    await state.update_data(state=state_title)

    event = MESSAGES.get(state_title)
    for message_content in event.messages:
        await message_content.answer(message)


@router.message()
async def check_answer(message: Message, state: FSMContext):
    state_data = await state.get_data()
    current_state = state_data.get("state")

    new_state = States.DEFAULT
    if event := MESSAGES.get(current_state):
        if button := event.get_button(message.text):
            await state.update_data(state=button.source)
            new_state = button.source
    else:
        await state.update_data(state=new_state)

    print(new_state)
    event = MESSAGES.get(new_state)
    for message_content in event.messages:
        await message_content.answer(message)
