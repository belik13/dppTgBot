import sqlite3
import telebot
import os

bot = telebot.TeleBot("7388607968:AAGGLmsktgT_rTJV_e9D3fd6v-X6oWcQ41E")

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

dirpath = os.path.dirname(__file__)

def db_table_val(user_id: int, user_name: str):
    cursor.execute('INSERT INTO test (user_id, user_name) VALUES (?, ?)',
                   (user_id, user_name))
    conn.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать')


@bot.message_handler(commands=['defects'])
def defects_message(message):
    bot.send_message(message.chat.id, 'Отправьте ваш файл формата ".pts"')


@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    src ='FilesFromUsers/' + message.document.file_name;
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)

    file_name = new_file.name

    if not file_name.endswith(".pts"):
        os.remove(src)
        bot.reply_to(message, "Вы отправили файл не того формата")
    # else:
        # tod0 Обработка + Сохранение В БД

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет! Ваше имя добавлено в базу данных!')

        us_id = message.from_user.id
        us_name = message.from_user.first_name

        db_table_val(user_id=us_id, user_name=us_name)

bot.polling()