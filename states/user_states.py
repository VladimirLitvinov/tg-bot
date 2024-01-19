from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    """
    Class for user states in bot
    """
    choosing_city = State()
    enter_date = State()
    exit_date = State()
    adults_quantity = State()
    request = State()
    custom_request = State()
    more_results = State()
    children = State()
    infants = State()
    pets = State()
    currency = State()
    max_price = State()
    history = State()
