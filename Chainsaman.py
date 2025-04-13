import telebot
import sqlite3
from telebot import types
from datetime import datetime

# Initialize bot with your API key
API_KEY = '7215821191:AAEzFPwyx8FjlXMr2mpVTbYzpHoMbPsaCDc'
bot = telebot.TeleBot(API_KEY)

# Database Setup
def create_connection():
    return sqlite3.connect('user_data.db')

def create_table():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        required_exp INTEGER DEFAULT 12345,
        yens INTEGER DEFAULT 250,
        crystals INTEGER DEFAULT 0,
        tickets INTEGER DEFAULT 0,
        energy INTEGER DEFAULT 10000,
        max_energy INTEGER DEFAULT 10000,
        last_energy_refill TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        chosen_character TEXT DEFAULT NULL
    )''')
    connection.commit()
    connection.close()

# Start Command for Groups
@bot.message_handler(commands=['start'])
def start_group(message):
    user = message.from_user
    if message.chat.type == "private":
        # Private chat setup (new user or returning user)
        connection = create_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM user_data WHERE user_id = ?', (user.id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            # Add new user to the database
            cursor.execute('''
            INSERT INTO user_data (user_id, username) VALUES (?, ?)
            ''', (user.id, user.username))
            connection.commit()

            # Send Welcome Message
            bot.send_message(
                message.chat.id,
                f"🔥 Welcome to the Chainsaw Man Game, {user.first_name}! 🔥\n\n"
                "⚔️ Fight devils, earn rewards, and become the strongest hunter! ⚔️",
                parse_mode="HTML"
            )

            # Send Character Selection
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Choose Character", callback_data="choose_char"))
            bot.send_message(message.chat.id, "Click below to choose your character!", reply_markup=markup)

            bot.send_photo(message.chat.id, "https://files.catbox.moe/qeqy19.jpg")
        else:
            # If user exists
            bot.send_message(
                message.chat.id,
                "Welcome Back! Please join the group to continue playing.",
                parse_mode="HTML"
            )
        connection.close()

    else:
        # Group message setup
        bot.send_message(
            message.chat.id,
            f"🔥 Welcome to the Chainsaw Man Game, {user.first_name}! 🔥\n\n"
            "⚔️ Fight devils, earn rewards, and become the strongest hunter! ⚔️",
            parse_mode="HTML"
        )

        # Send character selection button
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Start Contract", url=f"t.me/{bot.get_me().username}?start={user.id}"))
        bot.send_message(message.chat.id, "Click below to start your contract!", reply_markup=markup)

        bot.send_photo(message.chat.id, "https://files.catbox.moe/qeqy19.jpg")

# Character Selection Command
@bot.callback_query_handler(func=lambda call: call.data == "choose_char")
def choose_character(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Hirokazu", callback_data="hiro"),
        types.InlineKeyboardButton("Kobeni", callback_data="kobeni"),
        types.InlineKeyboardButton("Akane", callback_data="akane")
    )
    bot.edit_message_text(
        "Choose your character!",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# Character Selected Callback
@bot.callback_query_handler(func=lambda call: call.data in ["hiro", "kobeni", "akane"])
def character_selected(call):
    user = call.from_user
    character = call.data

    connection = create_connection()
    cursor = connection.cursor()

    # Update the user's selected character in the database
    cursor.execute('UPDATE user_data SET chosen_character = ? WHERE user_id = ?', (character, user.id))
    connection.commit()

    # Inform the user of their selection
    bot.edit_message_text(
        f"Your chosen character is: {character.capitalize()}",
        call.message.chat.id,
        call.message.message_id
    )
    connection.close()

# Main function to start the bot
if __name__ == "__main__":
    create_table()  # Create table if not exists
    bot.polling(none_stop=True)
