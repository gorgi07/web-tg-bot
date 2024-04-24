from bot_funcs import keybord_generate

start_kb = keybord_generate(
    [{'text': 'Играть',
      'callback_data': 'games_menu',
      'url': None},
     {'text': 'Друзья',
      'callback_data': 'friends_menu',
      'url': None},
     {'text': 'Рейтинг',
      'callback_data': 'rate_menu',
      'url': None}
     ])

# определение всех, требуемых далее inline-клавиатур
rate_menu_kb = keybord_generate(
    [{'text': 'Назад',
      'callback_data': 'main_menu',
      'url': None}
     ])

friends_menu_kb = keybord_generate([
    {'text': 'Добавить друга',
     'callback_data': 'add_friend',
     'url': None},
    {'text': 'Список друзей',
     'callback_data': 'friend_list',
     'url': None},
    {'text': 'Рейтинг друзей',
     'callback_data': 'friend_rate',
     'url': None},
    {'text': 'Назад',
     'callback_data': 'main_menu',
     'url': None}
])

games_menu_kb = keybord_generate(
    [{'text': 'Кости',
      'callback_data': 'kosti_game',
      'url': None},
     {'text': 'Цуефа',
      'callback_data': 'tsuefa_game',
      'url': None},
     {'text': 'Рулетка',
      'callback_data': 'ruletka_game',
      'url': None},
     {'text': 'В главное меню',
      'callback_data': 'main_menu',
      'url': None}
     ])

tsuefa_kb = keybord_generate(
    [{'text': 'Камень',
      'callback_data': 'stone',
      'url': None},
     {'text': 'Ножницы',
      'callback_data': 'scissors',
      'url': None},
     {'text': 'Бумага',
      'callback_data': 'paper',
      'url': None}
     ])

kosti_kb = keybord_generate(
    [{'text': 'Брость кости',
      'callback_data': 'start_kosti',
      'url': None}
     ])

ruletka_kb = keybord_generate(
    [{'text': 'Крутить',
      'callback_data': 'start_roll',
      'url': None}]
)

friends_all_rate_or_back_kb = keybord_generate(
    [{'text': 'Полный рейтинг',
      'callback_data': 'all_friend_rate',
      'url': None},
     {'text': 'Назад',
      'callback_data': 'friends_menu',
      'url': None}]
)
