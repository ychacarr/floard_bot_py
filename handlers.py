from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboards_and_buttons import *
import random
from config import *

# Инициализация бота и дэспэтчера
storage = MemoryStorage()  # Хранение данных
bot = Bot(token=TOKEN_sergey_test_bot)  # Инициализация бота
dp = Dispatcher(bot, storage=storage)  # Диспэтчер


# сегодняшний вечер клацаем, затем задаём кто есть. затем кто первый, сплит команд, выбор игры

async def command_start(message: types.Message):
    """
    Команда старт
    """
    await message.answer('Выберите шонить', reply_markup=kb_main_menu)


async def command_split_team(callback: types.CallbackQuery):
    """
    Берёт из списка присутсвующих сегодня людей и сплитит их на команды
    атрибуты: количество команд
    В инлайне
    """
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
    # else:
    #     await callback.message.answer('Не хочу вас делить. Что-то не так с количеством')


async def command_today_members(callback: types.CallbackQuery):
    """
    Показывает список всех наполочников. Пользователь выбирает, кто сегодня присутствует.
    В инлайне
    """
    list_of_members = await get_members_from_database()
    kb_with_members = await create_inline_keyboard_with_members(list_of_members)
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
    list_of_members = await get_members_from_database()
    random_member_number = random.randrange(0, (len(list_of_members)-1))
    await callback.message.answer(f"Первый ходит: {list_of_members[random_member_number]}")




async def command_choose_game_first_criterium(callback: types.CallbackQuery):
    """

    """
    await callback.message.answer('Выберите критерий игры:', reply_markup=kb_duration_of_game)


async def command_choose_game_second_criterium(callback: types.CallbackQuery):
    """

    """
    await callback.message.answer('Выберите критерий игры:', reply_markup=kb_speech_level_of_game)


async def command_choose_game_result(callback: types.CallbackQuery):
    """

    """
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




async def get_members_from_database():
    sg = "Сергей"
    yn = "Ян"
    vl = "Владислав"
    al = "Александр"
    il = "Илья"
    ap = "Алексей"
    tm = "Татьяна М"
    tu = "Татьяна Ю"
    vs = "Вероника"
    eu = "Евгения"
    pv = "Полина"
    lm = "Лидия"
    list = [sg, yn, vl, al, il, ap, tm, tu, vs, eu, pv, lm]
    return list


async def create_inline_keyboard_with_members(list_of_members: list):
    kb_with_members = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for k, member in enumerate(list_of_members, start=1):
        member_button = InlineKeyboardButton(f'{member}', callback_data=f"{k}_here")
        kb_with_members.add(member_button)
        print(k)
    return kb_with_members


async def split_teams(teams_count, callback):
    list_of_members = await get_members_from_database()
    list_of_lists = []
    for member in range(teams_count):
        member = []
        list_of_lists.append(member)

    for member in list_of_members:
        number_of_team = random.randrange(0, teams_count)
        list_of_lists[number_of_team].append(member)

    await print_splited_teams(list_of_lists, callback)


async def print_splited_teams(list_of_lists_with_members, callback):
    for k, list in enumerate(list_of_lists_with_members, start=1):
        await callback.message.answer(f'Команда {k}:')
        for j in list:
            await callback.message.answer(f'{j}')
        await callback.message.answer('-------------------------------')




def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_callback_query_handler(command_split_team, text='split_team')
    dp.register_callback_query_handler(command_split_team_result, text=['two_teams', 'three_teams', 'four_teams', 'five_teams'])
    dp.register_callback_query_handler(command_today_members, text='today_members')
    dp.register_callback_query_handler(command_today_members1, text=['1_here','2_here','3_here','4_here','5_here','6_here','7_here','8_here','9_here','10_here','11_here','12_here',])
    dp.register_callback_query_handler(command_first_move, text='first_move')
    dp.register_callback_query_handler(command_choose_game_first_criterium, text='choose_game')
    dp.register_callback_query_handler(command_choose_game_second_criterium, text=['fast_game', 'meduim_game', 'long_game'])
    dp.register_callback_query_handler(command_choose_game_result, text=['speechfull_game', 'speechless_game'])
    dp.register_message_handler(command_birthdays, commands=['birthdays'])
    dp.register_message_handler(command_congratulation, commands=['congrats'])
    dp.register_message_handler(command_add_game, commands=['add_game'])
    dp.register_message_handler(command_add_member, commands=['add_member'])
    dp.register_message_handler(command_delete_member, commands=['delete_member'])
    # dp.register_message_handler(command_games, commands=['games'])

    # dp.register_callback_query_handler(cancel_handler, text='отмена')



if __name__ == '__main__':
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)