# Импорт
import telebot
from data.users import User
from data.friends import Friend
from data.admins import Admin
from data import db_session, __all_models
from bot_funcs import callback_answer, tsuefa_game, add_friend
from keyboard_prototype import start_kb, rate_menu_kb, friends_menu_kb, games_menu_kb, tsuefa_kb
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
        bot.register_next_step_handler(new_message, add_friend, bot)

    elif 'yes_add_friend' in call.data:
        callback = call.data.split(" ")
        first_id = int(callback[1])
        second_id = int(callback[2])
        first_friend = db_sess.query(Friend).filter(Friend.id == first_id).first()
        print(first_friend.friends_input)
        first_friend.friends_input = first_friend.friends_input.replace(f" {second_id}", "")
        first_friend.friends += f" {second_id}"
        second_friend = db_sess.query(Friend).filter(Friend.id == second_id).first()
        second_friend.friends_output = second_friend.friends_output.replace(f" {first_id}", "")
        second_friend.friends += f" {first_id}"
        bot.send_message(second_id, f"Вы добавили в дркзья пользователя @{first_friend.name}", reply_markup=rate_menu_kb)
        bot.send_message(first_id, f"Пользователь @{second_friend.name} принял ваш запрос дружбы", reply_markup=rate_menu_kb)

    elif 'no_add_friend' in call.data:
        callback = call.data.split(" ")
        first_id = int(callback[1])
        second_id = int(callback[2])
        first_friend = db_sess.query(Friend).filter(Friend.id == first_id).first()
        first_friend.friends_input = " ".join(first_friend.friends_input.split().remove(second_id))
        second_friend = db_sess.query(Friend).filter(Friend.id == second_id).first()
        second_friend.friends_input = " ".join(second_friend.friends_input.split().remove(first_id))
        bot.send_message(second_id, f"Вы отклонили запрос дружбы от @{first_friend.name}", reply_markup=rate_menu_kb)
        bot.send_message(first_id, f"Пользователь @{second_friend.name} отклонил ваш запрос дружбы", reply_markup=rate_menu_kb)

    elif call.data == 'tsuefa_game':
        text = 'Играем! Камень, ножницы, бумага...\n1, 2, 3!'
        callback_answer(bot, call.from_user.id, text, tsuefa_kb, call)

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


def start(bot):
    # бесконечный поток запросов к серверам telegram
    bot.infinity_polling()


if __name__ == '__main__':
    first_thread = threading.Thread(target=start, args=[bot])
    first_thread.run()
