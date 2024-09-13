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

    cursor.execute('SELECT health, attack, defense, xp, level FROM players WHERE id = ?', (user_id,))
    player = cursor.fetchone()

    if player:
        health, attack, defense, xp, level = player
        bot.send_message(message.chat.id, f"Player Stats:\nHealth: {health}\nAttack: {attack}\nDefense: {defense}\nXP: {xp}\nLevel: {level}")
    else:
        bot.send_message(message.chat.id, "You are not registered yet. Use /start to register.")

# Команда для начала боя
@bot.message_handler(commands=['fight'])
def start_fight(message):
    user_id = message.from_user.id

    cursor.execute('SELECT health, attack, defense, xp, level FROM players WHERE id = ?', (user_id,))
    player = cursor.fetchone()

    if player:
        health, attack, defense, xp, level = player

        # Враги и их параметры
        enemies = [
            {"name": "Wild Hamster", "health": 50, "attack": 5, "defense": 2},
            {"name": "Furious Squirrel", "health": 70, "attack": 7, "defense": 3}
        ]
        enemy = random.choice(enemies)

        bot.send_message(message.chat.id, f"A wild {enemy['name']} appears! Prepare to fight!")

        # Простая система боя
        while health > 0 and enemy['health'] > 0:
            # Игрок атакует
            damage_to_enemy = max(0, attack - enemy['defense'])
            enemy['health'] -= damage_to_enemy
            bot.send_message(message.chat.id, f"You deal {damage_to_enemy} damage to {enemy['name']}!")

            if enemy['health'] <= 0:
                bot.send_message(message.chat.id, f"You defeated {enemy['name']}!")
                xp_gain = random.randint(10, 20)
                cursor.execute('UPDATE players SET xp = xp + ? WHERE id = ?', (xp_gain, user_id))
                
                # Проверяем, повысился ли уровень
                cursor.execute('SELECT xp, level FROM players WHERE id = ?', (user_id,))
                xp, level = cursor.fetchone()
                if xp >= level * 100:  # Каждые 100 XP - новый уровень
                    cursor.execute('UPDATE players SET level = level + 1, xp = 0 WHERE id = ?', (user_id,))
                    bot.send_message(message.chat.id, "Congratulations! You have leveled up!")
                conn.commit()
                return

            # Враг атакует
            damage_to_player = max(0, enemy['attack'] - defense)
            health -= damage_to_player
            bot.send_message(message.chat.id, f"{enemy['name']} deals {damage_to_player} damage to you!")

            if health <= 0:
                bot.send_message(message.chat.id, "You were defeated!")
                cursor.execute('UPDATE players SET health = 100 WHERE id = ?', (user_id,))
                conn.commit()
                return

        # Обновляем здоровье игрока после боя
        cursor.execute('UPDATE players SET health = ? WHERE id = ?', (health, user_id))
        conn.commit()
    else:
        bot.send_message(message.chat.id, "You are not registered yet. Use /start to register.")
# Команда для получения помощи
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Available commands:\n"
        "/start - Register or re-register\n"
        "/status - Check your player stats\n"
        "/fight - Start a fight with a random enemy\n"
        "/help - Show this help message"
    )
    bot.send_message(message.chat.id, help_text)

# Команда для сброса состояния игрока
@bot.message_handler(commands=['reset'])
def reset_status(message):
    user_id = message.from_user.id
    cursor.execute('UPDATE players SET health = 100, xp = 0 WHERE id = ?', (user_id,))
    conn.commit()
    bot.send_message(message.chat.id, "Your stats have been reset.")


# Запуск бота
bot.polling()
