from handlers import *
from aiogram import Dispatcher
from preferences import *
from voice_recognition import *


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_callback_query_handler(command_split_team, text='split_team')
    dp.register_callback_query_handler(command_split_team_result, text=['two_teams', 'three_teams', 'four_teams',
                                                                        'five_teams'])
    dp.register_callback_query_handler(start_evening, text=['exit_member_chose', 'backtomenu'])
    dp.register_callback_query_handler(end_evening, text='end_evening')
    dp.register_callback_query_handler(command_today_members, text='today_members')
    dp.register_callback_query_handler(today_members_edit_kb,
                                       text=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'])
    dp.register_callback_query_handler(command_first_move, text='first_move')
    dp.register_callback_query_handler(command_choose_game_first_criterium, text='choose_game')
    dp.register_callback_query_handler(command_choose_game_second_criterium,
                                       text=['fast_game', 'meduim_game', 'long_game', 'no_matter_duration_game'])
    dp.register_callback_query_handler(command_choose_game_third_criterium, text=['speechfull_game', 'speechless_game',                                                                                  'no_matter_speech_game'])
    dp.register_callback_query_handler(command_choose_game_result,
                                       text=['coop_game', 'individ_game', 'tvt_game', 'no_matter_type_game'])

    dp.register_callback_query_handler(make_individual_preferences, text='individual_preferences')
    dp.register_callback_query_handler(first_individual_preferences, text='ready')
    dp.register_callback_query_handler(second_individual_preferences, text=['0_pref', '1_pref', '2_pref', '3_pref', 'its_me'])

    dp.register_message_handler(command_birthdays, commands=['birthdays'])
    dp.register_callback_query_handler(command_congratulation, text=['congrats'])
    dp.register_message_handler(command_add_game, commands=['add_game'])
    dp.register_message_handler(command_add_member, commands=['add_member'])
    dp.register_message_handler(command_delete_member, commands=['delete_member'])
    # dp.register_message_handler(speech_recogn, content_types=types.ContentType.VOICE)


