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


def callback_answer(bot, user_id, text, keybord, call):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(user_id, text, reply_markup=keybord)


def tsuefa_game(bot, user_choice, db_session, user_id):
    bot_choice = choice(['Камень', 'Ножницы', 'Бумага'])
    rules = {
        'камень': 'ножницы',
        'ножницы': 'бумага',
        'бумага': 'камень'
    }
    user = db_session.query(User).filter(User.id == user_id).first()
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
    db_session.commit()


def add_friend(message, bot):
    new_friend = str(message.text).replace("@", "")
    first_user = db_sess.query(Friend).filter(Friend.id ==
                                              message.from_user.id).first()
    second_user = db_sess.query(Friend).filter(Friend.name == new_friend).first()
    if second_user:
        first_user.friends_input += f" {second_user.id}"
        second_user.friends_output += f" {first_user.id}"
        bot.send_message(message.from_user.id, "Запрос дружбы успешно отправлен",
                         reply_markup=keybord_generate([{'text': 'Назад',
                                                         'callback_data': 'friends_menu',
                                                         'url': None}
                                                        ]))
        bot.send_message(second_user.id, f"Пользователь @{first_user.name} отправил вам запрос дружбы",
                         reply_markup=keybord_generate([{'text': 'Принять',
                                                         'callback_data': " ".join(['yes_add_friend', str(first_user.id), str(second_user.id)]),
                                                         'url': None},
                                                        {'text': 'Отклонить',
                                                         'callback_data': " ".join(['no_add_friend', str(first_user.id), str(second_user.id)]),
                                                         'url': None}]))
    else:
        print("No")

    db_sess.commit()


def kosti_game(bot, db_session, user_id):
    user_choice, bot_choice = randint(0, 6), randint(0, 6)
    user = db_session.query(User).filter(User.id == user_id).first()
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
    db_session.commit()
