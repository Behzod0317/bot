import psycopg2
from telebot import TeleBot
from telebot.types import Message
import datetime
bot = TeleBot("token")




DATABASE_URL = "postgres://user:password@host:port/dbname"


def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn


def insert_user_data(user_id, join_date, user_info):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "INSERT INTO users (user_id, join_date, user_info) VALUES (%s, %s, %s)"

    join_date = datetime.date(2023, 6, 22)  

    cursor.execute(query, (user_id, join_date, user_info))
    conn.commit()
    cursor.close()
    conn.close()


@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    user_id = message.from_user.id
    join_date = message.date
    user_info = f"{message.from_user.first_name} {message.from_user.last_name}"
    insert_user_data(user_id, join_date, user_info)
    bot.reply_to(message, "User information has been stored in the database.")

    # print(message)
bot.polling()
