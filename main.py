# Импорт
import telebot
from data.users import User
from data import db_session, __all_models
from game_funcs import keybord_generate, callback_answer

# создание бота
API_TOKEN = '7168920535:AAFENbTdCAxujSoFc9KHomPtqynghWzjZIA'
bot = telebot.TeleBot(API_TOKEN)

# подключение БД и создание сессии
db_session.global_init('db/bot.db')
db_sess = db_session.create_session()

# определение всех, требуемых далее inline-клавиатур
start_kb = keybord_generate([{'text': 'Рейтинг',
                             'callback_data': 'rate_menu',
                              'url': None,
                              'callback_game': None},
                             {'text': 'Играть',
                             'callback_data': 'games_menu',
                              'url': None,
                              'callback_game': None},
                             {'text': 'Друзья',
                              'callback_data': 'friends_menu',
                              'url': None,
                              'callback_game': None}
                             ], width=3)
rate_menu_kb = keybord_generate([{'text': 'Назад',
                              'callback_data': 'main_menu',
                              'url': None,
                              'callback_game': None}])
friends_menu_kb = keybord_generate([{'text': 'Назад',
                                     'callback_data': 'main_menu',
                                     'url': None,
                                     'callback_game': None},
                                    {'text': 'Список друзей',
                                     'callback_data': 'friend_list',
                                     'url': None,
                                     'callback_game': None},
                                    {'text': 'Рейтинг',
                                     'callback_data': 'friend_rate',
                                     'url': None,
                                     'callback_game': None}
                                    ], width=3)


@bot.message_handler(commands=['start'])
def start_reaction(message):
    '''Функция, обрабатывающая команду /start. При первом входе в бота
    пользователь вносится в базу данных, если он уже в базе и
    использовал команду снова, то возвращается в главное меню'''
    # получение списков всех id в БД
    result = map(lambda x: x.id, db_sess.query(User).all())
    # проверка наличия id пользователя в БД и последующий действия
    if message.from_user.id not in result:
        bot.send_message(message.chat.id, f"Привет, "
                                          f"{message.from_user.username}! Я "
                                          f"бот с минииграми.\nВыбери "
                                          f"интересующее тебя меню.",
                         reply_markup=start_kb)
        user = User()
        user.id = message.from_user.id
        user.name = message.from_user.username
        user.friends = ''
        db_sess.add(user)
    else:
        bot.send_message(message.chat.id, 'Вы в главном меню, выберите, '
                                          'что вас интересует?',
                         reply_markup=start_kb)
        user = db_sess.query(User).filter(User.id == \
                                          message.from_user.id).first()
        user.menu = 'main'
    # сохранение изменений в БД
    db_sess.commit()


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'rate_menu':
        text = f'Рейтинг участников бота по игровым очкам:\n'
        callback_answer(bot, call.from_user.id, text, rate_menu_kb,
                        'rate', db_sess, call)
    elif call.data == 'games_menu':
        text = f'Выберите интересующую вас игру'
        callback_answer(bot, call.from_user.id, text, rate_menu_kb,
                        'games', db_sess, call)
    elif call.data == 'friends_menu':
        text = (f'Вы хотите просмотреть список своих друзей или ваш рейтинг '
                f'среди них?')
        callback_answer(bot, call.from_user.id, text, friends_menu_kb,
                        'friends', db_sess, call)
    elif call.data == 'main_menu':
        text = 'Вы в главном меню, выберите, что вас интересует?'
        callback_answer(bot, call.from_user.id, text, start_kb,
                        'main', db_sess, call)
    elif call.data == 'friend_list':
        text = 'Ваши друзья:\n'
        user = db_sess.query(User).filter(User.id == call.from_user.id).first()
        text += '\n'.join(user.friends.split())
        callback_answer(bot, call.from_user.id, text, rate_menu_kb,
                        'friends_list', db_sess, call)



# бесконечный поток запросов к серверам telegram
bot.infinity_polling()