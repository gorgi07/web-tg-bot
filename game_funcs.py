import sqlite3

con = sqlite3.connect('bot.db')
cur = con.cursor()
cur.execute('delete from main where id = NULL')
con.commit()
con.close()