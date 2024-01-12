import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import BOT_TOKEN
from handlers import default_handlers, custom_handlers, common
from database.base import init_db


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(default_handlers.router, custom_handlers.router, common.router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(init_db())
    asyncio.run(main())
