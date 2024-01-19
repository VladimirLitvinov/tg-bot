from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardButton, \
    CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_data.config import DEFAULT_COMMANDS
from database.common import get_history, get_history_by_id
from site_api.site_api_handler import user_request
from states.user_states import UserStates
from .utils.utils import build_history_text, AsyncResults, send_messages

router = Router()


@router.message(Command(commands=["cancel"]))
async def cancel(message: Message, state: FSMContext) -> None:
    """
    Handler for the cancel current action, clear user's state
    :param message: Message object
    :param state: User state
    :return: None
    """
    await state.clear()
    await message.answer(
        text="Команда отменена",
        reply_markup=ReplyKeyboardRemove()
    )
    text = [f"/{command} - {desc}" for command, desc in DEFAULT_COMMANDS]
    await message.answer("\n".join(text))


@router.message(Command(commands=["history"]))
async def history(message: Message, state: FSMContext) -> None:
    """
    Handler for displaying user search history
    :param message: Message object
    :param state: User state
    :return: None
    """
    user_history = await get_history(message.from_user.id)
    if len(user_history) == 0:
        await message.answer('Вы еще не делали запросы')
    else:
        text, _history = await build_history_text(user_history)
        keyboard = InlineKeyboardBuilder()
        for i in _history:
            keyboard.add(InlineKeyboardButton(text=i, callback_data=str(_history[i].id)))
        await message.answer(text)
        await message.answer('Выберите номер запроса чтобы повторить', reply_markup=keyboard.as_markup())
        await state.set_state(UserStates.history)


@router.callback_query(UserStates.history, F.data)
async def history_results(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for handling user search history callback
    :param callback: User callback query
    :param state: User's state
    :return: None
    """
    history_id = callback.data
    request = await get_history_by_id(int(history_id))
    params = {
        'city': request.city,
        'enter_date': datetime.strftime(request.enter_date, '%Y-%m-%d'),
        'exit_date': datetime.strftime(request.exit_date, '%Y-%m-%d'),
        'adults': request.adults
    }
    if request.children is not None:
        params['children'] = request.children
        params['infants'] = request.infants
        params['pets'] = request.pets
        params['currency'] = request.currency

    response = await user_request(params)

    if response['error'] is True:
        text = response['message']
        await callback.message.answer(f'Ошибка: {text}\nВведите новый запрос')
        await state.clear()

    else:
        if request.command != '/custom':
            results = AsyncResults(response['results'], request.command)
        else:
            results = AsyncResults(response['results'], request.command, request.max_price)
        await send_messages(results, callback.message, response, state)


@router.message(UserStates.history)
async def history_err(message: Message) -> None:
    """
    Handler for handling incorrect user input
    :param message: User's message
    :return: None
    """
    await message.answer('Выберите значение или введите "/cancel"')
