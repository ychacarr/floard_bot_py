from register_handlers import register_handlers
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import *
import logging

# Инициализация бота и дэспэтчера
storage = MemoryStorage()  # Хранение данных
bot = Bot(token=BOT_TOKEN)  # Инициализация бота
dp = Dispatcher(bot, storage=storage)  # Диспэтчер
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
