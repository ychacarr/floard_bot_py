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
# Переменная для сохранения id главного чата
MAIN_CHAT_ID = None
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

def restore_main_chat_id(filename:str = './data/main_chat.backup'):
    """
    Функция считывает значение id главного чата из файла.

    Перехватывает исключения.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as params_file:
            global MAIN_CHAT_ID
            MAIN_CHAT_ID = int(params_file.read())
    except Exception:
        pass

async def save_main_chat_id(new_id: int, filename:str = './data/main_chat.backup'):
    """
    Функция обновляет текущее значение MAIN_CHAT_ID и записывает изменённое значение в файл.

    Возвращает:\n
        True -- в случае успешной записи в файл и обновления значения переменной\n
        False -- в случае возникновения исключения при открытии/записи в файл\n
    Если в момент записи возникли проблемы, значение MAIN_CHAT_ID откатывается к предыдущему значению.
    """
    global MAIN_CHAT_ID
    tmp = MAIN_CHAT_ID
    try:
        with open(filename, 'w', encoding='utf-8') as params_file:
            MAIN_CHAT_ID = new_id
            params_file.write(str(MAIN_CHAT_ID))
        return True
    except Exception as err:
        MAIN_CHAT_ID = tmp
        return False