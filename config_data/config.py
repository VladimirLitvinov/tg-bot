import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
DEFAULT_COMMANDS = (
    ("help", "Вывести справку"),
    ("bestdeals", "Лучшие предложения"),
    ("lowprice", "Низкие цены"),
    ("highprice", "Высокие цены"),
    ("history", "История запросов"),
    ("custom", "Свой фильтр"),
    ("cancel", "Отмена команды")
)
