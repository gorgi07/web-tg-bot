import telebot
import sqlite3


API_TOKEN = '7168920535:AAFENbTdCAxujSoFc9KHomPtqynghWzjZIA'
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    con = sqlite3.connect('bot.db')
    cur = con.cursor()
    result = cur.execute('SELECT id from main').fetchall()
    if (message.from_user.id, ) not in result:
        bot.send_message(message.chat.id, f"Привет, "
                                          f"{message.from_user.username}! Я "
                                          f"бот с минииграми.\nВыбери "
                                          f"интересующее тебя меню.")
        cur.execute('INSERT INTO main VALUES (?, ?, ?, 0, "main")',
                    (message.from_user.id, 0,
                     message.from_user.username))
    else:
        bot.send_message(message.chat.id, 'Вы в главном меню, выберите, '
                                          'что вас интересует?')
        cur.execute('''UPDATE main
                    SET menu = ?
                    WHERE id = ?''', ('main', message.from_user.id))
    con.commit()
    con.close()


bot.infinity_polling()