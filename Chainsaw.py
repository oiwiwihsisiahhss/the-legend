import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import random

TOKEN = "7215821191:AAH7YBa2FQi-0lfNHAnZMQtBAENTO1paw6A"
bot = telebot.TeleBot(TOKEN)

# Official Group ID (Replace if needed)
OFFICIAL_GROUP_ID = -1002369433935

# Store user data (Use SQLite for persistence in the future)
user_data = {}
daily_claims = {}

# Character Stats
character_stats = {
    "Himeno": {
        "Health": 85,
        "Attack": 60,
        "Defense": 70,
        "Special Ability": "Phantom Strike",
        "Level": 0,
        "EXP": "200 / 1000",
        "Description": "A relentless hunter who walks the line between the living and the dead.",
        "Image": "https://files.catbox.moe/i3vcf7.jpg"
    },
    "Hirokazu": {
        "Health": 75,
        "Attack": 65,
        "Defense": 60,
        "Special Ability": "Bullet Barrage",
        "Level": 0,
        "EXP": "150 / 1000",
        "Description": "A determined fighter with a sharp aim.",
        "Image": "https://files.catbox.moe/2l5fw0.jpg"
    },
    "Kishibe": {
        "Health": 90,
        "Attack": 80,
        "Defense": 75,
        "Special Ability": "Devil Slayer",
        "Level": 0,
        "EXP": "250 / 1000",
        "Description": "A veteran devil hunter feared by both devils and humans.",
        "Image": "https://files.catbox.moe/xg6bdl.jpg"
    }
}

# /start Command (Only in DM)
# /start Command (Only in DM)
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if message.chat.type != "private":
        bot.send_message(chat_id, f"❌ @{message.from_user.username}, use /start in DM.")
        return

    start_msg = """
🔥 *Welcome to the Chainsaw Man Game!* 🔥
━━━━━━━━━━━━━
💀 Choose your character and embark on a thrilling adventure! 💀
⚔️ Fight devils, earn rewards, and become the strongest hunter! ⚔️
━━━━━━━━━━━━━
"""

    if user_id not in user_data:
        user_data[user_id] = {"started": True, "character": None, "yens": 0, "gems": 0, "exp": 0, "level": 1, "owned_characters": []}

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🎭 Choose Character", callback_data="choose_char"))

        bot.send_photo(user_id, "https://files.catbox.moe/qeqy19.jpg", caption=start_msg, parse_mode="Markdown", reply_markup=keyboard)
    else:
        bot.send_message(user_id,
        "⚠ *You have already started the bot!* \n\n"
        "Welcome back, hunter! You’ve already embarked on your journey in the *Chainsaw Man Game*.\n"
        "Keep grinding, slaying devils, and becoming stronger!\n\n"
        "📌 *Stay connected with our community and never miss an update!*\n\n"
        "🔗 [Join our Group](https://t.me/chainsawman_main_gc) \n"
        "🔗 [Join Update Channel](https://t.me/chainsaw_man_update_channel)\n\n"
        "🔥 Keep hunting and prove your strength!",
        parse_mode="Markdown"
    )

# /choose_char Command
@bot.callback_query_handler(func=lambda call: call.data == "choose_char")
def choose_char(call):
    user_id = call.from_user.id

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Himeno", callback_data="Himeno"))
    keyboard.add(InlineKeyboardButton("Hirokazu", callback_data="Hirokazu"))
    keyboard.add(InlineKeyboardButton("Kishibe", callback_data="Kishibe"))

    bot.answer_callback_query(call.id)

    # **Remove inline keyboard after choosing character**
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

    bot.send_message(user_id, "🎭 *Choose your character:*", reply_markup=keyboard, parse_mode="Markdown")

# Character Selection & Stats Display
@bot.callback_query_handler(func=lambda call: call.data in character_stats)
def select_character(call):
    user_id = call.from_user.id
    chosen_character = call.data

    user_data[user_id]["character"] = chosen_character
    if chosen_character not in user_data[user_id]["owned_characters"]:
        user_data[user_id]["owned_characters"].append(chosen_character)

    char_info = character_stats[chosen_character]
    stats_msg = f"""
🎭 *You have chosen {chosen_character}!* 🎭
━━━━━━━━━━━━━
❤️ *Health:* {char_info["Health"]}
⚔️ *Attack:* {char_info["Attack"]}
🛡️ *Defense:* {char_info["Defense"]}
✨ *Special Ability:* {char_info["Special Ability"]}
🔰 *Level:* {char_info["Level"]}
📈 *EXP:* {char_info["EXP"]}
📖 *Description:* {char_info["Description"]}
━━━━━━━━━━━━━
"""

    bot.answer_callback_query(call.id)

    # **Remove inline keyboard after character selection**
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

    bot.send_photo(user_id, char_info["Image"], caption=stats_msg, parse_mode="Markdown")

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
        bot.send_message(message.chat.id, f"⏳ Already claimed! Try again in {remaining_time} hours.")
        return

    user_data[user_id]["yens"] += 150
    user_data[user_id]["gems"] += 100
    daily_claims[user_id] = current_time

    bot.send_message(message.chat.id, "🎁 You received *150 Yens* and *100 Gems*!", parse_mode="Markdown")
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

    # Add an Exit button
    markup = InlineKeyboardMarkup()
    exit_button = InlineKeyboardButton("❌ Exit", callback_data="exit_balance")
    markup.add(exit_button)

    bot.send_message(message.chat.id, balance_msg, parse_mode="Markdown", reply_markup=markup)


# Handle exit button click
@bot.callback_query_handler(func=lambda call: call.data == "exit_balance")
def exit_balance(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "✅ Balance closed successfully!")

@bot.message_handler(commands=['mycharacters'])
def mycharacters(message):
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {"owned_characters": []}

    owned_characters = user_data[user_id].get("owned_characters", [])

    if not owned_characters:
        bot.send_message(
            message.chat.id,
            "❌ *You don't own any characters yet.*\n"
            "Start your journey and collect powerful hunters!",
            parse_mode="Markdown"
        )
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
@bot.message_handler(commands=["stats"])
def stats_command(message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)  # Get command arguments

    # Check if user provided a character name
    if len(args) < 2:
        bot.reply_to(message, "❌ Please specify a character name! Example: `/stats Himeno`")
        return

    input_name = args[1].strip()  # Get the character name and remove spaces

    # Convert input to lowercase for matching
    matched_character = next((name for name in character_stats if name.lower() == input_name.lower()), None)

    if not matched_character:
        bot.reply_to(message, f"❌ Character '{input_name}' not found! Please check the spelling.")
        return

    # Check if the user owns the character
    if user_id not in user_data or matched_character not in user_data[user_id].get("owned_characters", []):
        bot.reply_to(message, f"❌ You don’t own '{matched_character}'!")
        return

    # Retrieve stats using the correct character name
    char_info = character_stats[matched_character]

    stats_msg = f"""
🎭 *Character Stats: {matched_character}* 🎭
━━━━━━━━━━━━━
❤️ *Health:* {char_info["Health"]}
⚔️ *Attack:* {char_info["Attack"]}
🛡️ *Defense:* {char_info["Defense"]}
✨ *Special Ability:* {char_info["Special Ability"]}
🔰 *Level:* {char_info["Level"]}
📈 *EXP:* {char_info["EXP"]} / 1000
📖 *Description:* {char_info["Description"]}
━━━━━━━━━━━━━
    """

    # Send character image along with stats
    if "Image" in char_info:  # Ensure an image exists for the character
        bot.send_photo(message.chat.id, char_info["Image"], caption=stats_msg, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, stats_msg, parse_mode="Markdown")
@bot.message_handler(commands=['add'])
def add_resources(message):
    user_id = message.from_user.id
    
    if user_id != 6306216999:  # Replace with your user ID (only you can use this)
        bot.reply_to(message, "You don't have permission to add resources.")
        return

    try:
        # Split the command into parts
        parts = message.text.split()
        
        # Check if the user provided the necessary arguments
        if len(parts) < 3:
            bot.reply_to(message, "Invalid command format. Please use '/add yens <amount>', '/add gems <amount>', or '/add char <character_name>'.")
            return

        # Handling the 'char' command
        if parts[1] == 'char':
            char_name = parts[2].capitalize()  # Ensure the character name is properly capitalized
            
            if char_name in character_stats:
                stats = character_stats[char_name]
                # Add character to the user's mycharacters list
                if user_id not in user_data:
                    user_data[user_id] = {'yens': 0, 'gems': 0, 'mycharacters': []}  # Initialize if not exist
                
                if char_name not in user_data[user_id]['mycharacters']:
                    user_data[user_id]['mycharacters'].append(char_name)
                    bot.reply_to(message, f"{char_name} has been added to your characters!\n"
                                          f"Health: {stats['Health']}\n"
                                          f"Attack: {stats['Attack']}\n"
                                          f"Defense: {stats['Defense']}\n"
                                          f"Special Ability: {stats['Special Ability']}\n"
                                          f"Level: {stats['Level']}\n"
                                          f"EXP: {stats['EXP']}\n"
                                          f"Description: {stats['Description']}\n\n"
                                          f"Image: {stats['Image']}")
                else:
                    bot.reply_to(message, f"You already have {char_name} in your characters.")
            else:
                bot.reply_to(message, f"Character '{char_name}' is not available. Please check the name and try again.")

        # Handling 'yens' command
        elif parts[1] == 'yens':
            try:
                amount = int(parts[2])  # Convert the input value to an integer
            except ValueError:
                bot.reply_to(message, "Invalid amount. Please provide a valid number for yens.")
                return

            if user_id not in user_data:
                user_data[user_id] = {'yens': 0, 'gems': 0, 'mycharacters': []}  # Initialize if not exist

            # Add or subtract the yens (positive or negative)
            user_data[user_id]['yens'] += amount
            
            if amount > 0:
                bot.reply_to(message, f"{amount} yens have been added to your account.")
            else:
                bot.reply_to(message, f"{-amount} yens have been deducted from your account.")

        # Handling 'gems' command
        elif parts[1] == 'gems':
            try:
                amount = int(parts[2])  # Convert the input value to an integer
            except ValueError:
                bot.reply_to(message, "Invalid amount. Please provide a valid number for gems.")
                return

            if user_id not in user_data:
                user_data[user_id] = {'yens': 0, 'gems': 0, 'mycharacters': []}  # Initialize if not exist

            # Add or subtract the gems (positive or negative)
            user_data[user_id]['gems'] += amount
            
            if amount > 0:
                bot.reply_to(message, f"{amount} gems have been added to your account.")
            else:
                bot.reply_to(message, f"{-amount} gems have been deducted from your account.")
        else:
            bot.reply_to(message, "Invalid command format. Please use '/add yens <amount>', '/add gems <amount>', or '/add char <character_name>'.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")
bot.polling()
