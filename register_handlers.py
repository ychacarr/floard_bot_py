from handlers import *
from aiogram import Dispatcher
from preferences import *
import globals

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_message_handler(command_help, commands=['help'])
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
    dp.register_message_handler(command_congratulation, commands=['congrats'])
    dp.register_message_handler(command_add_game, commands=['add_game'])
    dp.register_message_handler(command_add_member, commands=['add_member'])
    dp.register_message_handler(command_delete_member, commands=['delete_member'])
    
    # admin commands
    dp.register_message_handler(set_main_chat, commands=['setmain'])
    dp.register_message_handler(set_birthday_chat, commands=['setbirthday'])
    dp.register_message_handler(get_db_command, commands=['getdb'])

    dp.register_message_handler(pipka_size, commands=['pipkasize'])
    dp.register_message_handler(who_am_i, commands=['whoami'])
    dp.register_message_handler(magic_ball_helper, commands=['magicball'])
    dp.register_message_handler(get_new_year_fortune, commands=['fortune'])
    dp.register_message_handler(get_new_year_fortune, lambda msg:
                                                (msg.chat.type == 'private' and 'предсказание' in msg.text.lower()) or
                                                (f'{globals.BOT_USERNAME}' in msg.text and ('предсказание' in msg.text.lower()))
                                )
    # схема реакции хендлера аналогична хендлеру команды "пипка". Текст активации: "кто я сегодня?"
    dp.register_message_handler(who_am_i, lambda msg:
                                                (msg.chat.type == 'private' and 'кто я сегодня?' in msg.text.lower()) or
                                                (f'{globals.BOT_USERNAME}' in msg.text and ('кто я сегодня?' in msg.text.lower()))
                                )
    # схема реакции аналогична хендеру выше. Текст активации должен содержать вопросительный знак.
    # !ВАЖНО! Этот хендлер должен идти после любой другой команды, текст активации которой содержит вопросительный знак!
    dp.register_message_handler(magic_ball, lambda msg:
                                                (msg.chat.type == 'private' and '?' in msg.text) or
                                                (f'{globals.BOT_USERNAME}' in msg.text and ('?' in msg.text))
                                )
    # хэндлер снизу реагирует на слово "пипка" (без учёта регистра):
        # если чат личный - проверка только на содержание в тексте слова "пипка"
        # иначе, проверяет наличие в тексте упоминания бота и содержание в тексте слова "пипка"
    # в итоге в беседах, команда активируется только если написать "@здесь_упоминание_бота пипка".
    dp.register_message_handler(pipka_size, lambda msg: 
                                                (msg.chat.type == 'private' and ('пипка') in msg.text.lower()) or
                                                (globals.BOT_USERNAME in msg.text and ('пипка' in msg.text.lower()))
                                )
    # !ВАЖНО! Этот хендлер обрабатывает неизвестные команды. Он обязательно должен быть в самом конце списка хендлеров
    dp.register_message_handler(unknown_command, lambda msg:
                                                    ((msg.chat.type == 'private') or 
                                                    (f'{globals.BOT_USERNAME}' in msg.text)))