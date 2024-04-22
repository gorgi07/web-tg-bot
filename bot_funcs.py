import telebot
from data.users import User
from data import db_session, __all_models


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
