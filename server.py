# Импорт
import telebot
from data.users import User
from data.friends import Friend
from data.admins import Admin
from data import db_session, __all_models
from bot_funcs import (callback_answer, tsuefa_game, add_friend, kosti_game,
                       start_roll_num, del_friend, start_roll_colour)
from keyboard_prototype import *
import threading

# создание бота
API_TOKEN = '7168920535:AAFENbTdCAxujSoFc9KHomPtqynghWzjZIA'
bot = telebot.TeleBot(API_TOKEN)

# подключение БД и создание сессии
db_session.global_init('db/bot.db')
db_sess = db_session.create_session()


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
        db_sess.add(user)

        friend = Friend()
        friend.id = message.from_user.id
        friend.name = message.from_user.username
        db_sess.add(friend)
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

        users = db_sess.query(User).filter(User.id != call.from_user.id).all()
        users_rate = []
        for user in users:
            this_user = db_sess.query(User).filter(User.id == user.id).first()
            users_rate.append((this_user.rate, this_user.name))
        this_man = db_sess.query(User).filter(User.id == call.from_user.id).first()
        users_rate.append((this_man.rate, this_man.name))
        users_rate.sort(key=lambda x: x[0], reverse=True)
        for i in range(0, min(10, len(users_rate))):
            text += f"{i + 1}. @{users_rate[i][1]}\t{users_rate[i][0]}\n"
        text += "-----------------------------\n"
        text += (f"Ваш рейтинг:\n{users_rate.index((this_man.rate,
                                                    this_man.name)) + 1}. "
                 f"@{this_man.name}\t{this_man.rate}")
        callback_answer(bot, call.from_user.id, text,
                        rate_menu_kb, call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'all_rate':
        text = f'Рейтинг участников бота по игровым очкам:\n'

        users = db_sess.query(User).filter(User.id != call.from_user.id).all()
        users_rate = []
        for user in users:
            this_user = db_sess.query(User).filter(User.id == user.id).first()
            users_rate.append((this_user.rate, this_user.name))
        this_man = db_sess.query(User).filter(User.id == call.from_user.id).first()
        users_rate.append((this_man.rate, this_man.name))
        users_rate.sort(key=lambda x: x[0], reverse=True)
        for i in range(0, len(users_rate)):
            text += f"{i + 1}. @{users_rate[i][1]}\t{users_rate[i][0]}\n"
        text += "-----------------------------\n"
        text += (f"Ваш рейтинг:\n{users_rate.index((this_man.rate,
                                                    this_man.name)) + 1}. "
                 f"@{this_man.name}\t{this_man.rate}")
        callback_answer(bot, call.from_user.id, text, keybord_generate(
            [{'text': 'Назад',
              'callback_data': 'main_menu',
              'url': None}
             ]), call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'games_menu':
        text = f'Выберите интересующую вас игру'
        callback_answer(bot, call.from_user.id, text, games_menu_kb, call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'friends_menu':
        text = (f'Вы хотите просмотреть список своих друзей или ваш рейтинг '
                f'среди них?')
        callback_answer(bot, call.from_user.id, text, friends_menu_kb, call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'main_menu':
        text = 'Вы в главном меню, выберите, что вас интересует?'
        callback_answer(bot, call.from_user.id, text, start_kb, call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'friend_list':
        text = 'Ваши друзья:\n'
        user = db_sess.query(Friend).filter(Friend.id ==
                                            call.from_user.id).first()
        friends_list = user.friends.split()
        friends_list.remove("None")
        for friend in friends_list:
            text += f"@{db_sess.query(Friend).filter(Friend.id ==
                                                     friend).first().name}\n"
        text = text.rstrip("\n")
        callback_answer(bot, call.from_user.id, text, back_to_friends, call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'friend_rate':
        friend = db_sess.query(Friend).filter(Friend.id ==
                                              call.from_user.id).first()
        friends_list = friend.friends.split()
        friends_list.remove("None")
        text = "Рейтинг среди ваших друзей:\n"
        friends_rate = []
        for friend in friends_list:
            this_friend = db_sess.query(User).filter(User.id == friend).first()
            friends_rate.append((this_friend.rate, this_friend.name))
        user = db_sess.query(User).filter(User.id == call.from_user.id).first()
        friends_rate.append((user.rate, user.name))
        friends_rate.sort(key=lambda x: x[0], reverse=True)
        for i in range(0, min(10, len(friends_rate))):
            text += f"{i + 1}. @{friends_rate[i][1]}\t{friends_rate[i][0]}\n"
        text += "-----------------------------\n"
        text += (f"Ваш рейтинг:\n{friends_rate.index((user.rate,
                                                      user.name)) + 1}. "
                 f"@{user.name}\t{user.rate}")
        callback_answer(bot, call.from_user.id, text,
                        friends_all_rate_or_back_kb, call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'all_friend_rate':
        friend = db_sess.query(Friend).filter(Friend.id ==
                                              call.from_user.id).first()
        friends_list = friend.friends.split()
        friends_list.remove("None")
        text = "Рейтинг среди ваших друзей:\n"
        friends_rate = []
        for friend in friends_list:
            this_friend = db_sess.query(User).filter(User.id == friend).first()
            friends_rate.append((this_friend.rate, this_friend.name))
        user = db_sess.query(User).filter(User.id == call.from_user.id).first()
        friends_rate.append((user.rate, user.name))
        friends_rate.sort(key=lambda x: x[0], reverse=True)
        for i in range(0, len(friends_rate)):
            text += f"{i + 1}. @{friends_rate[i][1]}\t{friends_rate[i][0]}\n"
        text += "-----------------------------\n"
        text += (f"Ваш рейтинг:\n{friends_rate.index((user.rate,
                                                      user.name)) + 1}. "
                 f"@{user.name}\t{user.rate}")
        callback_answer(bot, call.from_user.id, text,
                        back_to_friends, call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'add_friend':
        bot.delete_message(call.message.chat.id, call.message.id)
        text = ('Введите username пользователя, которого '
                'хотите добавить в друзья (@username):')
        new_message = bot.send_message(call.from_user.id, text)
        bot.register_next_step_handler(new_message, add_friend, bot)

    # //*-------------------------------------------------------------------------------------*//
    elif 'yes_add_friend' in call.data:
        callback = call.data.split(" ")
        first_id = int(callback[1])
        second_id = int(callback[2])

        first_friend = db_sess.query(Friend).filter(Friend.id ==
                                                    first_id).first()
        input_array = first_friend.friends_input.split()
        input_array.remove(str(second_id))
        first_friend.friends_input = " ".join(input_array)
        first_friend.friends += f" {second_id}"

        second_friend = db_sess.query(Friend).filter(Friend.id ==
                                                     second_id).first()
        output_array = second_friend.friends_output.split()
        output_array.remove(str(first_id))
        second_friend.friends_output = " ".join(output_array)
        second_friend.friends += f" {first_id}"

        bot.send_message(second_id, f"Вы добавили в дркзья пользователя "
                                    f"@{first_friend.name}",
                         reply_markup=rate_menu_kb)
        bot.send_message(first_id, f"Пользователь @{second_friend.name} "
                                   f"принял ваш запрос дружбы",
                         reply_markup=rate_menu_kb)
        db_sess.commit()

    # //*-------------------------------------------------------------------------------------*//
    elif 'no_add_friend' in call.data:
        callback = call.data.split(" ")
        first_id = int(callback[1])
        second_id = int(callback[2])

        first_friend = db_sess.query(Friend).filter(Friend.id ==
                                                    first_id).first()
        input_array = first_friend.friends_input.split()
        input_array.remove(str(second_id))
        first_friend.friends_input = " ".join(input_array)

        second_friend = db_sess.query(Friend).filter(Friend.id ==
                                                     second_id).first()
        output_array = second_friend.friends_output.split()
        output_array.remove(str(first_id))
        second_friend.friends_output = " ".join(output_array)

        bot.send_message(second_id, f"Вы отклонили запрос дружбы от "
                                    f"@{first_friend.name}",
                         reply_markup=rate_menu_kb)
        bot.send_message(first_id, f"Пользователь @{second_friend.name} "
                                   f"отклонил ваш запрос дружбы",
                         reply_markup=rate_menu_kb)
        db_sess.commit()

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'del_friend':
        bot.delete_message(call.message.chat.id, call.message.id)
        text = ('Введите username пользователя, которого '
                'хотите удалить из друзей (@username):')
        new_message = bot.send_message(call.from_user.id, text)
        bot.register_next_step_handler(new_message, del_friend, bot)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'tsuefa_game':
        text = 'Играем! Камень, ножницы, бумага...\n1, 2, 3!'
        callback_answer(bot, call.from_user.id, text, tsuefa_kb, call)

    # //*-------------------------------------------------------------------------------------*//
    elif (call.data == 'stone' or call.data == 'paper' or
          call.data == 'scissors'):
        translate = {'stone': 'Камень',
                     'scissors': 'Ножницы',
                     'paper': 'Бумага'}
        bot.delete_message(call.message.chat.id, call.message.id)
        tsuefa_game(bot, translate[call.data], call.from_user.id)
        bot.send_message(call.from_user.id, f'Ещё раз?',
                         reply_markup=after_tsuefa_game)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'kosti_game':
        text = 'Бросаем кости!'
        callback_answer(bot, call.from_user.id, text, kosti_kb, call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'start_kosti':
        bot.delete_message(call.message.chat.id, call.message.id)
        kosti_game(bot, call.from_user.id)
        bot.send_message(call.from_user.id, f'Ещё раз?',
                         reply_markup=after_kosti_game)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'ruletka_game':
        callback_answer(bot, call.from_user.id, "Сделайте ставку",
                        rollet_kb, call)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'red_bet':
        bot.delete_message(call.message.chat.id, call.message.id)
        start_roll_colour('красный', bot, after_roll_menu, open(
            'data/ezgif.com-gif-maker-1-1.gif', 'rb'), call.from_user.id)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'black_bet':
        bot.delete_message(call.message.chat.id, call.message.id)
        start_roll_colour('чёрный', bot, after_roll_menu, open(
            'data/ezgif.com-gif-maker-1-1.gif', 'rb'), call.from_user.id)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'zero_bet':
        bot.delete_message(call.message.chat.id, call.message.id)
        start_roll_colour(0, bot, after_roll_menu, open(
            'data/ezgif.com-gif-maker-1-1.gif', 'rb'), call.from_user.id)

    # //*-------------------------------------------------------------------------------------*//
    elif call.data == 'num_bet':
        bot.delete_message(call.message.chat.id, call.message.id)
        new_message = bot.send_message(call.from_user.id,
                                       'Сделайте вашу ставку!')
        bot.register_next_step_handler(new_message, start_roll_num, bot,
                                       after_roll_menu, open(
                'data/ezgif.com-gif-maker-1-1.gif', 'rb'))


def start(bot):
    # бесконечный поток запросов к серверам telegram
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"[ОШИБКА] Произошла ошибка подключения {e}")


if __name__ == '__main__':
    first_thread = threading.Thread(target=start, args=[bot])
    first_thread.run()
