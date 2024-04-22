import telebot
from data.users import User
from data.friends import Friend
from data import db_session, __all_models
from random import choice


db_session.global_init('db/bot.db')
db_sess = db_session.create_session()


def keybord_generate(buttons: list):
    """
    Универсальная функция для генерации inline-клавиатур.
    buttons - список словарей с параметрами кнопок, width - ширина клавиатуры
    в кнопках
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


def add_friend(message):
    user = db_session.query(Friend).filter(Friend.id ==
                                      message.from_user.id).first()
    print(f", {str(message.text).replace("@", "")}")
    user.output += f" {message.text.replase("@", "")}"
    db_session.commit()
