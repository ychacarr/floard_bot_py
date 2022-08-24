from aiogram import Bot, Dispatcher
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.config import *
from async_scheduler import AsyncScheduler

# Инициализация бота и дэспэтчера
storage = MemoryStorage()  # Хранение данных
bot = Bot(token=BOT_TOKEN)  # Инициализация бота
dp = Dispatcher(bot, storage=storage)  # Диспэтчер
scheduler = AsyncScheduler([], True, './data/scheduler_backup.backup') # Планировщик задач
logging.basicConfig(level=logging.INFO)
# Константа, где будет сохранено username бота (@здесь_имя)
BOT_USERNAME = ''
async def get_bot_username():
    """
    Функция для инициализации константы BOT_USERNAME

    Вызывает метод bot.get_me().
    """
    global BOT_USERNAME
    bot_user = await bot.get_me()
    BOT_USERNAME = bot_user.username