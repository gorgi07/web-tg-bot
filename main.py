# Импорт
import telebot
from data.users import User
from data import db_session, __all_models
from game_funcs import keybord_generate

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
                              'callback_game': None}], width=2)


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


# бесконечный поток запросов к серверам telegram
bot.infinity_polling()