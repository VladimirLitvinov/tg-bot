from aiogram.filters import Filter
from aiogram.types import Message


class RequestFilter(Filter):
    """
    Filter for handling start request text
    """

    def __init__(self, text: str) -> None:
        self.text = text

    async def __call__(self, message: Message) -> bool:
        """
        Check if text is valid and if it is not
        :param message: User's message
        :return: boolean value indicating if text is valid
        """
        return message.text == self.text
