import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboards_and_buttons import *
import random
from config import *
from database import *

# Инициализация бота и дэспэтчера
storage = MemoryStorage()  # Хранение данных
bot = Bot(token=BOT_TOKEN)  # Инициализация бота
dp = Dispatcher(bot, storage=storage)  # Диспэтчер
logging.basicConfig(level=logging.INFO)

# сегодняшний вечер клацаем, затем задаём кто есть. затем кто первый, сплит команд, выбор игры

async def command_start(message: types.Message):
    """
    Команда старт
    """
    await message.answer('Выберите шонить', reply_markup=kb_main_menu)


async def start_evening(callback: types.CallbackQuery):
    """
    Команда старт
    """
    await callback.message.answer('Выберите шонить', reply_markup=kb_today_menu)



async def command_split_team(callback: types.CallbackQuery):
    """
    Берёт из списка присутсвующих сегодня людей и сплитит их на команды
    атрибуты: количество команд
    В инлайне
    """
    await callback.answer('')
    await callback.message.answer('Выберите количество комманд:', reply_markup=kb_number_of_teams)


async def command_split_team_result(callback: types.CallbackQuery):
    """

    """
    if callback.data == "two_teams":
        await split_teams(2, callback)
    if callback.data == "three_teams":
        await split_teams(3, callback)
    if callback.data == "four_teams":
        await split_teams(4, callback)
    if callback.data == "five_teams":
        await split_teams(5, callback)
    await callback.answer('')
    # else:
    #     await callback.message.answer('Не хочу вас делить. Что-то не так с количеством')


async def command_today_members(callback: types.CallbackQuery):
    """
    Показывает список всех наполочников. Пользователь выбирает, кто сегодня присутствует.
    В инлайне
    """
    list_of_members = await get_active_members_from_database()
    kb_with_members = await create_inline_keyboard_with_members(list_of_members)
    await callback.answer('')
    # global kb_with_members
    await callback.message.answer('Выберите, кто сегодня присутствует ', reply_markup=kb_with_members)
    # print(callback.message.reply_markup)


async def command_today_members1(callback: types.CallbackQuery):
    print(callback.message.reply_markup)
    print(callback.data)
    # kb_with_members
    # await callback.message.edit_reply_markup(kb_with_members)




async def command_first_move(callback: types.CallbackQuery):
    """
    Рандомно выбирает того, кто сегодня первый ходит
    В инлайне
    """
    list_of_members = await get_active_members_from_database()
    random_member_number = random.randrange(0, (len(list_of_members)-1))
    await callback.answer('')
    await callback.message.answer(f"Первый ходит: {list_of_members[random_member_number].full_name}")




async def command_choose_game_first_criterium(callback: types.CallbackQuery):
    """

    """
    await callback.answer('')
    await callback.message.answer('Выберите критерий игры:', reply_markup=kb_duration_of_game)


async def command_choose_game_second_criterium(callback: types.CallbackQuery):
    """

    """
    await callback.answer('')
    await callback.message.answer('Выберите критерий игры:', reply_markup=kb_speech_level_of_game)


async def command_choose_game_result(callback: types.CallbackQuery):
    """

    """
    await callback.answer('')
    await callback.message.answer('Результат игры: игра')




async def command_birthdays():
    pass


async def command_congratulation():
    pass


async def command_add_member():
    pass


async def command_delete_member():
    pass


async def command_add_game():
    pass


async def command_delete_game():
    pass




async def get_active_members_from_database():
    list = []
    for member in Member:
        if (member.is_active):
            list.append(member)
    return list

async def get_all_members_from_database():
    list = []
    for member in Member:
        list.append(member)
    return list


async def create_inline_keyboard_with_members(list_of_members: list):
    kb_with_members = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for k, member in enumerate(list_of_members, start=1):
        member_button = InlineKeyboardButton(f'{member.full_name}', callback_data=f"{k}_here")
        kb_with_members.add(member_button)
        print(k)
    return kb_with_members


async def split_teams(teams_count, callback):
    list_of_members = await get_active_members_from_database()
    list_of_lists = []
    teams_size_without_remainder = len(list_of_members) // teams_count
    remainder = len(list_of_members) % teams_count
    print(teams_size_without_remainder)

    for member in range(teams_count):
        member = []
        list_of_lists.append(member)


    print(list_of_members)
    i=0
    while i < teams_count:
        while len(list_of_lists[i]) < teams_size_without_remainder:
            list_of_lists[i].append(list_of_members.pop(random.randrange(0, len(list_of_members))))
            print(f"Цикл {i}")
        i += 1


    for member in list_of_members:
        list_of_lists[random.randrange(0,len(list_of_lists)-1)].append(member)


    await print_splited_teams(list_of_lists, callback)


async def print_splited_teams(list_of_lists_with_members, callback):
    for k, list in enumerate(list_of_lists_with_members, start=1):
        string_all_members_of_team = f'Команда {k}: \n'
        for member in list:
            string_all_members_of_team = string_all_members_of_team + member.full_name + '\n'
        await callback.message.answer(f'{string_all_members_of_team}')
    await callback.answer('')