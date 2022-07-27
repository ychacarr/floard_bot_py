from aiogram import types
from keyboards_and_buttons import *
import random
from database import *
import copy



# сегодняшний вечер клацаем, затем задаём кто есть. затем кто первый, сплит команд, выбор игры

async def command_start(message: types.Message):
    """
    Команда старт
    """
    await message.answer('Выберите шонить', reply_markup=kb_main_menu)
    global today_members
    today_members = []


async def command_today_members(callback: types.CallbackQuery):
    """
    Показывает список всех наполочников. Пользователь выбирает, кто сегодня присутствует.
    """
    global list_of_active_members
    list_of_active_members = await get_active_members_from_database()
    kb_with_members = await create_inline_keyboard_with_members(list_of_active_members)
    await callback.answer('')
    await callback.message.answer('Выберите, кто сегодня присутствует ', reply_markup=kb_with_members)


async def today_members_edit_kb(callback: types.CallbackQuery):
    """
    Функция изменения клавиатуры, после того, как был клик на присутствующего человека.
    """
    await callback.answer('')

    for member in list_of_active_members:
        if callback.data == str(member.id):
            today_members.append(member)
            list_of_active_members.remove(member)
        else:
            continue

    new_kb_with_members = await create_inline_keyboard_with_members(list_of_active_members)
    await callback.message.edit_reply_markup(new_kb_with_members)




async def start_evening(callback: types.CallbackQuery):
    """
    Старт вечера. Наступает после выбора всех присутствующих сегодня пользователей.
    Выбирается одна из необходимых функций:
    Разбиться на команды, Выбор первого хода, Генерация подходящей всем игры.
    """
    await callback.answer('')
    await callback.message.answer('Выберите шонить', reply_markup=kb_today_menu)




async def command_split_team(callback: types.CallbackQuery):
    """
    Даёт пользователю выбор количества команд, на которые надо разделить присутсвующих в этот вечер
    """
    await callback.answer('')
    await callback.message.answer('Выберите количество комманд:', reply_markup=kb_number_of_teams)


async def command_split_team_result(callback: types.CallbackQuery):
    """
    Ловит количество выбранных комманд и вызывает функцию split_teams, куда передаёт их количество.
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




async def command_first_move(callback: types.CallbackQuery):
    """
    Рандомно выбирает пользователя из присутсвующих, который должен делать первый ход
    """
    list_of_members = today_members
    random_member_number = random.randrange(0, (len(list_of_members)))
    await callback.answer('')
    await callback.message.answer(f"Первый ходит: {list_of_members[random_member_number].full_name}")




async def command_choose_game_first_criterium(callback: types.CallbackQuery):
    """
    Команда выбора первого критерия игры, в которую пользователи хотят поиграть вечером.
    Критерий: Длительность
    """
    await callback.answer('')
    await callback.message.answer('Выберите критерий игры:', reply_markup=kb_duration_of_game)


async def command_choose_game_second_criterium(callback: types.CallbackQuery):
    """
    Команда выбора второго критерия игры.
    Критерий: Разговорность
    """
    await callback.answer('')
    global game_duration_criterium
    if callback.data == 'fast_game':
        game_duration_criterium = 1
    if callback.data == 'meduim_game':
        game_duration_criterium = 2
    if callback.data == 'long_game':
        game_duration_criterium = 3
    if callback.data == 'no_matter_duration_game':
        game_duration_criterium = None

    await callback.message.answer('Выберите критерий игры:', reply_markup=kb_speech_level_of_game)


async def command_choose_game_third_criterium(callback: types.CallbackQuery):
    """
    Команда выбора третьего критерия игры
    Критерий: Командность
    """
    await callback.answer('')
    global game_speech_criterium
    if callback.data == 'speechfull_game':
        game_speech_criterium = True
    if callback.data == 'speechless_game':
        game_speech_criterium = False
    if callback.data == 'no_matter_speech_game':
        game_speech_criterium = None
    await callback.message.answer('Выберите критерий игры:', reply_markup=kb_type_of_game)


async def command_choose_game_result(callback: types.CallbackQuery):
    """
    Результат выбора критериев игры.
    """
    await callback.answer('')
    global game_teaming_criterium
    if callback.data == 'coop_game':
        game_teaming_criterium = 3
    if callback.data == 'individ_game':
        game_teaming_criterium = 1
    if callback.data == 'tvt_game':
        game_teaming_criterium = 2
    if callback.data == 'no_matter_type_game':
        game_teaming_criterium = None

    result = choose_a_game(today_members, game_duration_criterium, game_teaming_criterium, game_speech_criterium)
    result_games_string = ''
    for game in result[0]:
        print(game)
        result_games_string += game.name
        result_games_string += '\n'

    if len(result_games_string) != 0:
        await callback.message.answer('На основе введённых данных я выбрал следующие игры:' + '\n' +
                            f'{result_games_string}')
    else:
        await callback.message.answer('Таких игр для вас не найдено')




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
    """
    Забирает пользователей, у которых есть параметр is_active, из базы данных
    """
    list = []
    for member in Member:
        if member.is_active:
            list.append(member)
    return list


async def get_all_members_from_database():
    """
    Забирает всех пользователей из базы данных
    """
    list = []
    for member in Member:
        list.append(member)
    return list


async def create_inline_keyboard_with_members(list_of_members: list):
    """
    Создаёт инлайн клавиатуру с теми пользователями, которые пришли на вход
    """
    kb_with_members = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for member in list_of_members:
        member_button = InlineKeyboardButton(f'{member.full_name}', callback_data=f"{member.id}")
        kb_with_members.add(member_button)

    exit_members_button = InlineKeyboardButton('Закончить', callback_data="exit_member_chose")
    kb_with_members.add(exit_members_button)
    return kb_with_members


async def split_teams(teams_count, callback):
    """
    Разбивает список пользователей этого вечера на то количество команд, которое передаётся на вход
    """
    list_of_members = copy.deepcopy(today_members)
    list_of_lists = []
    teams_size_without_remainder = len(list_of_members) // teams_count

    for member in range(teams_count):
        member = []
        list_of_lists.append(member)


    i=0
    while i < teams_count:
        while len(list_of_lists[i]) < teams_size_without_remainder:
            list_of_lists[i].append(list_of_members.pop(random.randrange(0, len(list_of_members))))
        i += 1


    for member in list_of_members:
        list_of_lists[random.randrange(0,len(list_of_lists)-1)].append(member)


    await print_splited_teams(list_of_lists, callback)


async def print_splited_teams(list_of_lists_with_members, callback):
    """
    Распечатывает в чат пользователей, разбитых по командам
    """
    for k, list in enumerate(list_of_lists_with_members, start=1):
        string_all_members_of_team = f'Команда {k}: \n'
        for member in list:
            string_all_members_of_team = string_all_members_of_team + member.full_name + '\n'
        await callback.message.answer(f'{string_all_members_of_team}')
    await callback.answer('')
