from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder

from database.models import History
from states.user_states import UserStates


class AsyncResults:
    def __init__(self, list_result, command, max_price: int = None):
        if command == '/lowprice':
            self.list_result = sorted(list_result, key=lambda x: x['price']['total'])
        elif command == '/highprice':
            self.list_result = sorted(list_result, key=lambda x: x['price']['total'], reverse=True)
        elif command == '/bestdeals':
            self.list_result = sorted(list_result, key=lambda x: x.get('rating', 0), reverse=True)
        elif command == '/custom':
            self.list_result = [result for result in list_result if float(result['price']['total']) <= float(max_price)]
        self.counter = 0

    def __aiter__(self):
        return self

    async def __anext__(self, ):
        if self.counter == len(self.list_result):
            raise StopAsyncIteration
        self.counter += 1
        return self.list_result[self.counter]


async def get_text(params_dict: dict) -> str:
    text = (f'Название: {params_dict["name"]}\n'
            f'Кровати: {params_dict["beds"]}\n'
            f'Адрес: {params_dict["address"]}\n'
            f'Цена: {params_dict["price"]["total"]} '
            f'{params_dict["price"]["currency"]}\n'
            f'Рейтинг: {params_dict["rating"]}')

    return text


async def build_media_message(photos_dict: dict) -> MediaGroupBuilder:
    message_builder = MediaGroupBuilder()
    for link in photos_dict[:3]:
        message_builder.add_photo(link)

    return message_builder


async def build_description_message(params_dict: dict):
    hotel_params = {
        'name': params_dict['name'],
        'beds': params_dict['beds'],
        'address': params_dict['address'],
        'price': params_dict['price'],
        'rating': params_dict.get('rating', 0)
    }
    text = await get_text(hotel_params)
    button = InlineKeyboardBuilder()
    button.row(InlineKeyboardButton(
        text="Ссылка на сайт", url=params_dict['deeplink'])
    )
    return text, button


async def send_messages(iterator: AsyncResults, message: Message, response: dict, state: FSMContext):
    while True:
        one_result = await anext(iterator)
        media_message = await build_media_message(one_result['images'])
        description_message = await build_description_message(one_result)
        await message.answer_media_group(media=media_message.build())
        await message.answer(description_message[0], reply_markup=description_message[1].as_markup())
        if iterator.counter % 3 == 0:
            count_results = len(response['results']) - iterator.counter + 1
            button = InlineKeyboardBuilder()
            button.row(InlineKeyboardButton(
                text=f"Показать еще", callback_data='more_results')
            )
            await message.answer(f'Доступно еще {count_results} результатов', reply_markup=button.as_markup())
            await state.update_data(results=iterator, response=response, message=message)
            await state.set_state(UserStates.more_results)
            break

        if iterator.counter + 1 == len(response['results']):
            await message.answer('Конец списка, введите новую команду')
            await state.clear()


async def build_history_text(history_list: list[History]) -> str:
    splitter = '-' * 10
    history_text = ''
    for history in history_list:
        history_text += (f'Дата поиска: {history.date_search}\n'
                         f'Город: {history.city}\n'
                         f'Дата въезда: {history.enter_date}\n'
                         f'Дата выезда: {history.exit_date}\n'
                         f'Взрослые: {history.adults}\n'
                         f'{splitter}\n')

    return history_text
