import telebot
import random
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Token (Replace with your own token)
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

# /start Command (Works only in DM)
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type != "private":
        bot.send_message(message.chat.id, "❌ Please start the bot in DM.")
        return

    user_id = message.chat.id
    user_data[user_id] = {"character": None, "gems": 0, "yens": 0, "exp": 0, "level": 1, "owned_characters": []}

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

# /choose_char Command
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
    user_data[user_id]["owned_characters"].append(character_name)

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

# /daily Command
@bot.message_handler(commands=['daily'])
def daily(message):
    if message.chat.id != OFFICIAL_GROUP_ID:
        bot.send_message(message.chat.id, "❌ You can only claim daily rewards in the official group.")
        return

    user_id = message.from_user.id
    current_time = time.time()

    if user_id in daily_claims and current_time - daily_claims[user_id] < 86400:
        remaining_time = int((86400 - (current_time - daily_claims[user_id])) / 3600)
        bot.send_message(message.chat.id, f"⏳ You already claimed your daily reward! Try again in {remaining_time} hours.")
        return

    if user_id not in user_data:
        user_data[user_id] = {"character": None, "gems": 0, "yens": 0, "exp": 0, "level": 1, "owned_characters": []}

    user_data[user_id]["yens"] += 150
    user_data[user_id]["gems"] += 100
    daily_claims[user_id] = current_time

    bot.send_message(message.chat.id, "🎁 You received *150 Yens* and *100 Gems*! Come back tomorrow for more.", parse_mode="Markdown")

# /balance Command
@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        bot.send_message(message.chat.id, "❌ You haven't started the game yet. Use /start.")
        return

    user = user_data[user_id]
    balance_msg = f"""
╔════════════════════════════╗
║     💰 HUNTER'S TREASURY 💰     ║
╠════════════════════════════╣
║ 🎭 *Hunter Profile*             ║
║ 📌 ID   │ `{user_id}`           ║
║ 📝 Name │ `{message.from_user.first_name}`   
╠════════════════════════════╣
║ 💴 *Wealth*                      
║ 💰 Yens   │ `{user['yens']}`    
║ 💎 Gems   │ `{user['gems']}`     
╠════════════════════════════╣
║ ⚔️ *Combat Stats*               
║ 📊 Level │ `{user['level']}`    
║ 🔺 EXP    │ `{user['exp']}` / 1000  
╚════════════════════════════╝
"""

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("❌ Exit", callback_data="exit_balance"))
    bot.send_message(message.chat.id, balance_msg, parse_mode="Markdown", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "exit_balance")
def exit_balance(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "✅ Balance closed.")

# /mycharacters Command
@bot.message_handler(commands=['mycharacters'])
def mycharacters(message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"owned_characters": []}

    owned_characters = user_data[user_id].get("owned_characters", [])

    if not owned_characters:
        bot.send_message(message.chat.id, "❌ You don't own any characters yet.\nStart your journey and collect powerful hunters!")
        return

    random.shuffle(owned_characters)
    char_list = "\n".join([f"{i + 1}️⃣ {char}" for i, char in enumerate(owned_characters)])

    response = f"""
📜 *Your Character Collection* 📜
━━━━━━━━━━━━━━━━━━━
🔢 *Total Characters:* {len(owned_characters)}
{char_list}
━━━━━━━━━━━━━━━━━━━
"""

    bot.send_message(message.chat.id, response, parse_mode="Markdown")
# /stats Command (Case-Insensitive)
@bot.message_handler(commands=['stats'])
def stats(message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ Please provide a character name. Example: `/stats Himeno`", parse_mode="Markdown")
        return

    character_name = args[1].strip().lower()  # Convert input to lowercase
    matched_character = None

    # Check if the input matches any character (case-insensitive)
    for char_name in characters.keys():
        if char_name.lower() == character_name:
            matched_character = char_name
            break

    if not matched_character:
        bot.send_message(message.chat.id, "❌ Character not found! Check the spelling and try again.", parse_mode="Markdown")
        return

    char = characters[matched_character]
    stats_message = f"""
🩸 _{matched_character}_ 🩸
━━━━━━━━━━━━━
❤️ Health: 〘 {char['health']} HP 〙
⚔️ Attack: 〘 {char['attack']} 〙
👻 Special Ability: _{char['special_ability']}_ 
🔺 EXP Needed: 〘 {char['exp_needed']} 〙
━━━━━━━━━━━━━
💀 *{char['description']}*
"""

    bot.send_photo(message.chat.id, char["image"], caption=stats_message, parse_mode="Markdown")
# Start the bot
bot.polling()
