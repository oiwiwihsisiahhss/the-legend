import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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


import sqlite3

def create_connection():
    return sqlite3.connect('chainsaw.db')

def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Create user_team_selection table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_team_selection (
            user_id INTEGER PRIMARY KEY,
            current_team INTEGER DEFAULT 1
        );
    ''')

    # Create character_base_stats table
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS character_base_stats (
         character_id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         level INTEGER DEFAULT 1,
         exp INTEGER NOT NULL DEFAULT 0,
         required_exp INTEGER NOT NULL,
         devil_contract TEXT NOT NULL,
         special_ability TEXT NOT NULL,
         attack INTEGER NOT NULL,
         defense INTEGER NOT NULL,
         speed INTEGER NOT NULL,
         precision INTEGER NOT NULL,
         instinct INTEGER NOT NULL,
         required_souls INTEGER NOT NULL DEFAULT 50,
         current_souls INTEGER NOT NULL DEFAULT 0,
         description TEXT NOT NULL,
         image_link TEXT NOT NULL,
         move_1 TEXT NOT NULL,
         move_1_unlock_level INTEGER DEFAULT 1,
         move_2 TEXT NOT NULL,
         move_2_unlock_level INTEGER DEFAULT 25,
         move_3 TEXT NOT NULL,
         move_3_unlock_level INTEGER DEFAULT 50,
         special_ability_unlock_level INTEGER DEFAULT 50
       )
    ''')

    # Insert default characters
    cursor.executemany('''
        INSERT OR IGNORE INTO character_base_stats 
        (name, required_exp, attack, defense, speed, precision, instinct, description, special_ability, devil_contract, image_link, required_souls, current_souls, move_1, move_2, move_3) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        (
            "Hirokazu Arai", 10000, 75, 65, 73, 70, 70,
            "A kind-hearted but determined devil hunter, Hirokazu values loyalty over strength. His mysterious contract shields him from death once but leaves him defenseless after.",
            "Fox Bite", "Fox Devil", "https://files.catbox.moe/56udfe.jpg",
            50, 0, "Quick Slash", "Defensive Stance", "Fox's Fury"
        ),
        (
            "Akane Sawatari", 15000, 75, 65, 72, 72, 68,
            "A ruthless and calculating former Yakuza, Akane wields the power of the Snake Devil to execute enemies instantly. Cold and efficient, she manipulates others to achieve her goals.",
            "Serpent’s Execution", "Snake Devil", "https://files.catbox.moe/tc02h0.jpg",
            50, 0, "Snake Strike", "Venomous Coil", "Serpent's Wrath"
        ),
        (
            "Kobeni Higashiyama", 25000, 74, 68, 74, 68, 72,
            "Timid yet incredibly fast, Kobeni survives against all odds. Though she hates fighting, her instincts and agility make her nearly untouchable in combat.",
            "Survivor’s Instinct", "Unknown", "https://files.catbox.moe/ka15hs.jpg",
            50, 0, "Agile Dash", "Evasive Maneuver", "Instinctive Strike"
        )
    ])

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

    # Create user_characters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_characters (
            user_id INTEGER NOT NULL,
            character_id INTEGER NOT NULL,
            level INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES user_data(user_id) ON DELETE CASCADE,
            FOREIGN KEY (character_id) REFERENCES character_base_stats(character_id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, character_id)
        )
    ''')

    # Create teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            user_id INTEGER,
            team_number INTEGER,
            slot1 TEXT,
            slot2 TEXT,
            slot3 TEXT,
            PRIMARY KEY (user_id, team_number)
        )
    ''')

    # Final commit and close
   # conn.commit()
   # conn.close()
        

    # Already created earlier but added again — optional:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_team_selection (
            user_id INTEGER PRIMARY KEY,
            current_team INTEGER DEFAULT 1
        )
    ''')

    # Commit and close
    conn.commit()
    conn.close()

# Sample data function for testing (only if no data)
#def initialize_sample_team(user_id):
    #for i in range(1, 6):
       # cursor.execute('''
          #  INSERT OR IGNORE INTO teams (user_id, team_number, slot1, slot2, slot3)
      #      VALUES (?, ?, ?, ?, ?)
    #    ''', (user_id, i, 'Character A', 'Character B', 'Character C'))
#    conn.commit()

#import sqlite3

# Establishing database connection
def get_connection():
    return sqlite3.connect('chainsaw.db', check_same_thread=False)

# Function to get user team (slot1, slot2, slot3)
def get_user_team(user_id, team_number=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT slot1, slot2, slot3 FROM teams
        WHERE user_id = ? AND team_number = ?
    ''', (user_id, team_number))
    row = cursor.fetchone()
    conn.close()
    if row and any(row):
        return [char if char else "Empty" for char in row]
    return ["Empty", "Empty", "Empty"]

# Function to set the user's main team
#def set_main_team(user_id, team_number):
def set_main_team(user_id, team_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_team_selection (user_id, current_team)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET current_team = excluded.current_team
    ''', (user_id, team_number))
    conn.commit()
    conn.close()

# Function to get the user's main team
def get_main_team(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT current_team FROM user_team_selection WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 1  # Defaults to team 1 
def set_user_team(user_id, team_number, slot1, slot2, slot3):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO teams (user_id, team_number, slot1, slot2, slot3)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, team_number)
        DO UPDATE SET slot1 = excluded.slot1, slot2 = excluded.slot2, slot3 = excluded.slot3
    ''', (user_id, team_number, slot1, slot2, slot3))

    conn.commit()
    conn.close()   

    
 
@bot.message_handler(commands=['myteam'])
def my_team(message):
    user_id = message.from_user.id

    # Get the user's last selected team
    selected_team_number = get_main_team(user_id)
    
    # Get the team details based on the selected team number
    team = get_user_team(user_id, team_number=selected_team_number)

    # Generate team display text
    team_text = f"✨<b>Your Current Team (Team {selected_team_number})</b> ✨\n"
    team_text += "━━━━━━━━━━━━━━━\n"
    for i, char in enumerate(team, start=1):
        team_text += f"<b>{i}\uFE0F\u20E3 {char}</b>\n"
    team_text += "━━━━━━━━━━━━━━━"

    # Inline keyboard for team selection
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Team 1⃣", callback_data="team1"),
        types.InlineKeyboardButton("Team 2⃣", callback_data="team2"),
    )
    markup.add(
        types.InlineKeyboardButton("Team 3⃣", callback_data="team3"),
        types.InlineKeyboardButton("Team 4⃣", callback_data="team4"),
    )
    markup.add(types.InlineKeyboardButton("Team 5⃣", callback_data="team5"))

    # If the chat is private, allow editing the team
    if message.chat.type == 'private':
        markup.add(types.InlineKeyboardButton("Edit Team📝", callback_data="edit_team"))
    
    # Close button (user-specific callback_data)
    close_button = types.InlineKeyboardButton("Close ❌", callback_data=f"close_{user_id}")
    markup.add(close_button)

    # Send the message with the team info and the inline keyboard
    bot.send_message(
        message.chat.id,
        team_text,
        reply_markup=markup,
        reply_to_message_id=message.message_id,
        parse_mode="HTML"
    )
import logging

@bot.callback_query_handler(func=lambda call: call.data.startswith("close_"))
def handle_close_callback(call):
    user_id = call.from_user.id
    target_id = int(call.data.split("_")[1])

    if user_id != target_id:
        bot.answer_callback_query(call.id, "This button isn't for you!", show_alert=True)
        return

    # Save to DB (if needed)
    conn = create_connection()
    cursor = conn.cursor()
    # Example: cursor.execute("UPDATE teams SET locked = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    # Respond with message
    success_message = (
        "<b>✅ Team Setup Successfully Closed!</b>\n\n"
        "Your team configuration has been saved and is now closed."
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=success_message,
        parse_mode="HTML"
    )

    bot.answer_callback_query(call.id, "Your team setup has been successfully closed.", show_alert=True)


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


@bot.callback_query_handler(func=lambda call: call.data == "choose_char")
def show_character_options(call):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Hirokazu Arai", callback_data="select_char_1"),
        InlineKeyboardButton("Akane Sawatari", callback_data="select_char_2"),
        InlineKeyboardButton("Kobeni Higashiyama", callback_data="select_char_3")
    )
    bot.send_message(
        chat_id=call.message.chat.id,
        text="Choose your character:",
        reply_markup=keyboard
    )
@bot.callback_query_handler(func=lambda call: call.data.startswith("select_char_"))
def handle_character_selection(call):
    user_id = call.from_user.id
    character_id = int(call.data.split("_")[-1])

    # Check if user has already selected
    cursor.execute("SELECT 1 FROM user_characters WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        bot.answer_callback_query(call.id, "You have already chosen a character!")
        return

    # Insert into DB
    cursor.execute("INSERT INTO user_characters (user_id, character_id) VALUES (?, ?)", (user_id, character_id))
    conn.commit()

    # Fetch character stats
    cursor.execute("SELECT name, attack, defense, speed, special_ability FROM character_base_stats WHERE character_id = ?", (character_id,))
    char = cursor.fetchone()

    if char:
        name, atk, df, spd, ability = char
        # Delete the previous keyboard message (optional)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"**{name} Selected!**\n\nAttack: {atk}\nDefense: {df}\nSpeed: {spd}\nSpecial Ability: {ability}",
            parse_mode="Markdown"
        )   
@bot.message_handler(commands=['myhunters'])        
def show_user_characters(message):
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    user_id = message.from_user.id
    cursor.execute('''
        SELECT cb.name, uc.level
        FROM user_characters uc
        JOIN character_base_stats cb ON uc.character_id = cb.character_id
        WHERE uc.user_id = ?
    ''', (user_id,))
    
    characters = cursor.fetchall()
    conn.close()

    if not characters:
        bot.send_message(message.chat.id, "❌ You don't have any hunters yet.")
    else:
        response = "🧾 *<b>Your Hunters Collection</b>:*\n━━━━━━━━━━━━━━\n"
        for i, (name, level) in enumerate(characters, start=1):
            response += f"*{i}. {name}*  —  `Level {level}`\n"
        response += "━━━━━━━━━━━━━━"
        bot.send_message(message.chat.id, response, parse_mode="HTML", reply_to_message_id=message.message_id)        
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
@bot.message_handler(commands=['c_add'])
def add_character(message):
    if message.from_user.id != 6306216999:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Please reply to the user you want to add the character to.\nUsage: `/c_add <character_name>`", parse_mode="Markdown")
        return

    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Usage: /c_add <character_name>")
            return

        character_name = args[1].strip().lower()
        user = message.reply_to_message.from_user
        user_id = user.id
        user_name = user.first_name
        user_link = f'<a href="tg://user?id={user_id}">{user_name}</a>'

        conn = sqlite3.connect("chainsaw.db")
        cursor = conn.cursor()

        # Get character_id from name
        cursor.execute("SELECT character_id, name FROM character_base_stats WHERE LOWER(name) = ?", (character_name,))
        character = cursor.fetchone()

        if not character:
            bot.reply_to(message, "❌ Character not found. Please check the name and try again.")
            conn.close()
            return

        character_id, char_name = character

        # Insert character into user's collection
        cursor.execute('''
            INSERT OR IGNORE INTO user_characters (user_id, character_id, level)
            VALUES (?, ?, 1)
        ''', (user_id, character_id))
        conn.commit()
        conn.close()

        bot.send_message(
            message.chat.id,
            f"✅ <b>{char_name}</b> has been added to {user_link}'s hunter list.",
            parse_mode="HTML"
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}") 
@bot.message_handler(commands=['stats'])
def stats(message):
    args = message.text.split(' ', 1)
    if len(args) == 1:
        return bot.reply_to(message, "❌ Please provide a character name.")
    
    name_input = args[1].strip().lower()
    user_id = message.from_user.id

    conn = sqlite3.connect('chainsaw.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT cb.character_id, cb.name, cb.description, cb.attack, cb.defense, cb.speed, cb.precision,
               cb.instinct, cb.image_link, cb.exp, cb.required_exp, uc.level
        FROM user_characters uc
        JOIN character_base_stats cb ON uc.character_id = cb.character_id
        WHERE uc.user_id = ? AND LOWER(cb.name) LIKE ?
    ''', (user_id, f"{name_input}%"))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return bot.reply_to(message, "❌ No character found with that name.")

    (char_id, name, desc, atk, defense, spd, prec, inst, img, exp, req_exp, lvl) = result
    progress = int((exp / req_exp) * 10)
    bar = '█' * progress + '░' * (10 - progress)

    caption = f"""<b>🧾 Character Info</b>
━━━━━━━━━━━━━━
<b>📛 Name:</b> {name}
<b>⭐ Level:</b> {lvl}
<b>🧾 Description:</b> {desc}

<b>🔥 EXP Progress</b>
━━━━━━━━━━━━━━
<b>{exp} / {req_exp}</b>
<code>[{bar}]</code>

<b>⚔️ Battle Stats</b>
━━━━━━━━━━━━━━
<b>⚔️ Attack:</b> {atk}
<b>🛡 Defense:</b> {defense}
<b>⚡ Speed:</b> {spd}
<b>🎯 Precision:</b> {prec}
<b>✨ Instinct:</b> {inst}
━━━━━━━━━━━━━━"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌀Abilities", callback_data=f"abilities:{char_id}"))
    bot.send_photo(message.chat.id, img, caption=caption, parse_mode="HTML", reply_to_message_id=message.message_id, reply_markup=markup) 
@bot.callback_query_handler(func=lambda call: call.data.startswith('abilities:'))
def show_abilities(call):
    char_id = call.data.split(':')[1]
    user_id = call.from_user.id

    conn = sqlite3.connect('chainsaw.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT cb.name, cb.move_1, cb.move_1_unlock_level,
               cb.move_2, cb.move_2_unlock_level,
               cb.move_3, cb.move_3_unlock_level,
               cb.special_ability, cb.special_ability_unlock_level,
               uc.level
        FROM user_characters uc
        JOIN character_base_stats cb ON uc.character_id = cb.character_id
        WHERE uc.user_id = ? AND cb.character_id = ?
    ''', (user_id, char_id))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return bot.answer_callback_query(call.id, "❌ Character not found.")

    (name, m1, m1_lvl, m2, m2_lvl, m3, m3_lvl, special, special_lvl, lvl) = result

    def lock_check(lvl_required):
        return '✅' if lvl >= lvl_required else '🔐'

    text = f"""<b>🌀 Abilities - {name}</b>
━━━━━━━━━━━━━━
<b>{lock_check(m1_lvl)}</b> <b>Move 1:</b> {m1} <i>(Lv. {m1_lvl})</i>
<b>{lock_check(m2_lvl)}</b> <b>Move 2:</b> {m2} <i>(Lv. {m2_lvl})</i>
<b>{lock_check(m3_lvl)}</b> <b>Move 3:</b> {m3} <i>(Lv. {m3_lvl})</i>
<b>{lock_check(special_lvl)}</b> <b>Special:</b> {special} <i>(Lv. {special_lvl})</i>
━━━━━━━━━━━━━━"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⚜️Stats", callback_data=f"statsback:{char_id}"))
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                             caption=text, parse_mode="HTML", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data.startswith('statsback:'))
def return_to_stats(call):
    char_id = call.data.split(':')[1]
    user_id = call.from_user.id

    conn = sqlite3.connect('chainsaw.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name FROM character_base_stats WHERE character_id = ?
    ''', (char_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return bot.answer_callback_query(call.id, "❌ Character not found.")

    name = result[0].split()[0]  # Gets first name only (e.g., "Himeno" from "Himeno Ghost")

    # Construct the message text for the stats function
    fake_message = call.message
    fake_message.text = f"/stats {name}"  # Simulate a message text with the correct command
    fake_message.from_user = call.from_user  # Add the user from the callback

    # Now, instead of directly calling stats(fake_message), we can send the stats text and edit the message.
    conn = sqlite3.connect('chainsaw.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT cb.character_id, cb.name, cb.description, cb.attack, cb.defense, cb.speed, cb.precision,
               cb.instinct, cb.image_link, cb.exp, cb.required_exp, uc.level
        FROM user_characters uc
        JOIN character_base_stats cb ON uc.character_id = cb.character_id
        WHERE uc.user_id = ? AND LOWER(cb.name) LIKE ?
    ''', (user_id, f"{name.lower()}%"))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="❌ No character found with that name.")

    (char_id, name, desc, atk, defense, spd, prec, inst, img, exp, req_exp, lvl) = result
    progress = int((exp / req_exp) * 10)
    bar = '█' * progress + '░' * (10 - progress)

    caption = f"""<b>🧾 Character Info</b>
━━━━━━━━━━━━━━
<b>📛 Name:</b> {name}
<b>⭐ Level:</b> {lvl}
<b>🧾 Description:</b> {desc}

<b>🔥 EXP Progress</b>
━━━━━━━━━━━━━━
<b>{exp} / {req_exp}</b>
<code>[{bar}]</code>

<b>⚔️ Battle Stats</b>
━━━━━━━━━━━━━━
<b>⚔️ Attack:</b> {atk}
<b>🛡 Defense:</b> {defense}
<b>⚡ Speed:</b> {spd}
<b>🎯 Precision:</b> {prec}
<b>✨ Instinct:</b> {inst}
━━━━━━━━━━━━━━"""

    # Adding the "Abilities" button back into the keyboard
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Abilities", callback_data=f"abilities:{char_id}"))

    # Editing the existing message with the stats information and adding the "Abilities" button
    bot.edit_message_caption(chat_id=call.message.chat.id,
                             message_id=call.message.message_id,
                             caption=caption,
                             parse_mode="HTML",
                             reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("team"))
def handle_team_selection(call):
    user_id = call.from_user.id
    team_number = int(call.data[-1])  # Extract team number from "team1" to "team5"

    current_main = get_main_team(user_id)
    if team_number == current_main:
        bot.answer_callback_query(call.id, "⚠️ You have already set this team as your main team.", show_alert=True)
        return
    else:
        set_main_team(user_id, team_number)

    team = get_user_team(user_id, team_number)

    team_text = f"<b>✨ Your Current Team (Team {team_number})</b> ✨\n"
    team_text += "━━━━━━━━━━━━━━━\n"
    for i, char in enumerate(team, start=1):
        team_text += f"<b>{i}\uFE0F\u20E3 {char if char else 'Empty'}</b>\n"
    team_text += "━━━━━━━━━━━━━━━"

    markup = types.InlineKeyboardMarkup(row_width=2)
    row1 = [
        types.InlineKeyboardButton("Team 1⃣", callback_data="team1"),
        types.InlineKeyboardButton("Team 2⃣", callback_data="team2"),
    ]
    row2 = [
        types.InlineKeyboardButton("Team 3⃣", callback_data="team3"),
        types.InlineKeyboardButton("Team 4⃣", callback_data="team4"),
    ]
    row3 = [types.InlineKeyboardButton("Team 5⃣", callback_data="team5")]
    markup.add(*row1)
    markup.add(*row2)
    markup.add(*row3)

    if call.message.chat.type == 'private':
        row4 = [types.InlineKeyboardButton("Edit Team📝", callback_data="edit_team")]
        markup.add(*row4)

    close_button = types.InlineKeyboardButton("Close ❌", callback_data=f"close_{user_id}")
    markup.add(close_button)

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=team_text,
        reply_markup=markup,
        parse_mode="HTML"
    )
@bot.callback_query_handler(func=lambda call: call.data == "edit_team")
def handle_edit_team_callback(call):
    user_id = call.from_user.id

    # Adjusted button layout
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("➕ Add", callback_data="edit_add"),
        types.InlineKeyboardButton("🚫 Remove", callback_data="edit_remove")
    )
    markup.add(
        types.InlineKeyboardButton("🔄 Swap", callback_data="edit_swap"),
        types.InlineKeyboardButton("↪️ Back", callback_data="edit_back")
    )
    markup.add(
        types.InlineKeyboardButton("❌ Close", callback_data=f"close_{user_id}")
    )

    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )

    bot.answer_callback_query(call.id, "Edit options loaded.")    
@bot.callback_query_handler(func=lambda call: call.data == "edit_back")
def handle_edit_back(call):
    user_id = call.from_user.id

    # Same logic from the /myteam command
    selected_team_number = get_main_team(user_id)
    team = get_user_team(user_id, team_number=selected_team_number)

    team_text = f"✨<b>Your Current Team (Team {selected_team_number})</b> ✨\n"
    team_text += "━━━━━━━━━━━━━━━\n"
    for i, char in enumerate(team, start=1):
        team_text += f"<b>{i}\uFE0F\u20E3 {char}</b>\n"
    team_text += "━━━━━━━━━━━━━━━"

    # Rebuild the team selection buttons
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Team 1⃣", callback_data="team1"),
        types.InlineKeyboardButton("Team 2⃣", callback_data="team2"),
    )
    markup.add(
        types.InlineKeyboardButton("Team 3⃣", callback_data="team3"),
        types.InlineKeyboardButton("Team 4⃣", callback_data="team4"),
    )
    markup.add(types.InlineKeyboardButton("Team 5⃣", callback_data="team5"))

    if call.message.chat.type == 'private':
        markup.add(types.InlineKeyboardButton("Edit Team📝", callback_data="edit_team"))
    
    markup.add(types.InlineKeyboardButton("Close ❌", callback_data=f"close_{user_id}"))

    # Edit the current message with updated content
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=team_text,
        reply_markup=markup,
        parse_mode="HTML"
    )

    bot.answer_callback_query(call.id, "Back to team view.")   
 # Global variable to keep track of page numbers

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

def generate_add_team_interface(user_id, team_number, page=1):
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT cbs.name 
        FROM user_characters uc
        JOIN character_base_stats cbs ON uc.name = cbs.name
        WHERE uc.user_id = ?
    ''', (user_id,))
    all_chars = sorted([row[0] for row in cursor.fetchall()])

    cursor.execute('''
        SELECT slot1, slot2, slot3
        FROM teams
        WHERE user_id = ? AND team_number = ?
    ''', (user_id, team_number))
    team = cursor.fetchone() or ("Empty", "Empty", "Empty")
    selected_chars = set(filter(lambda x: x and x != "Empty", team))

    per_page = 6
    total_pages = max(1, (len(all_chars) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    visible_chars = all_chars[start:end]

    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []

    for name in visible_chars:
        mark = " ☑" if name in selected_chars else ""
        safe_name = name[:30]
        callback = f"selectchar:{safe_name}:{team_number}:{page}"
        buttons.append(InlineKeyboardButton(text=name + mark, callback_data=callback[:64]))

    for i in range(0, len(buttons), 2):
        keyboard.row(*buttons[i:i+2])

    keyboard.row(
        InlineKeyboardButton("⏪", callback_data=f"edit_add:{team_number}:{max(1, page - 1)}"),
        InlineKeyboardButton(f"[{page}/{total_pages}]", callback_data="noop"),
        InlineKeyboardButton("⏩", callback_data=f"edit_add:{team_number}:{min(total_pages, page + 1)}")
    )

    keyboard.row(InlineKeyboardButton("💬 Save", callback_data=f"save_team:{team_number}"))
    keyboard.row(InlineKeyboardButton("Back", callback_data="edit_back"))
    keyboard.row(InlineKeyboardButton("Close", callback_data=f"close_{user_id}"))

    conn.close()
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("edit_add"))
def handle_edit_add(call):
    try:
        _, team_number, page = call.data.split(":")
        user_id = call.from_user.id
        team_number = int(team_number)
        page = int(page)

        conn = sqlite3.connect("chainsaw.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT slot1, slot2, slot3 
            FROM teams 
            WHERE user_id = ? AND team_number = ?
        ''', (user_id, team_number))
        team = cursor.fetchone() or ("Empty", "Empty", "Empty")
        conn.close()

        def format_slot(slot, index):
            return f"{index}️⃣ {slot if slot and slot != 'Empty' else 'Empty'}"

        team_message = (
            f"✨ Your Current Team (Team {team_number}) ✨\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{format_slot(team[0], 1)}\n"
            f"{format_slot(team[1], 2)}\n"
            f"{format_slot(team[2], 3)}\n"
            f"━━━━━━━━━━━━━━━"
        )

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=team_message,
            reply_markup=generate_add_team_interface(user_id, team_number, page)
        )
    except Exception as e:
        print(f"Error in handle_edit_add: {e}")
        bot.answer_callback_query(call.id, "An error occurred!")
bot.polling(none_stop=True)
