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