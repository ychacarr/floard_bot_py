from handlers import *
from aiogram import Dispatcher


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    # dp.register_callback_query_handler(start_evening, text=['today_members'])
    dp.register_callback_query_handler(command_split_team, text='split_team')
    dp.register_callback_query_handler(command_split_team_result, text=['two_teams', 'three_teams', 'four_teams', 'five_teams'])
    dp.register_callback_query_handler(command_today_members, text='today_members')
    # dp.register_callback_query_handler(command_today_members1, text=['1_here','2_here','3_here','4_here','5_here','6_here','7_here','8_here','9_here','10_here','11_here','12_here',])
    dp.register_callback_query_handler(command_first_move, text='first_move')
    dp.register_callback_query_handler(command_choose_game_first_criterium, text='choose_game')
    dp.register_callback_query_handler(command_choose_game_second_criterium, text=['fast_game', 'meduim_game', 'long_game', 'no_matter_duration_game'])
    dp.register_callback_query_handler(command_choose_game_result, text=['speechfull_game', 'speechless_game', 'no_matter_speech_game'])
    dp.register_message_handler(command_birthdays, commands=['birthdays'])
    dp.register_message_handler(command_congratulation, commands=['congrats'])
    dp.register_message_handler(command_add_game, commands=['add_game'])
    dp.register_message_handler(command_add_member, commands=['add_member'])
    dp.register_message_handler(command_delete_member, commands=['delete_member'])
    # dp.register_message_handler(command_games, commands=['games'])
    @dp.callback_query_handler(
        lambda call: ['1_here', '2_here', '3_here', '4_here', '5_here', '6_here', '7_here', '8_here', '9_here',
                      '10_here', '11_here', '12_here'] in call.data)
    async def next_keyboard(call):
        list_of_members = await get_members_from_database(clicked_member_id=call.data)
        kb_with_members = await create_inline_keyboard_with_members(list_of_members)
        await call.message.edit_reply_markup(kb_with_members)
    # dp.register_callback_query_handler(cancel_handler, text='отмена')