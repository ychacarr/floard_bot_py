from asyncio import sleep
from datetime import datetime
from genericpath import commonprefix
from aiogram import types
from keyboards_and_buttons import *
import random
from database import *
import copy
from random import randint
import globals
from data import config
from congratulations import prepare_birthday_notification_job
from aiogram.types import InputFile

pipka_max_size = randint(20, 30)

# сегодняшний вечер клацаем, затем задаём кто есть. затем кто первый, сплит команд, выбор игры

async def command_start(message: types.Message):
    """
    Команда старт
    """
    await message.answer('Выберите шонить', reply_markup=kb_main_menu)
    global today_members
    today_members = []


async def command_help(message: types.Message):
    command_list =  [
                        '\n/start - начинает вечер\n/pipkasize - может измерить твою пипку;',
                        '\n/whoami - скажет кто ты сегодня;',
                        '\n/magicball - может дать небольшое предсказание по интересующему тебя вопросу.',
                    ]
    admin_command_list = None
    if (message.from_id in config.admin_id_list and message.chat.type == 'private'):
        admin_command_list =    [
                                    '\n\nКоманды отладки и администрирования:'
                                    '\n/setmain - устанавливает текущий чат в качестве основного. Работает только к групповых чатах;',
                                    '\n/setbirthday Имя Фамилия - сохраняет текущий чат в качестве чата подготовки дня рождения указанного наполочника. Работает только в групповых чатах;',
                                    '\n/getdb - отправляет актуальный файл базы данных. Работает только в личном чате.'
                                ]
    send_str = ''.join(map(str, command_list)) if admin_command_list is None else ''.join(map(str, command_list + admin_command_list))
    await message.answer(f'Вот, что я умею:\n{send_str}')


async def command_today_members(callback: types.CallbackQuery):
    """
    Показывает список всех наполочников. Пользователь выбирает, кто сегодня присутствует.
    """
    global list_of_active_members
    list_of_active_members = await get_active_members_from_database()
    kb_with_members = await create_inline_keyboard_with_members(list_of_active_members)
    await callback.answer('')
    await callback.message.edit_text('Выберите, кто сегодня присутствует ', reply_markup=kb_with_members)


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
    await callback.message.edit_text('Выберите шонить', reply_markup=kb_today_menu)


async def end_evening(callback: types.CallbackQuery):
    """
    Окончание вечера. Удаляет менюшку
    """
    await callback.answer('')
    await callback.message.delete()
    await callback.answer('Приятного вечера!')




async def command_split_team(callback: types.CallbackQuery):
    """
    Даёт пользователю выбор количества команд, на которые надо разделить присутсвующих в этот вечер
    """
    await callback.answer('')
    await callback.message.edit_text('Выберите количество комманд:', reply_markup=kb_number_of_teams)


async def command_split_team_result(callback: types.CallbackQuery):
    """
    Ловит количество выбранных комманд и вызывает функцию split_teams, куда передаёт их количество.
    """
    await callback.message.delete()
    if callback.data == "two_teams":
        await split_teams(2, callback)
    if callback.data == "three_teams":
        await split_teams(3, callback)
    if callback.data == "four_teams":
        await split_teams(4, callback)
    if callback.data == "five_teams":
        await split_teams(5, callback)
    await callback.answer('')
    await callback.message.answer('Выберите шонить', reply_markup=kb_today_menu)





async def command_first_move(callback: types.CallbackQuery):
    """
    Рандомно выбирает пользователя из присутсвующих, который должен делать первый ход
    """
    await callback.answer('')
    list_of_members = today_members
    if len(list_of_members) != 0:
        random_member_number = random.randrange(0, (len(list_of_members)))
        await callback.message.edit_text(f"Первый ходит: {list_of_members[random_member_number].full_name}")
    else:
        await callback.message.edit_text("Не заполнен список присутствующих. Нажмите /start, чтобы заполнить его")
    await callback.message.answer('Выберите шонить', reply_markup=kb_today_menu)





async def command_choose_game_first_criterium(callback: types.CallbackQuery):
    """
    Команда выбора первого критерия игры, в которую пользователи хотят поиграть вечером.
    Критерий: Длительность
    """
    await callback.answer('')
    await callback.message.edit_text('Выберите критерий игры:', reply_markup=kb_duration_of_game)


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

    await callback.message.edit_text('Выберите критерий игры:', reply_markup=kb_speech_level_of_game)


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
    await callback.message.edit_text('Выберите критерий игры:', reply_markup=kb_type_of_game)


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
        await callback.message.edit_text('На основе введённых данных я выбрал следующие игры:' + '\n' +
                            f'{result_games_string}')
    else:
        await callback.message.edit_text('Таких игр для вас не найдено')
    await callback.message.answer('Выберите шонить', reply_markup=kb_today_menu)


async def pipka_size(message: types.Message):
    """
    Команда '/pipkasize' ('пипка')
    
    Замер пипки. У Сани всегда больше всех. 
    """
    reply_mention = ''
    if message.chat.type != 'private':
        reply_mention = f'@{message.from_user.username}! '
    if (message.from_id == Member.get((Member.name == 'Александр') & (Member.surname == 'Ситник')).telegram_id):
        global pipka_max_size
        pipka_max_size = pipka_max_size + randint(0, 5)
        await message.answer(f'{reply_mention}Размер твоей пипки равен {pipka_max_size} сантиметрам! 🤯😲')
    else:
        temp_size = randint(0, pipka_max_size - 1)
        size_string = f'{temp_size} сантиметрам'
        if temp_size % 10 == 1 and temp_size != 11:
            size_string = f'{temp_size} сантриметру'
        if (temp_size >= (pipka_max_size / 2 + 5)):
            await message.answer(f'{reply_mention}Размер твоей пипки равен {size_string}! 🧐👏🏿')
        elif (temp_size >= 15):
            await message.answer(f'{reply_mention}Размер твоей пипки равен {size_string}! 🤓👍🏻')
        elif (temp_size >= 10):
            await message.answer(f'{reply_mention}Размер твоей пипки равен {size_string}. 😐👌')
        elif (temp_size >= 5):
            await message.answer(f'{reply_mention}Размер твоей пипки равен {size_string}. 😕')
        elif (temp_size >= 2):
            await message.answer(f'{reply_mention}Размер твоей пипки равен {size_string}... 😨')
        elif (temp_size == 1):
            await message.answer(f'{reply_mention}Размер твоей пипки равен {size_string}... 😰')
        else:
            await message.answer(f'{reply_mention}Смотрю, смотрю, но ничего не вижу... Погоди, достану микроскоп...')
            await message.answer('🔬')
            temp_size = randint(0, 10)
            await sleep(3)
            if (temp_size != 0):
                if (temp_size != 1):
                    await message.answer(f'Ага! Разглядел. {reply_mention}Размер пипки равен {temp_size} *миллиметрам*! 🤭', parse_mode='markdown')
                else:
                    await message.answer(f'Ага! Разглядел. {reply_mention}Размер пипки равен {temp_size} *миллиметру*! 🤭', parse_mode='markdown')
            else:
                await message.answer(f'{reply_mention}Прости... Не помог даже микроскоп... 🙈')


async def who_am_i(message: types.Message):
    """
    Команда '/whoami' ('кто я сегодня?')

    Выдаёт случайно собранную кличку.\n
    Кличка строится по "формуле": прилагательное + существительное.\n
    Прилагательные и существительные берутся из таблиц БД KekAdjective и KekNoun.
    """
    writing_member = Member.get(Member.telegram_id == message.from_user.id)
    result_str = f'{KekAdjective.get_random(writing_member.sex).lower()} {KekNoun.get_random(writing_member.sex)}'
    if message.chat.type != 'private':
        await message.answer(f'@{message.from_user.username}, сегодня ты *{result_str}*!', parse_mode='markdown')
    else:
        await message.answer(f'Сегодня ты *{result_str}*!', parse_mode='markdown')


async def magic_ball_helper(message: types.Message):
    """
    Выводит справку по использованию функционала магического шара.

    Активируется командой /magicball
    """
    await message.answer(f'Если хочешь получить небольшое предсказание, отправь сообщение с упоминанием меня, содержащее интересующий тебя вопрос вида да\нет.\n' +
                            'В личном чате можешь не писать упоминание, просто отправь сообщение с вопросительным знаком.\n\n' +
                            f'Пример: \"Эй, @{globals.BOT_USERNAME}, мы сегодня сыграем в монополию?\"\n\n' +
                            'Если хочешь получить быстрое предсказание, добавь микрокоманду [быстро] в любое место текста.\n\n' +
                            f'Пример: \"Эй, @{globals.BOT_USERNAME}, а в мафию сыграем? [быстро]\"\n' +
                            f'или так: \"@{globals.BOT_USERNAME} [быстро] может хотя бы в магов?\"')


async def magic_ball(message: types.Message):
    """
    Функция генерации предсказания в ответ на вопрос боту.
    """
    msg_member = Member.get(Member.telegram_id == message.from_user.id)
    replies_list = ['Абсолютли!',
                    'Кажется, что \"Да\".',
                    'Пока решения нет..',
                    'Мой ответ \"Нет\"...',
                    'Всё чётко! Сумеешь, смогёшь!',
                    'Вероятнее всего.',
                    f'Спроси по новой, {msg_member.name}, всё фигня..',
                    'Перспективы не очень хорошие...',
                    'Никаких сомнений!',
                    'Перспективы хорошие.',
                    'Сущность в виде гномика закрывает обзор будущего..',
                    'Честно говоря, весьма сомнительно...',
                    'Определенно да!',
                    'Космос говорит \"Да, но это неточно.\".',
                    'Попробуй выйти на связь снова..',
                    'Ты втираешь мне какую-то дичь..',
                    'Мои источники даже не сомневаются в успехе!',
                    'Да.',
                    'Сконцентрируйся и попробуй спросить опять..',        
                    'Иммолед импрувед, или в переводе - вероятность этого события крайне мала...']
    if '[быстро]' not in message.text:
        testing = await message.reply('Хмм... Посылаю сигнал в космос...📡')
        await sleep(2)
        await testing.edit_text('...Стучусь в пятый дом Юпитера...🔮')
        await sleep(2)
        await testing.edit_text('...Ищу номера в слове \"нумерология\"...🎱')
        await sleep(2)
        await testing.edit_text(f'{replies_list[randint(0, len(replies_list) - 1)]}')
    else:
        await message.reply(f'{replies_list[randint(0, len(replies_list)) - 1]}')


async def set_main_chat(message: types.Message):
    """
    Функция обновления ID главного чата.

    Срабатывает только на сообщения от пользователей, чей telegram_id входит в список из файла config.py (admin_id_list)\n
    Вызывает unknown_command в ином случае.
    """
    if (message.chat.type != 'private' and message.from_user.id in config.admin_id_list):
        status = await globals.save_main_chat_id(message.chat.id)
        if status:
            await message.answer('ID главного чата успешно обновлён.')
        else:
            await message.answer('Не смог обновить ID главного чата.')
    else:
        await unknown_command(message)


async def set_birthday_chat(message: types.Message):
    """
    Функция обновления ID чата подготовки ко дню рождения наполочника.

    Срабатывает только на сообщения от пользователей, чей telegram_id входит в список из файла config.py (admin_id_list)\n
    Вызывает unknown_command если telegram_id не в списке разрешенных.\n

    Ожидает формат: /setbirthday Имя Фамилия\n
    В случае возникновения ошибки отправляет её содержание в личный чат написавшего команду.
    """
    if (message.chat.type != 'private' and message.from_user.id in config.admin_id_list):
        member_names_list = (message.text.removeprefix('/setbirthday ')).split(' ')
        try:
            if (len(member_names_list) == 2):
                member = Member.get((Member.name == member_names_list[0]) & (Member.surname == member_names_list[1]))
                member.birthday_group_id = message.chat.id
                member.save()
                globals.scheduler.delete_job(f'{member.full_name}_birthday_notification')
                globals.scheduler.add_job(prepare_birthday_notification_job(member))
                await message.answer(f'Чат сохранён в качестве чата подготовки к ДР наполочника: {member.full_name}.\nДата дня рождения: {member.birth_date}' +
                                        '\nПришлю уведомление за две недели до праздника.')
            else:
                raise Exception('На нашёл имени наполочника в тексте команды. Использование: /setbirthday Имя Фамилия')
        except Exception as err:
            await message.answer('Не смог обновить поздравительный чат наполочника. Подробности отправил в личный чат.')
            await globals.dp.bot.send_message(message.from_user.id, f'При попытке обновить поздравительный чат наполочника произошла ошибка: {err}')
    else:
        await unknown_command(message)


async def get_db_command(message: types.Message):
    if (message.chat.type == 'private' and message.from_id in config.admin_id_list):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f'{date_str}.db'
        db_file = InputFile('./data/floardbase.db', filename=filename)
        await message.answer_document(document=db_file, caption='Файл базы данных.')
    else:
        await unknown_command(message)


async def unknown_command(message: types.Message):
    """
    Функция обработчик всех неизвестных команд.
    """
    await message.answer('Извини, я не знаю такой команды.')


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