# Импорт
import telebot
from data.users import User
from data.admins import Admin
from data import db_session, __all_models
from bot_funcs import keybord_generate, callback_answer, tsuefa_game, add_friend
import threading

# создание бота
API_TOKEN = '7168920535:AAFENbTdCAxujSoFc9KHomPtqynghWzjZIA'
bot = telebot.TeleBot(API_TOKEN)

# подключение БД и создание сессии
db_session.global_init('db/bot.db')
db_sess = db_session.create_session()

# определение всех, требуемых далее inline-клавиатур
start_kb = keybord_generate([{'text': 'Рейтинг',
                              'callback_data': 'rate_menu',
                              'url': None},
                             {'text': 'Играть',
                              'callback_data': 'games_menu',
                              'url': None},
                             {'text': 'Друзья',
                              'callback_data': 'friends_menu',
                              'url': None}
                             ])
rate_menu_kb = keybord_generate([{'text': 'Назад',
                                  'callback_data': 'main_menu',
                                  'url': None}
                                 ])
friends_menu_kb = keybord_generate([{'text': 'Назад',
                                     'callback_data': 'main_menu',
                                     'url': None},
                                    {'text': 'Добавить друга',
                                     'callback_data': 'add_friend',
                                     'url': None},
                                    {'text': 'Список друзей',
                                     'callback_data': 'friend_list',
                                     'url': None},
                                    {'text': 'Рейтинг друзей',
                                     'callback_data': 'friend_rate',
                                     'url': None}
                                    ])
games_menu_kb = keybord_generate(
    [
        {'text': 'В главное меню',
         'callback_data': 'main_menu',
         'url': None},
        {'text': 'Кости',
         'callback_data': 'kosti_game',
         'url': None},
        {'text': 'Цуефа',
         'callback_data': 'tsuefa_game',
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



@bot.message_handler(commands=['start'])
def start_reaction(message):
    """
    Функция, обрабатывающая команду /start. При первом входе в бота
    пользователь вносится в базу данных, если он уже в базе и
    использовал команду снова, то возвращается в главное меню
    """
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
        callback_answer(bot, call.from_user.id, text, rate_menu_kb, call)

    elif call.data == 'games_menu':
        text = f'Выберите интересующую вас игру'
        callback_answer(bot, call.from_user.id, text, rate_menu_kb, call)

    elif call.data == 'friends_menu':
        text = (f'Вы хотите просмотреть список своих друзей или ваш рейтинг '
                f'среди них?')
        callback_answer(bot, call.from_user.id, text, friends_menu_kb, call)

    elif call.data == 'main_menu':
        text = 'Вы в главном меню, выберите, что вас интересует?'
        callback_answer(bot, call.from_user.id, text, start_kb, call)

    elif call.data == 'friend_list':
        text = 'Ваши друзья:\n'
        user = db_sess.query(User).filter(User.id == call.from_user.id).first()
        text += '\n'.join(user.friends.split())
        callback_answer(bot, call.from_user.id, text, rate_menu_kb, call)

    elif call.data == 'add_friend':
        bot.delete_message(call.message.chat.id, call.message.id)
        text = 'Введите username пользователя, которого хотите добавить в друзья (@username):'
        new_message = bot.send_message(call.from_user.id, text)
        bot.register_next_step_handler(new_message, add_friend)


    elif (call.data == 'stone' or call.data == 'paper' or
          call.data == 'scissors'):
        translate = {'stone': 'Камень',
                     'scissors': 'Ножницы',
                     'paper': 'Бумага'}
        bot.delete_message(call.message.chat.id, call.message.id)
        tsuefa_game(bot, translate[call.data], db_sess, call.from_user.id)
        bot.send_message(call.from_user.id, f'Выберите интересующую вас '
                                            f'игру',
                         reply_markup=games_menu_kb)

    elif call.data == 'tsuefa_game':
        text = 'Играем! Камень, ножницы, бумага...\n1, 2, 3!'
        callback_answer(bot, call.from_user.id, text, tsuefa_kb, call)


def start(bot):
    # бесконечный поток запросов к серверам telegram
    bot.infinity_polling()


if __name__ == '__main__':
    first_thread = threading.Thread(target=start, args=[bot])
    first_thread.run()
