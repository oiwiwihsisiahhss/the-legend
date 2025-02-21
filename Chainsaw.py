import telebot
import sqlite3
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Token
TOKEN = "7215821191:AAH7YBa2FQi-0lfNHAnZMQtBAENTO1paw6A"
bot = telebot.TeleBot(TOKEN)

# Database Setup
conn = sqlite3.connect("bot_data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    selected_character TEXT,
    gems INTEGER DEFAULT 0,
    yens INTEGER DEFAULT 0,
    exp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    last_daily_claim TEXT,
    has_started INTEGER DEFAULT 0
)
""")
conn.commit()

# Character Data
characters = {
    "Himeno": {
        "health": 85, "attack": 60, "defense": 70,
        "special_ability": "Phantom Strike", "exp_needed": 1000,
        "description": "A relentless hunter who walks the line between the living and the dead.",
        "image": "https://files.catbox.moe/i3vcf7.jpg"
    },
    "Hirokazu": {
        "health": 75, "attack": 65, "defense": 60,
        "special_ability": "Shield Bash", "exp_needed": 1000,
        "description": "A determined warrior with unwavering loyalty.",
        "image": "https://files.catbox.moe/2l5fw0.jpg"
    },
    "Kishibe": {
        "health": 90, "attack": 70, "defense": 80,
        "special_ability": "Demon Slayer", "exp_needed": 1000,
        "description": "A battle-hardened veteran feared by devils.",
        "image": "https://files.catbox.moe/xg6bdl.jpg"
    }
}

# Initialize user in the database
def initialize_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

# /start function
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    initialize_user(user_id)

    cursor.execute("SELECT has_started FROM users WHERE user_id=?", (user_id,))
    has_started = cursor.fetchone()[0]

    if has_started:
        bot.send_message(user_id, "❌ You have already started the bot.")
        return

    cursor.execute("UPDATE users SET has_started = 1 WHERE user_id = ?", (user_id,))
    conn.commit()

    keyboard = InlineKeyboardMarkup()
    choose_char_button = InlineKeyboardButton("🎭 Choose Character", callback_data="choose_char")
    keyboard.add(choose_char_button)

    start_msg = """
🔥 *Welcome to the Chainsaw Man Game!* 🔥
━━━━━━━━━━━━━
💀 Choose your character and embark on a thrilling adventure! 💀
⚔️ Fight devils, earn rewards, and become the strongest hunter! ⚔️
━━━━━━━━━━━━━
"""

    bot.send_photo(user_id, "https://files.catbox.moe/qeqy19.jpg", caption=start_msg, parse_mode="Markdown", reply_markup=keyboard)

# /choose_char function
@bot.callback_query_handler(func=lambda call: call.data == "choose_char")
def choose_char(call):
    user_id = call.from_user.id

    keyboard = InlineKeyboardMarkup()
    for char_name in characters.keys():
        keyboard.add(InlineKeyboardButton(char_name, callback_data=char_name))

    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "🎭 *Choose your character:*", reply_markup=keyboard, parse_mode="Markdown")

# Character selection
@bot.callback_query_handler(func=lambda call: call.data in characters)
def handle_char_selection(call):
    user_id = call.from_user.id
    character_name = call.data
    initialize_user(user_id)

    cursor.execute("UPDATE users SET selected_character = ? WHERE user_id = ?", (character_name, user_id))
    conn.commit()

    char = characters[character_name]
    stats = f"""
🩸 _{character_name}_ 🩸
━━━━━━━━━━━━━
❤️ Health: 〘 {char['health']} HP 〙
⚔️ Attack: 〘 {char['attack']} 〙
🛡 Defense: 〘 {char['defense']} 〙
👻 Special Ability: _{char['special_ability']}_ 
🔺 EXP Needed: 〘 {char['exp_needed']} 〙
━━━━━━━━━━━━━
💀 *{char['description']}*
"""

    bot.answer_callback_query(call.id)
    bot.send_photo(user_id, char["image"], caption=stats, parse_mode="Markdown")

# /stats function
@bot.message_handler(commands=['stats'])
def stats(message):
    user_id = message.from_user.id
    initialize_user(user_id)

    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) < 2:
        bot.send_message(user_id, "❌ Please specify a character name. Example: `/stats Himeno`", parse_mode="Markdown")
        return

    requested_character = command_parts[1].strip()

    cursor.execute("SELECT selected_character FROM users WHERE user_id=?", (user_id,))
    user_character = cursor.fetchone()

    if not user_character or not user_character[0]:
        bot.send_message(user_id, "❌ You haven't selected a character yet. Use /choose_char to select one.")
        return

    selected_character = user_character[0]

    if requested_character.lower() != selected_character.lower():
        bot.send_message(user_id, f"❌ You don't own {requested_character}. You have `{selected_character}`.", parse_mode="Markdown")
        return

    if selected_character in characters:
        char_stats = characters[selected_character]
        stats_message = f"""
🩸 _{selected_character}_ 🩸
━━━━━━━━━━━━━
❤️ Health: 〘 {char_stats['health']} HP 〙
⚔️ Attack: 〘 {char_stats['attack']} 〙
🛡 Defense: 〘 {char_stats['defense']} 〙
👻 Special Ability: _{char_stats['special_ability']}_ 
🔺 EXP Needed: 〘 {char_stats['exp_needed']} 〙
━━━━━━━━━━━━━
💀 *{char_stats['description']}*
"""
        bot.send_photo(user_id, char_stats["image"], caption=stats_message, parse_mode="Markdown")

# /balance command
@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.from_user.id
    initialize_user(user_id)

    cursor.execute("SELECT gems, yens, exp, level FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()

    balance_msg = f"""
╔════════════════════╗
      🎭 HUNTER'S BALANCE 🎭
╚════════════════════╝
💴 Yens: ❲ {user_data[1]} ❳  
💎 Gems: ❲ {user_data[0]} ❳  
📊 Level: ❲ {user_data[3]} ❳  
🔺 EXP: ❲ {user_data[2]} ❳  
━━━━━━━━━━━━━━━━━━━━━
⚡ Keep pushing forward, hunter! ⚡  
"""

    bot.send_message(user_id, balance_msg, parse_mode="Markdown")

# /daily function
@bot.message_handler(commands=['daily'])
def daily(message):
    user_id = message.chat.id
    group_id = -1002369433935

    if message.chat.id != group_id:
        bot.send_message(user_id, "❌ You can only claim the daily reward in the official group!")
        return

    cursor.execute("UPDATE users SET gems = gems + 100, yens = yens + 150, last_daily_claim = ? WHERE user_id = ?",
                   (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    conn.commit()

    bot.send_message(user_id, "🎉 You've claimed your daily rewards! \n💎 100 Gems\n💰 150 Yens")

# Start the bot
bot.polling()
