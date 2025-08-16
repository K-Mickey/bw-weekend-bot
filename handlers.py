import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from content import States, MESSAGES

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.update_data(state=States.START)
    logger.warning(f"User {message.from_user.id} start bot")
    await send_event(message, state)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        text="Пишите нам, если что-то не работает или нужна помощь:\n\n"
        "- Автор бота Михаил: @k_mickey \n"
        "- Наше главенство Мария: +79101463516"
    )


@router.message()
async def check_answer(message: Message, state: FSMContext):
    state_data = await state.get_data()
    try:
        if not (current_state := state_data.get("state")):
            logger.debug(
                f"User {message.from_user.id} has no state and start with state {States.START}"
            )
            await state.update_data(state=States.START)
            await send_event(message, state)

        else:
            event = MESSAGES.get(current_state)
            if button := event.get_button(message.text):
                logger.debug(
                    f"User {message.from_user.id} click button {button.text} and go to state {button.source}"
                )
                await state.update_data(state=button.source)
            await send_event(message, state)

    except Exception as e:
        logger.error(e)
        await state.update_data(state=States.DEFAULT)
        await send_event(message, state)


async def send_event(message: Message, state: FSMContext):
    state_data = await state.get_data()
    current_state = state_data.get("state")
    logger.debug(f"User {message.from_user.id} in state {current_state}")
    event = MESSAGES.get(current_state)
    for message_content in event.messages:
        await message_content.answer(message)
