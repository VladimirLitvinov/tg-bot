from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.common import add_new_history
from handlers.filters import RequestFilter
from handlers.utils.utils import AsyncResults, send_messages
from site_api.site_api_handler import user_request
from states.user_states import UserStates

CURRENCY = ['USD', 'EUR', 'RUB', ]

router = Router()


@router.message(UserStates.children, F.text.regexp(r'(?<![-.])\b[0-9]+\b(?!\.[0-9])'))
async def children(message: Message, state: FSMContext):
    await state.update_data(children=message.text)
    await message.answer('Введите количество грудных детей (от 0 до 2х лет)')
    await state.set_state(UserStates.infants)


@router.message(UserStates.children)
async def children_err(message: Message):
    await message.answer('Количество детей может быть только целым, положительным числом')


@router.message(UserStates.infants, F.text.regexp(r'(?<![-.])\b[0-9]+\b(?!\.[0-9])'))
async def infants(message: Message, state: FSMContext):
    await state.update_data(infants=message.text)
    await message.answer('Введите количество домашних животных')
    await state.set_state(UserStates.pets)


@router.message(UserStates.infants)
async def infants_err(message: Message):
    await message.answer('Количество грудных детей может быть только целым, положительным числом')


@router.message(UserStates.pets, F.text.regexp(r'(?<![-.])\b[0-9]+\b(?!\.[0-9])'))
async def pets(message: Message, state: FSMContext):
    await state.update_data(pets=message.text)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="USD $", callback_data='USD')
    )
    builder.row(InlineKeyboardButton(
        text="EUR €", callback_data='EUR')
    )
    builder.row(InlineKeyboardButton(
        text='RUB ₽', callback_data='RUB')
    )
    await message.answer('Выберите валюту', reply_markup=builder.as_markup())
    await state.set_state(UserStates.currency)


@router.message(UserStates.pets)
async def pets_err(message: Message):
    await message.answer('Количество домашних животных может быть только целым, положительным числом')


@router.callback_query(UserStates.currency, F.data.in_(CURRENCY))
async def min_price(callback: CallbackQuery, state: FSMContext):
    await state.update_data(currency=callback.data)
    await callback.message.answer('Введите максимальную цену')
    await state.set_state(UserStates.max_price)


@router.callback_query(UserStates.currency)
async def currency_err(callback: CallbackQuery):
    await callback.message.answer('Выберите валюту')


@router.message(UserStates.max_price, F.text.regexp(r'(?<![-.])\b[0-9]+'))
async def max_price(message: Message, state: FSMContext):
    kb = [KeyboardButton(text="Начать поиск")]
    keyboard = ReplyKeyboardMarkup(keyboard=[kb], resize_keyboard=True, one_time_keyboard=True)
    await state.update_data(max_price=message.text)
    await message.answer("Для начала поиска нажмите:\nНачать поиск", reply_markup=keyboard)
    await state.set_state(UserStates.custom_request)


@router.message(UserStates.max_price)
async def max_price(message: Message):
    await message.answer('Максимальная цена должна быть целым, положительным числом')


@router.message(UserStates.custom_request, RequestFilter('Начать поиск'))
async def request(message: Message, state: FSMContext):
    data = await state.get_data()
    params = {
        'city': data['city'],
        'user_tg_id': message.from_user.id,
        'enter_date': datetime.strptime(data['enter_date'], '%Y-%m-%d'),
        'exit_date': datetime.strptime(data['exit_date'], '%Y-%m-%d'),
        'adults': data['adults'],
        'date_search': datetime.now(),
        'children': data['children'],
        'infants': data['infants'],
        'pets': data['pets'],
        'currency': data['currency']
    }

    await add_new_history(params)

    response = await user_request(
        {
            'city': data['city'],
            'enter_date': data['enter_date'],
            'exit_date': data['exit_date'],
            'adults': data['adults'],
            'children': data['children'],
            'infants': data['infants'],
            'pets': data['pets'],
            'currency': data['currency'],
        }
    )

    if response['error'] is True:
        text = response['message']
        await message.answer(f'Ошибка: {text}\nВведите новый запрос')
        await state.clear()

    else:
        results = AsyncResults(response['results'], data['command'], data['max_price'])
        await send_messages(results, message, response, state)


@router.message(UserStates.custom_request)
async def get_request_err(message: Message):
    await message.answer('Нажмите кнопку или введите "Начать поиск"')
