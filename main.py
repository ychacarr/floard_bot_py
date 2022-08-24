import asyncio
from register_handlers import register_handlers
from aiogram import executor
from globals import dp, scheduler, get_bot_username
from congratulations import prepare_congratulation_jobs

if __name__ == '__main__':
    try:
        main_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(main_loop)
        prepare_congratulation_jobs()
        scheduler.add_to_loop(main_loop)

        main_loop.create_task(get_bot_username()) # добавление в список asyncio тасков функции инициализации username бота

        register_handlers(dp)
        executor.start_polling(dp, skip_updates=True)
    finally:
        scheduler.do_backup()
