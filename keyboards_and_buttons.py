from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

button_today_members = InlineKeyboardButton('Ввести присутствующих', callback_data="today_members")
button_individual_pref = InlineKeyboardButton('Задать предпочтения по играм', callback_data="individual_preferences")
kb_main_menu = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_main_menu.add(button_today_members).add(button_individual_pref)


button_split_team = InlineKeyboardButton('Разбиться на команды', callback_data="split_team")
button_first_move = InlineKeyboardButton('Кто первый ходит?', callback_data="first_move")
button_choose_game = InlineKeyboardButton('Выбрать игру', callback_data="choose_game")
kb_today_menu = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_today_menu.add(button_split_team).add(button_first_move).add(button_choose_game)


button_fast_game = InlineKeyboardButton('Быстрая', callback_data="fast_game")
button_meduim_game = InlineKeyboardButton('Средняя', callback_data="meduim_game")
button_long_game = InlineKeyboardButton('Долгая', callback_data="long_game")
button_no_matter_duration_game = InlineKeyboardButton('Не важно', callback_data="no_matter_duration_game")
kb_duration_of_game = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_duration_of_game.add(button_fast_game, button_meduim_game, button_long_game).add(button_no_matter_duration_game)

button_speechfull_game = InlineKeyboardButton('Разговорная', callback_data="speechfull_game")
button_speechless_game = InlineKeyboardButton('Неразговорная', callback_data="speechless_game")
button_no_matter_speech_game = InlineKeyboardButton('Не важно', callback_data="no_matter_speech_game")
kb_speech_level_of_game = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_speech_level_of_game.add(button_speechfull_game, button_speechless_game).add(button_no_matter_speech_game)

button_coop_game = InlineKeyboardButton('Кооперативная', callback_data="coop_game")
button_individual_game = InlineKeyboardButton('Индивидуальная', callback_data="individ_game")
button_team_vs_team_game = InlineKeyboardButton('Команда на команду', callback_data="tvt_game")
button_no_matter_type_game = InlineKeyboardButton('Не важно', callback_data="no_matter_type_game")
kb_type_of_game = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_type_of_game.add(button_coop_game).add(button_individual_game).add(button_team_vs_team_game).add(button_no_matter_type_game)


button_two_teams = InlineKeyboardButton('2', callback_data="two_teams")
button_three_teams = InlineKeyboardButton('3', callback_data="three_teams")
button_four_teams = InlineKeyboardButton('4', callback_data="four_teams")
button_five_teams = InlineKeyboardButton('5', callback_data="five_teams")
kb_number_of_teams = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=4)
kb_number_of_teams.add(button_two_teams, button_three_teams, button_four_teams, button_five_teams)


button_preferences_ready = InlineKeyboardButton('Готов!', callback_data="ready")
kb_preferences_ready = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_preferences_ready.add(button_preferences_ready)
button_preferences_ok = InlineKeyboardButton('Это я. Начать заполнение', callback_data="its_me")
kb_preferences_ok = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_preferences_ok.add(button_preferences_ok)

button_preferences_value_0 = InlineKeyboardButton('0', callback_data="0_pref")
button_preferences_value_1 = InlineKeyboardButton('1', callback_data="1_pref")
button_preferences_value_2 = InlineKeyboardButton('2', callback_data="2_pref")
button_preferences_value_3 = InlineKeyboardButton('3', callback_data="3_pref")
kb_preferences_values = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=4)
kb_preferences_values.add(button_preferences_value_0, button_preferences_value_1,
                          button_preferences_value_2, button_preferences_value_3)

button_preferences_okey = InlineKeyboardButton('ok', callback_data="oki")
kb_preferences_okey = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_preferences_okey.add(button_preferences_okey)

button_start = KeyboardButton('/start')
kb_menu_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_menu_start.add(button_start)