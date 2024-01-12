from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from config_data.config import DEFAULT_COMMANDS
from database.common import get_history
from .utils.utils import build_history_text

router = Router()


@router.message(Command(commands=["cancel"]))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Команда отменена",
        reply_markup=ReplyKeyboardRemove()
    )
    text = [f"/{command} - {desc}" for command, desc in DEFAULT_COMMANDS]
    await message.answer("\n".join(text))


@router.message(Command(commands=["history"]))
async def history(message: Message):
    user_history = await get_history(message.from_user.id)
    if len(user_history) == 0:
        await message.answer('Вы еще не делали запросы')
    else:
        text = await build_history_text(user_history)
        await message.answer(text)
