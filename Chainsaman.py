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
START HANDLER FOR GROUP

@bot.message_handler(commands=['start'], chat_types=['group', 'supergroup']) def start_in_group(message): try: chat_member = bot.get_chat_member(message.chat.id, bot.get_me().id) if chat_member.status in ['administrator', 'creator'] or message.text.startswith(f"/start@{bot.get_me().username}"): markup = types.InlineKeyboardMarkup() btn = types.InlineKeyboardButton("➡️ Start Your Contract", url=f"https://t.me/{bot.get_me().username}?start=start") markup.add(btn)

bot.send_photo(
            message.chat.id,
            photo="https://files.catbox.moe/qeqy19.jpg",
            caption=f"<b>{message.from_user.first_name}</b>, to begin your journey, tap below to start privately.",
            parse_mode="HTML",
            reply_to_message_id=message.message_id,
            reply_markup=markup
        )
except Exception as e:
    print(e)

START HANDLER FOR PRIVATE CHAT

@bot.message_handler(commands=['start'], chat_types=['private']) def start_in_dm(message): user_id = message.from_user.id username = message.from_user.username

conn = sqlite3.connect("chainsaw.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM user_data WHERE user_id = ?", (user_id,))
user = cursor.fetchone()

if not user:
    cursor.execute("""
        INSERT INTO user_data (user_id, username, level, exp, required_exp, yens, gems, crystals, tickets, energy, max_energy, last_energy_time, character)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, username, 1, 0, 12345, 0, 0, 0, 0, 10000, 10000, int(time.time()), None))
    conn.commit()
    conn.close()

    start_message = (
        "🔥 <b>WELCOME TO THE CHAINSAW MAN GAME</b> 🔥\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💀 <b>ENTER IF YOU DARE...</b>\n"
        "You've just crossed into a world where <b>Devils rule the shadows</b>,\n"
        "and <i>only the strongest Hunters survive.</i>\n\n"
        "Your soul is the price.\n"
        "Your blade is your answer.\n"
        "Your fate? Still unwritten.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚔️ <b>YOUR MISSION:</b>\n"
        "• 🧍‍♂️ Choose your Hunter\n"
        "• 👹 Hunt Devils\n"
        "• 🤝 Make Contracts\n"
        "• 🪙 Earn Yens, EXP & Gems\n"
        "• 🩸 Survive – Or die trying.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🕹️ <b>HOW TO BEGIN:</b>\n"
        "Press /choose_char to begin your contract.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 <i>“The chainsaw roars. Are you ready to bleed?”</i>"
    )

    choose_btn = types.InlineKeyboardMarkup()
    choose_btn.add(types.InlineKeyboardButton("🧍 Choose Character", callback_data="choose_char"))

    bot.send_photo(
        message.chat.id,
        photo="https://files.catbox.moe/bghkj1.jpg",
        caption=start_message,
        parse_mode="HTML",
        reply_markup=choose_btn
    )
else:
    conn.close()
    back_message = (
        "💀 <b>Welcome Back, Hunter!</b> 💀\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "You've already made your contract with us... and now, your journey continues!\n\n"
        "You’ve stepped away... but the devils never rest.\n"
        "Your fate still awaits — will you rise or fall?\n\n"
        "⚡️ <b>What’s Next?</b>\n"
        "• 🧍‍♂️ Your Hunter is waiting\n"
        "• 👹 Devils are still out there\n"
        "• 🤝 Keep making powerful contracts\n"
        "• 🩸 Fight, earn, and survive\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 GameBot whispers:\n"
        "<i>“The chainsaw roars again... Are you ready?”</i>\n\n"
        "➡️ <a href='https://t.me/chainsaw_man_group69'>Join the group and continue your adventure</a>"
    )

    bot.send_photo(
        message.chat.id,
        photo="https://files.catbox.moe/bghkj1.jpg",
        caption=back_message,
        parse_mode="HTML"
    )




# Main function to start the bot
if __name__ == "__main__":
    create_table()  # Create table if not exists
    bot.polling(none_stop=True)
