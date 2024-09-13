import telebot
import sqlite3
import random

# Telegram bot token
TOKEN = '6050751852:AAHrS5D7NjCdizmL8n_cI_9QMesLgJeWRf0'
bot = telebot.TeleBot(TOKEN)

# Подключаемся к базе данных
conn = sqlite3.connect('game.db', check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу для хранения данных игроков
cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY,
        username TEXT,
        health INTEGER DEFAULT 100,
        attack INTEGER DEFAULT 10,
        defense INTEGER DEFAULT 5,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1
    )
''')
conn.commit()

# Регистрация нового игрока
@bot.message_handler(commands=['start'])
def register_player(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Проверяем, есть ли игрок в базе данных
    cursor.execute('SELECT * FROM players WHERE id = ?', (user_id,))
    player = cursor.fetchone()

    if player is None:
        # Добавляем игрока в базу данных
        cursor.execute('INSERT INTO players (id, username) VALUES (?, ?)', (user_id, username))
        conn.commit()
        bot.send_message(message.chat.id, f"Welcome, {username}! You have been registered.")
    else:
        bot.send_message(message.chat.id, "You are already registered.")

# Команда для просмотра статуса игрока
@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.from_user.id

    cursor.execute('SELECT health, attack, defense, xp, level FROM players WHERE id = ?', (u
