from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale

from config_data.config import DEFAULT_COMMANDS
from database.common import add_new_history
from site_api.site_api_handler import user_request
from states.user_states import UserStates
from .filters import RequestFilter
from .utils.utils import AsyncResults, send_messages

router = Router()


@router.message(Command('start'))
async def start(message: Message) -> None:
    """
    Starts the bot
    :param message: User's message
    :return: None
    """
    await message.answer(f'Привет {message.from_user.first_name}!\nДля информации о командах введите /help')


@router.message(Command('help'))
async def help(message: Message) -> None:
    """
    Handler for /help command
    :param message: User's message
    :return: None
    """
    text = [f"/{command} - {desc}" for command, desc in DEFAULT_COMMANDS]
    await message.answer("\n".join(text))


@router.message(StateFilter(None), Command('lowprice', 'highprice', 'bestdeals', 'custom'))
async def get_city(message: Message, state: FSMContext) -> None:
    """
    Handler for getting user's command
    :param message: User's message
    :param state: User's state
    :return: None
    """
    await state.update_data(command=message.text)
    await message.answer('Введите название города')
    await state.set_state(UserStates.enter_date)


@router.message(UserStates.enter_date, F.text)
async def enter_date(message: Message, state: FSMContext) -> None:
    """
    Handler for getting enter date
    :param message: User's message
    :param state: User's state
    :return: None
    """
    calendar = SimpleCalendar(
        locale=await get_user_locale(message.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime.now() - timedelta(days=1), datetime.now() + timedelta(days=365))
    await state.update_data(city=message.text)
    await message.answer('Выберите дату заезда', reply_markup=await calendar.start_calendar())
    await state.set_state(UserStates.exit_date)


@router.message(UserStates.enter_date)
async def err_city_input(message: Message) -> None:
    """
    Handler for handling incorrect enter date input
    :param message: User's message
    :return: None
    """
    await message.answer('Название города может содержать только буквы')


@router.callback_query(SimpleCalendarCallback.filter(), UserStates.exit_date)
async def exit_date(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    """
    Handler for handling enter date callback
    :param callback_query: User's callback query
    :param callback_data: User's callback data
    :param state: User's state
    :return: None
    """
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(enter_date=date.strftime("%Y-%m-%d"))
        calendar.set_dates_range(min_date=date + timedelta(days=1), max_date=date + timedelta(days=365))
        await callback_query.message.answer(text='Выберите дату выезда', reply_markup=await calendar.start_calendar())
        await state.set_state(UserStates.adults_quantity)


@router.callback_query(SimpleCalendarCallback.filter(), UserStates.adults_quantity)
async def adults_quantity(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    """
    Handler for handling exit date callback
    :param callback_query: User's callback query
    :param callback_data: User's callback data
    :param state: User's state
    :return: None
    """
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await state.update_data(exit_date=date.strftime("%Y-%m-%d"))
        await callback_query.message.answer('Введите количество взрослых (от 13ти лет)')


@router.message(UserStates.adults_quantity, F.text.regexp(r'(?<![-.])\b[1-9]+\b(?!\.[0-9])'))
async def get_adults(message: Message, state: FSMContext) -> None:
    """
    Handler for getting adults
    :param message: User's message
    :param state: User's state
    :return: None
    """
    kb = [KeyboardButton(text="Начать поиск")]
    keyboard = ReplyKeyboardMarkup(keyboard=[kb], resize_keyboard=True, one_time_keyboard=True)
    await state.update_data(adults=message.text)
    data = await state.get_data()
    if data['command'] != '/custom':
        await message.answer("Для начала поиска нажмите:\nНачать поиск", reply_markup=keyboard)
        await state.set_state(UserStates.request)
    else:
        await message.answer('Введите количество детей (от 2х до 13ти лет)')
        await state.set_state(UserStates.children)


@router.message(UserStates.adults_quantity)
async def get_adults_err(message: Message) -> None:
    """
    Handler for handling incorrect values of the number of adults
    :param message: User's message
    :return: None
    """
    await message.answer('Количество взрослых можеть быть только целым числом не меньше 1')


@router.message(UserStates.request, RequestFilter('Начать поиск'))
async def get_request(message: Message, state: FSMContext) -> None:
    """
    Handler for handling user's request
    :param message: User's message
    :param state: User's state
    :return: None
    """
    user_params = await state.get_data()
    params = {
        'city': user_params['city'],
        'user_tg_id': message.from_user.id,
        'enter_date': datetime.strptime(user_params['enter_date'], '%Y-%m-%d'),
        'exit_date': datetime.strptime(user_params['exit_date'], '%Y-%m-%d'),
        'adults': user_params['adults'],
        'date_search': datetime.now(),
    }
    await add_new_history(params)
    response = await user_request(
        {
            'city': user_params['city'],
            'enter_date': user_params['enter_date'],
            'exit_date': user_params['exit_date'],
            'adults': user_params['adults']
        }
    )
    commands = [f"/{command} - {desc}" for command, desc in DEFAULT_COMMANDS]
    if response['error'] is True:
        text = response['message']
        await message.answer(f'Ошибка: {text}\nВведите новый запрос')
        await state.clear()
        await message.answer('\n'.join(commands))
    else:
        if len(response['results']) == 0:
            await message.answer('По вашему запросу ничего не найдено, введите новую команду')
            await message.answer('\n'.join(commands))
            await state.clear()
        else:
            results = AsyncResults(response['results'], user_params['command'])
            await send_messages(results, message, response, state)


@router.message(UserStates.request)
async def get_request_err(message: Message) -> None:
    """
    Handler for handling incorrect user's message for start search
    :param message: User's message
    :return: None
    """
    await message.answer('Нажмите кнопку или введите "Начать поиск"')


@router.callback_query(UserStates.more_results, F.data == "more_results")
async def more_results(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handler for handling callback query for more results
    :param callback: Callback query
    :param state: User's state
    :return: None
    """
    data = await state.get_data()
    results = data['results']
    response = data['response']
    message = data['message']
    await send_messages(results, message, response, state)
