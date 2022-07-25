from aiogram import types
from keyboards_and_buttons import *
from database import *
from aiogram.dispatcher.filters.state import State, StatesGroup
import re


async def make_individual_preferences(callback: types.CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Вы увидите название игры. '
                                  'Вам необходимо в чат написать ваше отношение к ней от 0 до 3, где:' + '\n' + '\n' +
                                  '0 - вообще никогда не буду играть (как монополия для Сани) ' + '\n' +
                                  '1 - могу поиграть, но лучше во что-то другое' + '\n' +
                                  '2 - нейтральное отношение' + '\n' +
                                  '3 - моя любимая игра', reply_markup=kb_preferences_ready)
    global games_list
    games_list = await get_all_games_from_database()
    global list_of_lists
    list_of_lists = []


async def first_individual_preferences(callback: types.CallbackQuery):
    await callback.answer('')
    global this_member
    this_member = await authorisation(callback)
    if this_member != None:
        await callback.message.answer(f'Вы идентифицированы как' + '\n' +
                                      f'{this_member.full_name}',
                                      reply_markup=kb_preferences_ok)
    else:
        await callback.message.answer('Нет вашего Telegram_ID в базе данных')


async def second_individual_preferences(callback: types.CallbackQuery):
    await callback.answer('')
    global list_of_lists


    for i in range(0, len(list_of_lists)):
        if (len(list_of_lists[i]) < 3) & (len(list_of_lists[i]) > 1):
            x = (re.findall('(\\d+)', callback.data))
            list_of_lists[i].append(int(x[0]))

    if len(games_list) != 0:
        current_game = games_list.pop(0)
        await callback.message.answer(f'Игра {current_game.name} \nОцените от 0 до 3',
                                      reply_markup=kb_preferences_values)
        list_with_choise = [this_member.id, current_game.id]
        list_of_lists.append(list_with_choise)
    else:
        for i in range(0, len(list_of_lists)):
            if (len(list_of_lists[i]) < 3) & (len(list_of_lists[i]) > 1):
                x = (re.findall('(\\d+)', callback.data))
                list_of_lists[i].append(int(x[0]))
        await callback.message.answer('Всё готово, спасибо за ответы!', reply_markup=kb_preferences_okey)


async def third_individual_preferences(callback: types.CallbackQuery):
    await callback.answer('', )
    await update_preference_database(list_of_lists)
    await callback.message.answer('Перейдите в главное меню, чтобы попробовать другие функции',
                                  reply_markup=kb_menu_start)


async def update_preference_database(list_of_values):
    for list in list_of_values:
        temp = Preference.get((Preference.member_id == list[0]) & (Preference.game_id == list[1]))
        temp.level = list[2]
        temp.save()


async def get_all_games_from_database():
    list = []
    for game in Game:
        list.append(game)
    return list


async def authorisation(callback):
    for member in Member:
        if callback.from_user.id == member.telegram_id:
            return member
        else:
            continue
    return None


async def generate_list_of_game_lists(count):
    list_of_game_lists = []
    for _ in range(0, count):
        list = []
        list_of_game_lists.append(list)
        print(list)
    return list_of_game_lists
