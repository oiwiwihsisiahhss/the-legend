import telebot
import os
import time
import math
import sqlite3
from telebot import types
from datetime import datetime, timedelta

import html

# Initialize bot with your API key
API_KEY = '7215821191:AAEzFPwyx8FjlXMr2mpVTbYzpHoMbPsaCDc'
bot = telebot.TeleBot(API_KEY)


def create_connection():
    return sqlite3.connect('chainsaw.db')
    


#DB_PATH = "/mnt/data/chainsaw.db"  # This is the persistent directory on StackHost
#os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
def create_table():
    connection = create_connection()
    cursor = connection.cursor()

    # Create user_data table
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
        )
    ''')

    # Create daily_rewards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_rewards (
            user_id INTEGER PRIMARY KEY,  
            last_claimed TIMESTAMP DEFAULT NULL,  
            FOREIGN KEY (user_id) REFERENCES user_data (user_id)
        )
    ''')

    # Create hunter_ranks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hunter_ranks (
            rank TEXT PRIMARY KEY,
            required_level INTEGER
        )
    ''')

    # Insert default hunter ranks
    cursor.execute('''
        INSERT OR IGNORE INTO hunter_ranks (rank, required_level) VALUES 
        ('E Rank - Novice Hunter 🪶', 1),
        ('D Rank - Rookie Hunter ⚔️', 25),
        ('C Rank - Skilled Hunter 🛡️', 50),
        ('B Rank - Elite Hunter 🏹', 100),
        ('A Rank - Master Hunter 🔥', 175),
        ('S Rank - Legendary Hunter 👑', 220)
    ''')

    # Create user_balance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_balance (
            user_id INTEGER PRIMARY KEY,
            yens INTEGER DEFAULT 0,
            crystals INTEGER DEFAULT 0,
            tickets INTEGER DEFAULT 0,
            energy INTEGER DEFAULT 10000,
            max_energy INTEGER DEFAULT 10000
        )
    ''')

    connection.commit()
    connection.close()

create_table() 
    
# GROUP START HANDLER
def check_and_handle_level_up(user_id, bot):
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    user = cursor.execute("SELECT level, exp, yens, crystals FROM user_data WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        conn.close()
        return

    level, exp, yens, crystals = user
    leveled_up = False
    message = ""

    while True:
        required_exp = int(12345 * (level ** 1.5))
        if exp < required_exp:
            break

        exp -= required_exp
        level += 1
        leveled_up = True

        reward_yens = 150 + 20 * level ** 2
        reward_crystals = 5 + 3 * level ** 2

        yens += reward_yens
        crystals += reward_crystals

        message += f"⚡️ You've leveled up to Level {level}!\n+{reward_yens} Yens\n+{reward_crystals} Crystals\n\n"

    cursor.execute("UPDATE user_data SET level = ?, exp = ?, yens = ?, crystals = ? WHERE user_id = ?",
                   (level, exp, yens, crystals, user_id))
    conn.commit()
    conn.close()

    if leveled_up:
        try:
            bot.send_message(user_id, message.strip())
        except Exception as e:
            print(f"Error sending level-up message to user {user_id}: {e}")
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
#def announce_open_feature():
    #message = ( """
#\u2705 The 'user_balance' table has been successfully created in the database! \U0001F389

#This table will track user balances, including:
#- **Yens** \U0001F4B4
#- **Crystals** \U0001F52E
#- **Tickets** \U0001F39F
#- **Energy** \U000026A1

#The system is now ready to handle user balance data.
#"""
    
 #   )
   # bot.send_message(chat_id=GROUP_ID, text=message, parse_mode='Markdown')
#def on_start():
    #announce_open_feature()

# Call announcement when the bot starts
#on_start()



GROUP9_ID = -1002680551934
GROUP_LINK = "https://t.me/chainsaw_man_group69"


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

# Check if user can claim daily reward


conn = sqlite3.connect("chainsaw.db", check_same_thread=False)
cursor = conn.cursor()

GROUP_LINK = "https://t.me/chainsaw_man_group69"

from datetime import datetime, timedelta

GROUP_LINK = "https://t.me/chainsaw_man_group69"

# --- Utility: Ensure user exists ---
def ensure_user_exists(user_id, username):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM user_data WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO user_data (user_id, username)
            VALUES (?, ?)
        """, (user_id, username))
        conn.commit()
    cursor.close()

# --- Utility: Check daily claim time ---
def can_claim_daily(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT last_claimed FROM daily_rewards WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    if result and result[0]:
        return datetime.fromisoformat(result[0])
    return None

# --- Utility: Update last claim timestamp ---
# --- Utility: Update last claim timestamp ---
def update_last_claim_time(user_id):
    now = datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO daily_rewards (user_id, last_claimed)
        VALUES (?, ?)
    """, (user_id, now))
    conn.commit()
    cursor.close()

# --- Utility: Update balance ---
def update_balance(user_id, yens=0, crystals=0):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE user_data
        SET yens = yens + ?, crystals = crystals + ?
        WHERE user_id = ?
    """, (yens, crystals, user_id))
    conn.commit()
    cursor.close()

# --- /daily command ---
@bot.message_handler(commands=['daily'])
def handle_daily(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    chat_id = message.chat.id

    # Must be used in group chat
    if message.chat.type == "private":
        bot.reply_to(message, f"❌ You can only claim daily rewards in the official group.\n👉 [Join our official group]({GROUP_LINK})", parse_mode="Markdown")
        return

    ensure_user_exists(user_id, username)

    last_claim_time = can_claim_daily(user_id)
    now = datetime.now()

    if not last_claim_time or now - last_claim_time >= timedelta(hours=24):
        update_balance(user_id, yens=250, crystals=100)
        update_last_claim_time(user_id)

        bot.reply_to(message, "✅ Daily reward claimed!\n\n+ 250 Yens\n+ 100 Crystals\n\nCome back in 24 hours!")
    else:
        remaining = timedelta(hours=24) - (now - last_claim_time)
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        bot.reply_to(message, f"⏳ You already claimed your daily reward!\n<blockquote>Come back in {hours}h {minutes}m {seconds}s.</blockquote>", parse_mode="HTML")



#@bot.message_handler(commands=['balance'])
@bot.message_handler(commands=['balance'])
def handle_balance(message):
    from datetime import datetime
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chat_id = message.chat.id

    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, username, join_date, level, exp, yens, crystals, tickets, energy, max_energy, last_energy_time, choosen_character
        FROM user_data WHERE user_id = ?
    """, (user_id,))
    
    user = cursor.fetchone()

    if not user:
        bot.reply_to(message, "❌ You haven't started the game yet.\nUse /start in the group to begin.")
        conn.close()
        return

    # Unpack values from the user tuple
    user_id, username, join_date, level, exp, yens, crystals, tickets, energy, max_energy, last_energy_time, chosen_character = user

    # Calculate required EXP dynamically
    required_exp = int(12345 * (level ** 1.5))

    # Fetch rank based on level
    cursor.execute('''
        SELECT rank FROM hunter_ranks
        WHERE required_level <= ?
        ORDER BY required_level DESC
        LIMIT 1
    ''', (level,))
    result = cursor.fetchone()
    rank = result[0] if result else "Unranked"

    def create_bar(current, total):
        filled = int((current / total) * 10) if total else 0
        return "█" * filled + "░" * (10 - filled)

    energy_bar = create_bar(energy, max_energy)
    exp_bar = create_bar(exp, required_exp)

    readable_date = datetime.strptime(join_date, "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y")
    conn.close()

    balance_message = f"""
<b>[CHAINSAW CONTRACT PROFILE]</b>\n
🔗 <b>Name:</b> <a href="tg://user?id={user_id}">{user_name}</a>
🆔 <b>UID:</b> <code>{user_id}</code>
🕰️ <b>Joined:</b> {readable_date}
🆙 <b>Level:</b> {level}
༺═━━━━━━━━━━━━━━━━━━━━═༻
💴 <b>Yens:</b> {yens}
🔮 <b>Crystals:</b> {crystals}
🎟️ <b>Tickets:</b> {tickets}
༺═━━━━━━━━━━━━━━━━━━━═༻
⚡ <b>Energy</b>
{energy_bar}  {energy} / {max_energy}
✨ <b>EXP</b>
{exp_bar}  {exp} / {required_exp}
༺═━━━━━━━━━━━━━━━━━━━━═༻
⚔️ <b>Rank:</b> {rank}
"""


    

    # Exit button
    keyboard = types.InlineKeyboardMarkup()
    exit_btn = types.InlineKeyboardButton("❌ Exit", callback_data=f"exit_{user_id}")
    keyboard.add(exit_btn)

    bot.send_message(chat_id, balance_message.strip(), parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('exit_'))
def close_balance_table(call):
    user_id = call.from_user.id
    target_id = int(call.data.split('_')[1])

    if user_id == target_id:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Closed.")
    else:
        bot.answer_callback_query(call.id, "❌ You can't close someone else's profile.")
@bot.message_handler(commands=['add'])
def add_resource(message):
    # Only allow the admin
    if message.from_user.id != 6306216999:
        return

    if not message.reply_to_message:
        bot.reply_to(message, "Please reply to the user's message to use this command.")
        return

    try:
        args = message.text.split()
        if len(args) != 3:
            bot.reply_to(message, "Usage: /add [resource] [amount]\nExample: /add tokens 100 or /add tokens -100")
            return

        resource = args[1].lower()
        amount = int(args[2])
        valid_resources = ['yens', 'crystals', 'tickets', 'exp']

        if resource not in valid_resources:
            bot.reply_to(message, f"Invalid resource. Choose from: {', '.join(valid_resources)}")
            return

        user_id = message.reply_to_message.from_user.id
        username = message.from_user.full_name or "unknown"
        target_name = message.reply_to_message.from_user.full_name or "unknown"
        conn = sqlite3.connect("chainsaw.db")
        cursor = conn.cursor()

        cursor.execute(f"UPDATE user_data SET {resource} = {resource} + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()

        action = "added" if amount > 0 else "deducted"
        amount_display = abs(amount)

        hyperlink = f"<a href='tg://user?id={user_id}'>{target_name}</a>"
        reply_msg = f"<b>{resource.capitalize()} {action} by {amount_display} for {hyperlink}</b>"
        bot.reply_to(message, reply_msg, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")  
    check_and_handle_level_up(user_id, bot)       
  # Handle the exception here  pass

import sqlite3

@bot.message_handler(commands=['give'])
def handle_give(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ You must reply to the user you want to give resources to.")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "❌ Usage: /give <amount_type> <amount>\nExample: /give yens 100")
        return

    amount_type = args[1].lower()
    try:
        amount = int(args[2])
    except ValueError:
        bot.reply_to(message, "❌ Amount must be a number.")
        return

    valid_types = ['yens', 'crystals', 'tickets', 'energy']
    if amount_type not in valid_types:
        bot.reply_to(message, f"❌ Invalid resource type. Choose from: {', '.join(valid_types)}")
        return

    giver_id = message.from_user.id
    receiver_id = message.reply_to_message.from_user.id

    if giver_id == receiver_id:
        bot.reply_to(message, "❌ You can't give resources to yourself.")
        return

    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    # Check giver
    cursor.execute("SELECT yens, crystals, tickets, energy FROM user_data WHERE user_id = ?", (giver_id,))
    giver = cursor.fetchone()
    if not giver:
        bot.reply_to(message, "❌ You haven't started the game yet.")
        conn.close()
        return

    giver_balance = dict(zip(valid_types, giver))
    if giver_balance[amount_type] < amount:
        bot.reply_to(message, f"❌ You don’t have enough {amount_type} to give.")
        conn.close()
        return

    # Check receiver
    cursor.execute("SELECT yens, crystals, tickets, energy FROM user_data WHERE user_id = ?", (receiver_id,))
    receiver = cursor.fetchone()
    if not receiver:
        bot.reply_to(message, "❌ The user you are trying to give to has not started the game.")
        conn.close()
        return

    # Update balances
    cursor.execute(f"UPDATE user_data SET {amount_type} = {amount_type} - ? WHERE user_id = ?", (amount, giver_id))
    cursor.execute(f"UPDATE user_data SET {amount_type} = {amount_type} + ? WHERE user_id = ?", (amount, receiver_id))
    conn.commit()
    conn.close()

    bot.reply_to(message, f"✅ Successfully transferred {amount} {amount_type} to {message.reply_to_message.from_user.first_name}.")
bot.polling(none_stop=True)
