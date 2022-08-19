import asyncio
from register_handlers import register_handlers
from aiogram import executor
from globals import dp, scheduler
from async_scheduler import AsyncScheduler
from congratulations import prepare_congratulation_jobs

if __name__ == '__main__':
    try:
        main_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(main_loop)
        prepare_congratulation_jobs()
        scheduler.add_to_loop(main_loop)

        register_handlers(dp)
        executor.start_polling(dp, skip_updates=True)
    finally:
        scheduler.do_backup()
