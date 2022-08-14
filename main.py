import asyncio
from register_handlers import register_handlers
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.config import *
import logging
from async_scheduler import AsyncScheduler
from congratulations import prepare_congratulation_jobs

# Инициализация бота и дэспэтчера
storage = MemoryStorage()  # Хранение данных
bot = Bot(token=BOT_TOKEN)  # Инициализация бота
dp = Dispatcher(bot, storage=storage)  # Диспэтчер
logging.basicConfig(level=logging.INFO)
scheduler = AsyncScheduler(prepare_congratulation_jobs(), True, 'scheduler_backup.backup')

if __name__ == '__main__':
    try:
        main_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(main_loop)
        scheduler.add_to_loop(main_loop)

        register_handlers(dp)
        executor.start_polling(dp, skip_updates=True)
    finally:
        scheduler.do_backup()
