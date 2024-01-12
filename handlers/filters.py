from aiogram.filters import Filter
from aiogram.types import Message


class RequestFilter(Filter):
    def __init__(self, text: str) -> None:
        self.text = text

    async def __call__(self, message: Message):
        return message.text == self.text
