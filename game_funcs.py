import telebot
from data.users import User
from data import db_session, __all_models


def keybord_generate(buttons: list, width=3):
    """
    Универсальная функция для генерации inline-клавиатур.
    buttons - список словарей с параметрами кнопок, width - ширина клавиатуры
    в кнопках
    """
    markup = telebot.types.InlineKeyboardMarkup(row_width=width)
    for elem in buttons:
        button = (
            telebot.types.InlineKeyboardButton(text=elem['text'],
                                               callback_data=
                                               elem['callback_data'],
                                               url=elem['url'],
                                               callback_game=
                                               elem['callback_game']))
        markup.add(button)
    return markup


def callback_answer(bot, user_id, text, keybord, new_menu, db_session):
    send_msg = bot.send_message(user_id, text, reply_markup=keybord)
    print(send_msg)
    user = db_session.query(User).filter(User.id == \
                                      user_id).first()
    user.menu = new_menu
    db_session.commit()
