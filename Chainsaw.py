import telebot
import random
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Token
TOKEN = "7215821191:AAH7YBa2FQi-0lfNHAnZMQtBAENTO1paw6A"
bot = telebot.TeleBot(TOKEN)

# Group ID where /daily is allowed
OFFICIAL_GROUP_ID = -1002369433935

# Character Data
characters = {
    "Himeno": {
        "health": 85, "attack": 60, "special_ability": "Phantom Strike", "exp_needed": 1000,
        "description": "A relentless hunter who walks the line between the living and the dead.",
        "image": "https://files.catbox.moe/i3vcf7.jpg"
    },
    "Hirokazu": {
        "health": 75, "attack": 65, "special_ability": "Shield Bash", "exp_needed": 1000,
        "description": "A determined warrior with unwavering loyalty.",
        "image": "https://files.catbox.moe/2l5fw0.jpg"
    },
    "Kishibe": {
        "health": 90, "attack": 70, "special_ability": "Demon Slayer", "exp_needed": 1000,
        "description": "A battle-hardened veteran feared by devils.",
        "image": "https://files.catbox.moe/xg6bdl.jpg"
    }
}

# User Data (Temporary, Replace with Database Later)
user_data = {}
daily_claims = {}

# /start Command (Only in DM)
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != "private":
        bot.send_message(message.chat.id, "❌ Please start the bot in DM.")
        return

    user_id = message.chat.id
    user_data[user_id] = {"character": None, "gems": 0, "yens": 0, "exp": 0, "level": 1}

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🎭 Choose Character", callback_data="choose_char"))

    start_msg = """
🔥 *Welcome to the Chainsaw Man Game!* 🔥
━━━━━━━━━━━━━
💀 Choose your character and embark on a thrilling adventure! 💀
⚔️ Fight devils, earn rewards, and become the strongest hunter! ⚔️
━━━━━━━━━━━━━
"""

    bot.send_photo(user_id, "https://files.catbox.moe/qeqy19.jpg", caption=start_msg, parse_mode="Markdown", reply_markup=keyboard)

# /choose_char (Only in DM)
@bot.callback_query_handler(func=lambda call: call.data == "choose_char")
def choose_char(call):
    if call.message.chat.type != "private":
        bot.answer_callback_query(call.id, "❌ Choose your character in DM!")
        return

    user_id = call.from_user.id
    keyboard = InlineKeyboardMarkup()
    for char_name in characters.keys():
        keyboard.add(InlineKeyboardButton(char_name, callback_data=char_name))

    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "🎭 *Choose your character:*", reply_markup=keyboard, parse_mode="Markdown")

# Character Selection
@bot.callback_query_handler(func=lambda call: call.data in characters)
def handle_char_selection(call):
    user_id = call.from_user.id
    character_name = call.data
    user_data[user_id]["character"] = character_name

    char = characters[character_name]
    stats = f"""
🩸 _{character_name}_ 🩸
━━━━━━━━━━━━━
❤️ Health: 〘 {char['health']} HP 〙
⚔️ Attack: 〘 {char['attack']} 〙
👻 Special Ability: _{char['special_ability']}_ 
🔺 EXP Needed: 〘 {char['exp_needed']} 〙
━━━━━━━━━━━━━
💀 *{char['description']}*
"""

    bot.answer_callback_query(call.id)
    bot.send_photo(user_id, char["image"], caption=stats, parse_mode="Markdown")

# /daily Command (Only in Group, Once Every 24 Hours)
@bot.message_handler(commands=['daily'])
def daily(message):
    if message.chat.type != "supergroup" and message.chat.id != OFFICIAL_GROUP_ID:
        bot.send_message(message.chat.id, "❌ You can only claim daily rewards in the official group.")
        return

    user_id = message.from_user.id
    current_time = time.time()

    # Check if user has already claimed within the last 24 hours
    if user_id in daily_claims:
        last_claim = daily_claims[user_id]
        time_passed = current_time - last_claim

        if time_passed < 86400:  # 24 hours = 86400 seconds
            remaining_time = int((86400 - time_passed) / 3600)
            bot.send_message(message.chat.id, f"⏳ You already claimed your daily reward! Try again in {remaining_time} hours.")
            return

    # Give rewards
    if user_id not in user_data:
        user_data[user_id] = {"character": None, "gems": 0, "yens": 0, "exp": 0, "level": 1}

    user_data[user_id]["yens"] += 150
    user_data[user_id]["gems"] += 100
    daily_claims[user_id] = current_time

    bot.send_message(message.chat.id, "🎁 You received *150 Yens* and *100 Gems*! Come back tomorrow for more.", parse_mode="Markdown")

# /balance Command with Exit Button
@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.chat.id
    if user_id not in user_data:
        bot.send_message(user_id, "❌ You haven't started the game yet. Use /start.")
        return

    user = user_data[user_id]

    balance_msg = f"""
╔════════════════════════════╗
║     💰 HUNTER'S TREASURY 💰     ║
╠════════════════════════════╣
║ 🎭 *Hunter Profile*             ║
║ 📌 ID   │ `{user_id}`           ║
║ 📝 Name │ `{message.from_user.first_name}`   ║
╠════════════════════════════╣
║ 💴 *Wealth*                      ║
║ 💰 Yens   │ `{user['yens']}`    ║
║ 💎 Gems  │ `{user['gems']}`     ║
╠════════════════════════════╣
║ ⚔️ *Combat Stats*               ║
║ 📊 Level │ `{user['level']}`    ║
║ 🔺 EXP   │ `{user['exp']}` / 1000  ║
╚════════════════════════════╝
"""

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("❌ Exit", callback_data="exit_balance"))

    # Check if the message is from a group or DM
    if message.chat.type in ['group', 'supergroup']:
        bot.send_message(message.chat.id, balance_msg, parse_mode="Markdown", reply_markup=keyboard)
    else:
        bot.send_message(user_id, balance_msg, parse_mode="Markdown", reply_markup=keyboard)

# Exit Balance Message
@bot.callback_query_handler(func=lambda call: call.data == "exit_balance")
def exit_balance(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "✅ Balance closed.")

# Start Bot
@bot.message_handler(commands=['stats'])
def stats(message):
    args = message.text.split(maxsplit=1)  # Split command and argument

    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ Usage: `/stats <character_name>`", parse_mode="Markdown")
        return

    character_name = args[1].strip()

    # Exact match check
    if character_name in characters:
        char = characters[character_name]

        stats_msg = f"""
🩸 *{character_name}* 🩸
━━━━━━━━━━━━━
❤️ Health: 〘 {char['health']} HP 〙
⚔️ Attack: 〘 {char['attack']} 〙
👻 Special Ability: _{char['special_ability']}_ 
🔺 EXP Needed: 〘 {char['exp_needed']} 〙
━━━━━━━━━━━━━
💀 *{char['description']}*
"""

        bot.send_photo(message.chat.id, char["image"], caption=stats_msg, parse_mode="Markdown")

    # Spelling mistake check
    elif any(name.lower() == character_name.lower() for name in characters.keys()):
        bot.send_message(message.chat.id, "⚠️ *Spelling error!* Check the name and try again.", parse_mode="Markdown")

    else:
        bot.send_message(message.chat.id, "❌ *Error!* Character not found.", parse_mode="Markdown")



# /mycharacters Command - Shows user's owned characters with count (Works in both Groups and DMs)
@bot.message_handler(commands=['mycharacters'])
def mycharacters(message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"owned_characters": []}  # Ensure data structure exists

    owned_characters = user_data[user_id].get("owned_characters", [])

    if not owned_characters:
        bot.send_message(message.chat.id, "❌ You don't own any characters yet.\nStart your journey and collect powerful hunters!")
        return

    random.shuffle(owned_characters)  # Shuffle characters only

    # Assign ordered numbers (1, 2, 3...)
    char_list = "\n".join([f"{i + 1}️⃣ {char}" for i, char in enumerate(owned_characters)])
    
    response = f"""
📜 *Your Character Collection* 📜
━━━━━━━━━━━━━━━━━━━
🔢 *Total Characters:* {len(owned_characters)}
{char_list}
━━━━━━━━━━━━━━━━━━━
"""

    bot.send_message(message.chat.id, response, parse_mode="Markdown")
#start the bot
bot.polling() 
