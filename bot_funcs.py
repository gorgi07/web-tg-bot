import telebot
from data.users import User
from data.friends import Friend
from data import db_session, __all_models
from random import choice, randint

db_session.global_init('db/bot.db')
db_sess = db_session.create_session()


def keybord_generate(buttons: list):
    """
    Универсальная функция для генерации inline-клавиатур.
    buttons - список словарей с параметрами кнопок
    """
    markup = telebot.types.InlineKeyboardMarkup()
    for elem in buttons:
        button = (
            telebot.types.InlineKeyboardButton(text=elem['text'],
                                               callback_data=
                                               elem['callback_data'],
                                               url=elem['url']))
        markup.add(button)
    return markup


back_to_friends = keybord_generate(
    [{'text': 'Назад',
      'callback_data': 'friends_menu',
      'url': None}
     ])


def callback_answer(bot, user_id, text, keybord, call):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(user_id, text, reply_markup=keybord)


def tsuefa_game(bot, user_choice, user_id):
    bot_choice = choice(['Камень', 'Ножницы', 'Бумага'])
    rules = {
        'камень': 'ножницы',
        'ножницы': 'бумага',
        'бумага': 'камень'
    }
    user = db_sess.query(User).filter(User.id == user_id).first()
    if bot_choice == user_choice:
        bot.send_message(user_id, 'Ничья! Ничего - лучше, чем минус :)')
        bot.send_message(user_id, f'Ваш рейтинг: {user.rate}')
    elif rules[user_choice.lower()] == bot_choice.lower():
        bot.send_message(user_id, 'Вы выиграли!')
        user.rate += 1
        bot.send_message(user_id, f'Ваш рейтинг: {user.rate}')
    else:
        bot.send_message(user_id, 'Вы проиграли!')
        if user.rate > 0:
            user.rate -= 1
        bot.send_message(user_id, f'Ваш рейтинг: {user.rate}')
    db_sess.commit()


def add_friend(message, bot):
    new_friend = str(message.text).replace("@", "")
    first_user = db_sess.query(Friend).filter(Friend.id ==
                                              message.from_user.id).first()
    second_user = db_sess.query(Friend).filter(Friend.name == new_friend).first()
    if second_user:
        first_user.friends_input += f" {second_user.id}"
        second_user.friends_output += f" {first_user.id}"
        bot.send_message(message.from_user.id, "Запрос дружбы успешно "
                                               "отправлен",
                         reply_markup=back_to_friends)

        bot.send_message(second_user.id, f"Пользователь @{first_user.name} "
                                         f"отправил вам запрос дружбы",
                         reply_markup=
                         keybord_generate([{'text': 'Принять',
                                            'callback_data': " ".join(
                                                ['yes_add_friend',
                                                 str(first_user.id),
                                                 str(second_user.id)]),
                                            'url': None},
                                            {'text': 'Отклонить',
                                             'callback_data': " ".join(
                                                 ['no_add_friend',
                                                  str(first_user.id),
                                                  str(second_user.id)]),
                                             'url': None}]))
    else:
        bot.send_message(message.from_user.id, "Данный пользователь "
                                               "ещё не зарегистрирован",
                         reply_markup=back_to_friends)

    db_sess.commit()


def del_friend(message, bot):
    new_friend = str(message.text).replace("@", "")
    first_user = db_sess.query(Friend).filter(Friend.id ==
                                              message.from_user.id).first()
    second_user = db_sess.query(Friend).filter(Friend.name == new_friend).first()

    if second_user:
        input_array = first_user.friends.split()
        if str(second_user.id) in input_array:
            input_array.remove(str(second_user.id))
            first_user.friends = " ".join(input_array)

            input_array = second_user.friends.split()
            input_array.remove(str(first_user.id))
            second_user.friends = " ".join(input_array)

            bot.send_message(message.from_user.id, f"Вы удалили из друзей "
                                                   f"пользователя @{second_user.name}",
                             reply_markup=back_to_friends)
            bot.send_message(second_user.id, f"Пользователь @{first_user.name} "
                                                   f"удалил вас из друзей")
        else:
            bot.send_message(message.from_user.id, "Данный пользователь "
                                                   "не является вашим другом",
                             reply_markup=back_to_friends)

    else:
        bot.send_message(message.from_user.id, "Данный пользователь "
                                               "ещё не зарегистрирован",
                         reply_markup=back_to_friends)

    db_sess.commit()


def kosti_game(bot, user_id):
    user_choice, bot_choice = randint(0, 6), randint(0, 6)
    user = db_sess.query(User).filter(User.id == user_id).first()
    if user_choice > bot_choice:
        bot.send_message(user_id, f'Очки игрока:{user_choice}\n'
                                  f'Очки диллера:{bot_choice}\n'
                                  'Вы выиграли!')
        user.rate += 1
        bot.send_message(user_id, f'Ваш рейтинг: {user.rate}')
    elif user_choice == bot_choice:
        bot.send_message(user_id, 'Ничья! Ничего - лучше, чем минус :)')
    else:
        bot.send_message(user_id, f'Очки игрока:{user_choice}\n'
                                  f'Очки диллера:{bot_choice}\n'
                                  'Вы проиграли!')
        if user.rate > 0:
            user.rate -= 1
        bot.send_message(user_id, f'Ваш рейтинг: {user.rate}')
    db_sess.commit()


def start_roll_num(message, bot, kb, file):
    if message.text.strip() not in map(str, range(1, 37)):
        bot.send_message(message.chat.id, 'Вы неверно ввели ставку')
        bot.send_message(message.chat.id, 'Выберите интересующую вас игру',
                         reply_markup=kb)
    else:
        bot.send_message(message.chat.id, 'Ставка принята!')
        bot.send_document(message.from_user.id, document=file)
        user = db_sess.query(User).filter(User.id ==
                                             message.from_user.id).first()
        roll = randint(0, 36)
        bot.send_message(message.chat.id, f'Выпало {roll}')
        if roll == int(message.text.strip()):
            bot.send_message(message.chat.id, 'Вы выиграли!')
            user.rate += 25
            bot.send_message(message.from_user.id, f'Ваш рейтинг: {user.rate}')
        else:
            bot.send_message(message.from_user.id, 'Вы проиграли!')
            if user.rate > 4:
                user.rate -= 5
            bot.send_message(message.from_user.id, f'Ваш рейтинг: {user.rate}')
        db_sess.commit()
        bot.send_message(message.from_user.id, f'Ещё раз?',
                         reply_markup=kb)

def start_roll_colour(user_choice, bot, kb, file, user_id):
    result = randint(1, 36)
    bot.send_message(user_id, 'Ставка принята!')
    bot.send_document(user_id, document=file)
    user = db_sess.query(User).filter(User.id == user_id).first()
    if user_choice == 0:
        win = 50
    else:
        win = 5
    if result != 0:
        if result % 2 == 0:
            result = 'красный'
        else:
            result = 'чёрный'
    bot.send_message(user_id, f'Выпал {result}')
    if user_choice == result:
        bot.send_message(user_id, 'Вы выиграли!')
        user.rate += win
        bot.send_message(user_id, f'Ваш рейтинг: {user.rate}')
    else:
        bot.send_message(user_id, 'Вы проиграли!')
        if user.rate > 4:
            user.rate -= 5
        bot.send_message(user_id, f'Ваш рейтинг: {user.rate}')
    db_sess.commit()
    bot.send_message(user_id, f'Ещё раз?',
                     reply_markup=kb)