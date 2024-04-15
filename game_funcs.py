import telebot


def keybord_generate(buttons: list, width=3):
    '''Универсальная функция для генерации inline-клавиатур.
    buttons - список словарей с параметрами кнопок, width - ширина клавиатуры
    в кнопках'''
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