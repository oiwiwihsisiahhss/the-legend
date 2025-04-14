import telebot
import time
import sqlite3
from telebot import types
from datetime import datetime
import os

# Initialize bot with your API key
API_KEY = '7215821191:AAEzFPwyx8FjlXMr2mpVTbYzpHoMbPsaCDc'
bot = telebot.TeleBot(API_KEY)

if os.path.exists("chainsaw.db"):
    os.remove("chainsaw.db")
# Database Setup
def create_connection():
    return sqlite3.connect('chainsaw.db')
    

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
        last_energy_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        choosen_character TEXT DEFAULT NULL
    )''')
    connection.commit()
    connection.close() 


    
# GROUP START HANDLER
@bot.message_handler(commands=['start'], chat_types=['group', 'supergroup'])
def start_in_group(message):
    try:
        chat_member = bot.get_chat_member(message.chat.id, bot.get_me().id)
        if chat_member.status in ['administrator', 'creator'] or message.text.startswith(f"/start@{bot.get_me().username}"):
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("➡️ Start Your Contract", url=f"https://t.me/{bot.get_me().username}?start=start")
            markup.add(btn)

            bot.send_photo(
                message.chat.id,
                photo="https://files.catbox.moe/qeqy19.jpg",
                caption=f"<b>{message.from_user.first_name}</b>, to begin your journey, tap below to start privately.",
                reply_to_message_id=message.message_id,
                reply_markup=markup, 
                parse_mode = "HTML"
            )
    except Exception as e:
        print(e)


# PRIVATE START HANDLER
@bot.message_handler(commands=['start'], chat_types=['private'])
def start_in_dm(message):
    user_id = message.from_user.id
    username = message.from_user.username

    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_data WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    

    if not user:
        cursor.execute("""
    INSERT INTO user_data (
        user_id, username, level, exp, required_exp, yens,
        crystals, tickets, energy, max_energy,
        last_energy_time, choosen_character
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    user_id, username, 1, 0, 12345, 250,  # Use 250 for yens per your default
    0, 0, 10000, 10000,
    int(time.time()), None
))

                

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
            reply_markup=choose_btn, 
            parse_mode = "HTML"
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
            parse_mode = "HTML"
        )




@bot.message_handler(commands=['open'])
def open_menu(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "This command only works in private messages.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/explore")
    btn2 = types.KeyboardButton("/close")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "/close")
def close_menu(message):
    hide_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Keyboard closed.", reply_markup=hide_markup)

@bot.message_handler(func=lambda message: message.text == "/explore")
def explore_action(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "This command only works in private messages.")
        return

    bot.send_message(message.chat.id, "You chose to explore!")

GROUP_ID = -1002680551934 # Replace with your group chat ID

# Announcement function
def announce_open_feature():
    message = (
        "🔥 Attention, Devil Hunters! 🔥\n\n"
        "Your **Daily Reward** is here!\n\n"
        "💀 Today's reward includes:\n"
        "- **150 Yens**\n"
        "- **100 Gems**\n\n"
        "💎 Stay sharp and claim your rewards every day!\n"
        "The hunt never stops! 🏹💀\n\n"
        "Keep battling, and may your chainsaws stay sharp! ⚔️"
    
    )
    bot.send_message(chat_id=GROUP_ID, text=message, parse_mode='Markdown')
def on_start():
    announce_open_feature()

# Call announcement when the bot starts
on_start()



GROUP9_ID = -1002680551934
GROUP_LINK = "https://t.me/chainsaw_man_group69"
DAILY_CRYSTALS = 250

conn = sqlite3.connect("chainsaw.db", check_same_thread=False)
cursor = conn.cursor()

# Function to check if bot is admin or tagged
def is_allowed(message):
    if message.chat.type != "supergroup":
        return False
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
        return True
    admins = bot.get_chat_administrators(message.chat.id)
    bot_id = bot.get_me().id
    return any(admin.user.id == bot_id for admin in admins)

@bot.message_handler(commands=['daily'])
def handle_daily(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    now = datetime.now()

    # Only in group
    if message.chat.type == "private":
        bot.send_message(
            chat_id,
            f"⛔️ You can only claim daily rewards in the official group.\n\n➡️ [Join Group Here]({GROUP_LINK})",
            parse_mode="Markdown", disable_web_page_preview=True)
        return

    if chat_id != GROUP9_ID or not is_allowed(message):
        return  # Only respond if in the right group AND tagged or admin

    # Ensure user exists
    cursor.execute("SELECT 1 FROM user_data WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT OR IGNORE INTO user_data (user_id) VALUES (?)", (user_id,))
        conn.commit()

    # Check last claim
    cursor.execute("SELECT last_claimed FROM daily_rewards WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if row and row[0]:
        last_claimed = datetime.fromisoformat(row[0])
        if now < last_claimed + timedelta(hours=24):
            remaining = (last_claimed + timedelta(hours=24)) - now
            h, rem = divmod(int(remaining.total_seconds()), 3600)
            m, s = divmod(rem, 60)
            bot.reply_to(message, f"⏳ Already claimed.\nTry again in: {h:02}:{m:02}:{s:02}")
            return

    # Grant reward
    cursor.execute("UPDATE user_data SET crystals = crystals + ? WHERE user_id = ?", (DAILY_CRYSTALS, user_id))
    cursor.execute("INSERT OR REPLACE INTO daily_rewards (user_id, last_claimed) VALUES (?, ?)", (user_id, now.isoformat()))
    conn.commit()

    bot.reply_to(message, f"✅ You received {DAILY_CRYSTALS} Crystals!\nCome back tomorrow for more.")
# Main function to start the bot
if __name__ == "__main__":
    create_table()  # Create table if not exists
    bot.polling(none_stop=True)
