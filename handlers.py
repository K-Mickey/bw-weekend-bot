from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from content import States, MESSAGES

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.update_data(state=States.START)
    await send_event(message, state)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        text="Если что-то не работает, то напишите нам об этом:\n\n"
        "- Автор бота Михаил: @k_mickey \n"
        "- Наше главенство Мария: +79101463516"
    )


@router.message()
async def check_answer(message: Message, state: FSMContext):
    state_data = await state.get_data()
    if not (current_state := state_data.get("state")):
        await state.update_data(state=States.START)

    elif event := MESSAGES.get(current_state):
        if button := event.get_button(message.text):
            await state.update_data(state=button.source)

    else:
        await state.update_data(state=States.DEFAULT)

    await send_event(message, state)


async def send_event(message: Message, state: FSMContext):
    state_data = await state.get_data()
    current_state = state_data.get("state")
    event = MESSAGES.get(current_state)
    for message_content in event.messages:
        await message_content.answer(message)
