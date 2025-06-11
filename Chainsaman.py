import telebot
import random
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import time
import math
import sqlite3
from telebot import types
from datetime import datetime, timedelta

import html
# Temporary in-memory sel pgection before saving
temp_team_selection = {}
swap_selection = {}
temp_swaps = {}  # {user_id: {"team_number": 1, "first_slot": 0}}
# Initialize bot with your API key
API_KEY = '7215821191:AAEzFPwyx8FjlXMr2mpVTbYzpHoMbPsaCDc'
bot = telebot.TeleBot(API_KEY)


import sqlite3

def create_connection():
    return sqlite3.connect('chainsaw.db')

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    #cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devils (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            image TEXT NOT NULL
            
        )
    ''')
    cursor.executemany("""
        INSERT INTO devils (name, image) VALUES (?, ?)
""", [
    ("SEA CUCUMBER DEVIL", "https://files.catbox.moe/jss3ms.jpg"),
    ("LEECH DEVIL", "https://files.catbox.moe/z1cyi3.jpg"),
    ("BAT DEVIL", "https://files.catbox.moe/m1cr9k.jpg"),
    ("TOMATO DEVIL", "https://files.catbox.moe/gcg6bg.jpg"),
    ("MUSCLE DEVIL", "https://files.catbox.moe/sm9xad.jpg"),
    ("FISH DEVIL", "https://files.catbox.moe/d7an4c.jpg"),
])
    
    
    
    
    

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
        (character_id, name, required_exp, attack, defense, speed, precision, instinct, description, special_ability, devil_contract, image_link, required_souls, current_souls, move_1, move_2, move_3) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
        (
            1, "Hirokazu Arai", 10000, 75, 65, 73, 70, 70,
            "A kind-hearted but determined devil hunter, Hirokazu values loyalty over strength. His mysterious contract shields him from death once but leaves him defenseless after.",
            "Fox Bite", "Fox Devil", "https://files.catbox.moe/56udfe.jpg",
            50, 0, "Quick Slash", "Defensive Stance", "Fox's Fury"
        ),
        (
            2,"Akane Sawatari", 15000, 75, 65, 72, 72, 68,
            "A ruthless and calculating former Yakuza, Akane wields the power of the Snake Devil to execute enemies instantly. Cold and efficient, she manipulates others to achieve her goals.",
            "Serpent’s Execution", "Snake Devil", "https://files.catbox.moe/tc02h0.jpg",
            50, 0, "Snake Strike", "Venomous Coil", "Serpent's Wrath"
        ),
        (
            3,"Kobeni Higashiyama", 25000, 74, 68, 74, 68, 72,
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
def generate_team_stats_text(user_id, team_number):
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT slot1, slot2, slot3 FROM teams
        WHERE user_id = ? AND team_number = ?
    """, (user_id, team_number))
    slots = cursor.fetchone() or ("Empty", "Empty", "Empty")

    stats = {"attack": 0, "defense": 0, "speed": 0}
    count = 3  # Always divide by 3 since "Empty" counts as 0

    for char_name in slots:
        if char_name and char_name != "Empty":
            cursor.execute("""
                SELECT attack, defense, speed FROM character_base_stats
                WHERE name = ?
            """, (char_name,))
            row = cursor.fetchone()
            if row:
                stats["attack"] += row[0]
                stats["defense"] += row[1]
                stats["speed"] += row[2]
    
    conn.close()

    avg_attack = stats["attack"] // count
    avg_defense = stats["defense"] // count
    avg_speed = stats["speed"] // count

    def make_bar(value):
        filled = int(value / 10)
        empty = 10 - filled
        return "▓" * filled + "░" * empty

    return (
        "📊 Team Stats Overview:\n"
        f"⚔️ Atk: {avg_attack}  {make_bar(avg_attack)}\n"
        f"🛡 Def: {avg_defense}  {make_bar(avg_defense)}\n"
        f"⚡ Spd: {avg_speed}  {make_bar(avg_speed)}"
    )
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
def get_team_character_ids(user_id, team_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT slot1, slot2, slot3 FROM teams WHERE user_id = ? AND team_number = ?', (user_id, team_number))
    row = cursor.fetchone()
    conn.close()
    return list(row) if row else []
def get_main_team(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT current_team FROM user_team_selection WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return int(row[0]) if row else 1  # Ensures correct type
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

    selected_team_number = get_main_team(user_id)
    team = get_user_team(user_id, team_number=selected_team_number)

    # Team display text
    team_text = f"✨<b>Your Current Team (Team {selected_team_number})</b> ✨\n"
    team_text += "━━━━━━━━━━━━━━━"
    for char in team:
        team_text += f"\n✧ {char if char else 'Empty'}"
    team_text += "\n━━━━━━━━━━━━━━━"

    # Add stats overview
    team_text += generate_team_stats_text(user_id, selected_team_number)

    # Inline keyboard
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

    if message.chat.type == 'private':
        markup.add(types.InlineKeyboardButton("Edit Team📝", callback_data="edit_team"))

    close_button = types.InlineKeyboardButton("Close ❌", callback_data=f"close_{user_id}")
    markup.add(close_button)

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
    INSERT OR IGNORE INTO user_data (
        user_id, username, level, exp, required_exp, yens,
        crystals, tickets, energy, max_energy,
        last_energy_time, choosen_character
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    user_id, username, 1, 0, 12345, 250,
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
    team_number = int(call.data[-1])  # team1 to team5 → number
    selected_team_number = get_main_team(user_id)
    current_main = get_main_team(user_id)

    if team_number == current_main:
        bot.answer_callback_query(call.id, "⚠️ You have already set this team as your main team.", show_alert=True)
        return

    # Update the main team in database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_team_selection (user_id, current_team)
        VALUES (?, ?)
    ''', (user_id, team_number))
    conn.commit()
    conn.close()

    set_main_team(user_id, team_number)  # Update in any in-memory dict if needed

    bot.answer_callback_query(call.id, f"✅ Team {team_number} is now your main team!", show_alert=True)

    team = get_user_team(user_id, team_number)

    team_text = f"<b>✨ Your Current Team (Team {team_number})</b> ✨\n"
    team_text += "━━━━━━━━━━━━━━━\n"
    for char in team:
        team_text += f"<b>✧ {char if char else 'Empty'}</b>\n"
    team_text += "━━━━━━━━━━━━━━━\n"
    team_text += generate_team_stats_text(user_id, selected_team_number)

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
        markup.add(types.InlineKeyboardButton("Edit Team📝", callback_data="edit_team"))

    markup.add(types.InlineKeyboardButton("Close ❌", callback_data=f"close_{user_id}"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=team_text,
        reply_markup=markup,
        parse_mode="HTML"
    )
#@bot.callback_query_handler(func=lambda call: call.data == "edit_team")
@bot.callback_query_handler(func=lambda call: call.data == "edit_team")
def handle_edit_team_callback(call):
    user_id = call.from_user.id
    selected_team_number = get_main_team(user_id)
    team = get_user_team(user_id, selected_team_number)  # This line was missing

    team_text = f"✨Your Current Team (Team {selected_team_number}) ✨\n"
    for i, char in enumerate(team, start=1):
        team_text += f"<b>{i}✧ {char}</b>\n"
    team_text += "━━━━━━━━━━━━━━━\n"

    # Show buttons, etc...
    
    team_text += generate_team_stats_text(user_id, selected_team_number)

    try:
        selected_team_number = get_main_team(user_id)
        prev_page = 0  # Assuming 0 or another appropriate default value

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕ Add", callback_data=f"edit_add:{selected_team_number}:{prev_page}"),
            types.InlineKeyboardButton("🚫 Remove", callback_data=f"edit_remove:{selected_team_number}")
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
    except Exception as e:
        bot.send_message(user_id, f"[EditTeam Error]\nUser: {user_id}\nError: {str(e)}")    
@bot.callback_query_handler(func=lambda call: call.data == "edit_back")
def handle_edit_back(call):
    user_id = call.from_user.id

    # Same logic from the /myteam command
    selected_team_number = get_main_team(user_id)
    team = get_user_team(user_id, team_number=selected_team_number)

    team_text = f"✨<b>Your Current Team (Team {selected_team_number})</b> ✨\n"
    team_text += "━━━━━━━━━━━━━━━\n"
    for i, char in enumerate(team, start=1):
        team_text += f"<b>{i}✧ {char}</b>\n"
    team_text += "━━━━━━━━━━━━━━━\n"
    
    team_text += generate_team_stats_text(user_id, selected_team_number)


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
 # Global variable to keep track of page numbe

ADMIN_ID = 6306216999  # Replace with your Telegram ID
def generate_add_team_interface(user_id, team_number, page=1, temp_selected=None):
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    # Fetch all characters owned by the user
    cursor.execute('''
        SELECT cbs.name
        FROM user_characters uc
        JOIN character_base_stats cbs ON uc.character_id = cbs.character_id
        WHERE uc.user_id = ?
    ''', (user_id,))
    all_chars = sorted([row[0].strip() for row in cursor.fetchall()])

    # Fetch saved team slots
    cursor.execute('''
        SELECT slot1, slot2, slot3
        FROM teams
        WHERE user_id = ? AND team_number = ?
    ''', (user_id, team_number))
    team = list(cursor.fetchone() or ["Empty", "Empty", "Empty"])

    conn.close()

    # Decide what characters are currently selected
    if temp_selected:
        selected_chars = set(x.strip() for x in temp_selected if x and x != "Empty")
    else:
        selected_chars = set(x.strip() for x in team if x and x != "Empty")

    # Include selected characters in the list too (for tick display)
    combined_chars = sorted(set(all_chars + list(selected_chars)))  # ensure no one is skipped

    # Pagination logic
    per_page = 6
    total_pages = max(1, (len(combined_chars) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    visible_chars = combined_chars[start:end]

    # Build keyboard
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for name in visible_chars:
        display_name = name + " ☑" if name in selected_chars else name
        safe_name = name.replace(":", "").replace("|", "")[:50]
        callback = f"selectchar:{safe_name}:{team_number}:{page}"
        buttons.append(InlineKeyboardButton(text=display_name, callback_data=callback[:64]))

    for i in range(0, len(buttons), 2):
        keyboard.row(*buttons[i:i+2])

    keyboard.row(
        InlineKeyboardButton("⏪", callback_data=f"edit_add:{team_number}:{max(1, page - 1)}"),
        InlineKeyboardButton(f"[{page}/{total_pages}]", callback_data="noop"),
        InlineKeyboardButton("⏩", callback_data=f"edit_add:{team_number}:{min(total_pages, page + 1)}")
    )
    keyboard.row(InlineKeyboardButton("💬 Save", callback_data=f"save_team:{team_number}"))
    keyboard.row(InlineKeyboardButton("↪️ Back", callback_data="edit_back"))
    keyboard.row(InlineKeyboardButton("❌ Close", callback_data=f"close_{user_id}"))

    return keyboard
@bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("edit_add"))
def handle_edit_add(call):
    try:
        data_parts = call.data.split(":")
        if len(data_parts) != 3:
            raise ValueError("Invalid callback data: " + call.data)

        _, team_number, page = data_parts
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
        error_msg = f"[EditAdd Error]\nUser: {call.from_user.id}\nError: {str(e)}"
        bot.send_message(ADMIN_ID, error_msg)
        bot.answer_callback_query(call.id, "An error occurred!")
def format_team_message(team, team_number):
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
    return team_message
#def add_character_to_team(user_id, team_number, character_name):
def update_team_message(user_id, team_number, message_id, chat_id):
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    cursor.execute('''
        SELECT slot1, slot2, slot3
        FROM teams
        WHERE user_id = ? AND team_number = ?
    ''', (user_id, team_number))
    team = cursor.fetchone() or ("Empty", "Empty", "Empty")
    conn.close()

    updated_text = (
        f"✨ Your Current Team (Team {team_number}) ✨\n"
        f"━━━━━━━━━━━━━━━\n"
        f"1️⃣ {team[0]}\n"
        f"2️⃣ {team[1]}\n"
        f"3️⃣ {team[2]}\n"
        f"━━━━━━━━━━━━━━━"
    )

    keyboard = generate_add_team_interface(user_id, team_number)

    try:
        bot.edit_message_text(
    chat_id=call.message.chat.id,
    message_id=call.message.message_id,
    text=team_message,
    reply_markup=generate_add_team_interface(user_id, team_number, page, temp_selected=team)
)
    except Exception as e:
        print(f"[Update Team Error] {e}")
@bot.callback_query_handler(func=lambda call: call.data.startswith("selectchar:"))
def handle_selectchar(call):
    try:
        _, char_name, team_number, page = call.data.split(":")
        user_id = call.from_user.id
        team_number = int(team_number)
        page = int(page)

        key = (user_id, team_number)

        # Initialize temporary selection if not exists
        if key not in temp_team_selection:
            conn = sqlite3.connect("chainsaw.db")
            cursor = conn.cursor()
            cursor.execute("SELECT slot1, slot2, slot3 FROM teams WHERE user_id = ? AND team_number = ?", (user_id, team_number))
            team = cursor.fetchone() or ("Empty", "Empty", "Empty")
            temp_team_selection[key] = list(team)
            conn.close()

        team = temp_team_selection[key]

        # Toggle character in team
        if char_name in team:
            team[team.index(char_name)] = "Empty"
        elif "Empty" in team:
            team[team.index("Empty")] = char_name
        else:
            bot.answer_callback_query(call.id, "All slots are full. Remove one to add.")
            return

        # Update message
        preview_text = f"✨ Your Current Team (Team {team_number}) ✨\n━━━━━━━━━━━━━━━\n"
        for name in new_team:
            preview_text += f"✧ {name}\n"
        preview_text += "━━━━━━━━━━━━━━━"

        keyboard = generate_add_team_interface(user_id, team_number, page)
        bot.edit_message_text(preview_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

    except Exception as e:
        print(f"[SelectChar Error]\nUser: {call.from_user.id}\nError: {e}")
        bot.answer_callback_query(call.id, "An error occurred.")

    except Exception as e:
        print(f"[Add Character Error]\nUser: {user_id}\nError: {e}")
        bot.answer_callback_query(call.id, "An error occurred.")
import time

@bot.callback_query_handler(func=lambda call: call.data.startswith("save_team:"))
def handle_save_team(call):
    try:
        user_id = call.from_user.id
        team_number = int(call.data.split(":")[1])
        key = (user_id, team_number)

        if key not in temp_team_selection:
            bot.answer_callback_query(call.id, "No changes to save.")
            return

        team = temp_team_selection[key]
        chat_id = call.message.chat.id
        msg_id = call.message.message_id

        # Animated progress: 1% to 100%
        for i in range(0, 101, 5):  # Step by 5 for faster animation
            dots = "." * ((i // 10) % 4)  # Rotating dot effect
            bot.edit_message_text(
                f"💾 <b>Saving your team {i}%{dots}</b>",
                chat_id,
                msg_id,
                parse_mode="HTML"
            )
            time.sleep(0.10)

        # Save the team to database
        conn = sqlite3.connect("chainsaw.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO teams (user_id, team_number, slot1, slot2, slot3)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, team_number) DO UPDATE SET
                slot1=excluded.slot1,
                slot2=excluded.slot2,
                slot3=excluded.slot3
        ''', (user_id, team_number, *team))
        conn.commit()
        conn.close()

        del temp_team_selection[key]  # Clear after save

        # Final message
        bot.edit_message_text(
            "✅ <b>Team saved successfully!</b>",
            chat_id,
            msg_id,
            parse_mode="HTML"
        )

    except Exception as e:
        print(f"[SaveTeam Error]\nUser: {call.from_user.id}\nError: {e}")
        bot.answer_callback_query(call.id, "Error saving team.")     


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_swap"))
def handle_swap_start(call):
    user_id = call.from_user.id
    team_number = int(call.data.split(":")[1]) if ":" in call.data else 1

    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()
    cursor.execute("SELECT slot1, slot2, slot3 FROM teams WHERE user_id = ? AND team_number = ?", (user_id, team_number))
    team = list(cursor.fetchone() or ["Empty", "Empty", "Empty"])
    conn.close()

    temp_swaps[user_id] = {"team_number": team_number, "team": team[:]}  # deep copy

    keyboard = InlineKeyboardMarkup()
    for i, char in enumerate(team):
        keyboard.add(InlineKeyboardButton(f"{i+1}️⃣ {char}", callback_data=f"swap_from:{team_number}:{i}"))
    keyboard.add(
        InlineKeyboardButton("✅ Save", callback_data=f"swap_save:{team_number}"),
        InlineKeyboardButton("❌ Cancel", callback_data=f"swap_cancel:{team_number}")
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🔄 Choose the character slot to swap FROM:",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("swap_from:"))
def handle_swap_from(call):
    user_id = call.from_user.id
    _, team_number, from_index = call.data.split(":")
    from_index = int(from_index)

    if user_id not in temp_swaps:
        return bot.answer_callback_query(call.id, "No team found to swap.")

    temp_swaps[user_id]["from_index"] = from_index
    team = temp_swaps[user_id]["team"]

    keyboard = InlineKeyboardMarkup()
    for i, char in enumerate(team):
        if i != from_index:
            keyboard.add(InlineKeyboardButton(f"{i+1}️⃣ {char}", callback_data=f"swap_to:{team_number}:{i}"))
    keyboard.add(InlineKeyboardButton("Cancel", callback_data="edit_swap:" + str(team_number)))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🔁 Choose the character slot to swap TO:",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("swap_to:"))
def handle_swap_to(call):
    user_id = call.from_user.id
    _, team_number, to_index = call.data.split(":")
    to_index = int(to_index)

    if user_id not in temp_swaps:
        return bot.answer_callback_query(call.id, "Swap state not found.")

    swap_data = temp_swaps[user_id]
    team = swap_data["team"]
    from_index = swap_data.get("from_index")

    if from_index is None:
        return bot.answer_callback_query(call.id, "Invalid swap start.")

    if team[from_index] == "Empty" and team[to_index] == "Empty":
        return bot.answer_callback_query(call.id, "Cannot swap two empty slots.")

    team[from_index], team[to_index] = team[to_index], team[from_index]  # swap

    # Show preview
    preview = f"✨ Team {team_number} (Preview After Swap) ✨\n━━━━━━━━━━━━━━━"
    for char in team:
        preview += f"\n✧ {char}"
    preview += "\n━━━━━━━━━━━━━━━\nClick '✅ Save' to confirm or '❌ Cancel' to discard."

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Save", callback_data=f"swap_save:{team_number}"),
        InlineKeyboardButton("❌ Cancel", callback_data=f"swap_cancel:{team_number}")
    )

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=preview,
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("swap_save:"))
def handle_swap_save(call):
    user_id = call.from_user.id
    team_number = int(call.data.split(":")[1])

    if user_id not in temp_swaps:
        return bot.answer_callback_query(call.id, "No swap in progress.")

    team = temp_swaps[user_id]["team"]

    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE teams SET slot1 = ?, slot2 = ?, slot3 = ?
        WHERE user_id = ? AND team_number = ?
    ''', (team[0], team[1], team[2], user_id, team_number))
    conn.commit()
    conn.close()

    del temp_swaps[user_id]

    preview = f"✅ Team {team_number} saved!\n━━━━━━━━━━━━━━━"
    for char in team:
        preview += f"\n✧ {char}"
    preview += "\n━━━━━━━━━━━━━━━"

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Back", callback_data="edit_back"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=preview,
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("swap_cancel:"))
def handle_swap_cancel(call):
    user_id = call.from_user.id
    team_number = int(call.data.split(":")[1])
    temp_swaps.pop(user_id, None)

    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()
    cursor.execute("SELECT slot1, slot2, slot3 FROM teams WHERE user_id = ? AND team_number = ?", (user_id, team_number))
    team = list(cursor.fetchone() or ["Empty", "Empty", "Empty"])
    conn.close()

    preview = f"❌ Changes canceled. Showing original team.\n━━━━━━━━━━━━━━━"
    for char in team:
        preview += f"\n✧ {char}"
    preview += "\n━━━━━━━━━━━━━━━"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Back", callback_data="edit_back"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=preview,
        reply_markup=keyboard
    )
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_remove:"))
def handle_remove_menu(call):
    user_id = call.from_user.id
    team_number = int(call.data.split(":")[1])
    selected_team_number = get_main_team(user_id)
    team = get_user_team(user_id, selected_team_number)  # This line was missing

    team_text = f"✨Your Current Team (Team {selected_team_number}) ✨\n"
    for char in team:
        preview += f"\n✧ {char}"
    team_text += "━━━━━━━━━━━━━━━"
    team_text += generate_team_stats_text(user_id, selected_team_number)
    # Fetch team from DB
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()
    cursor.execute("SELECT slot1, slot2, slot3 FROM teams WHERE user_id = ? AND team_number = ?", (user_id, team_number))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return bot.answer_callback_query(call.id, "Team not found.")

    # Check if all slots are empty
    if all(char.lower() in ("empty", "", "none") for char in row if char):
        return bot.answer_callback_query(call.id, "No character to remove.")

    # Build remove options
    markup = types.InlineKeyboardMarkup()
    for idx, char in enumerate(row):
        if char and char.lower() not in ("empty", "", "none"):
            markup.add(types.InlineKeyboardButton(f"❌ Remove {char}", callback_data=f"remove_slot:{team_number}:{idx}"))
    markup.add(types.InlineKeyboardButton("↪️ Back", callback_data="edit_team"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Select a character to remove:\n\n" + team_text,
        reply_markup=markup,
        parse_mode="HTML"
    )


#@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_slot:"))
@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_slot:"))
def handle_remove_slot(call):
    user_id = call.from_user.id
    _, team_number, slot_index = call.data.split(":")
    team_number = int(team_number)
    slot_index = int(slot_index)

    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    cursor.execute("SELECT slot1, slot2, slot3 FROM teams WHERE user_id = ? AND team_number = ?", (user_id, team_number))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return bot.answer_callback_query(call.id, "Team not found.")

    team = list(row)

    if team[slot_index].lower() in ("empty", "", "none"):
        conn.close()
        return bot.answer_callback_query(call.id, f"Slot {slot_index + 1} is already empty!")

    # Remove character and shift left
    new_team = [char for char in team if char.lower() not in ("empty", "", "none")]
    new_team.pop(slot_index)
    while len(new_team) < 3:
        new_team.append("Empty")

    cursor.execute("""
        UPDATE teams
        SET slot1 = ?, slot2 = ?, slot3 = ?
        WHERE user_id = ? AND team_number = ?
    """, (*new_team, user_id, team_number))
    conn.commit()
    conn.close()

    # Build updated preview text
    preview_text = f"✨ Your Current Team (Team {team_number}) ✨\n━━━━━━━━━━━━━━━\n"
    for char in team:
        preview += f"\n✧ {char}"
    preview_text += "━━━━━━━━━━━━━━━"

    # Rebuild and update inline keyboard
    keyboard = generate_add_team_interface(user_id, team_number, page=1)  # default page = 1, or keep track of it if needed
    bot.edit_message_text(preview_text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

    bot.answer_callback_query(call.id, f"Removed character from slot {slot_index + 1}.")

def get_all_devils():
    conn = sqlite3.connect("chainsaw.db")
    c = conn.cursor()
    c.execute("SELECT name, image, level FROM devils")
    results = c.fetchall()
    conn.close()
    return results

@bot.message_handler(commands=['explore'])
def explore(message):
    if message.chat.type != "private":
        bot.reply_to(message, "❌ You can only explore in private chat. Message the bot directly.")
        return

    user_id = message.from_user.id

    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    # Check if user started
    cursor.execute("SELECT * FROM user_data WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        bot.reply_to(message, "❌ You haven't started the game yet.\nUse /start in the group to begin.")
        return
    
    # Check if user has a character in slot1
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()
    cursor.execute("SELECT slot1 FROM teams WHERE user_id = ?", (user_id,))
    slot1 = cursor.fetchone()

    if not slot1 or slot1[0] is None:
        conn.close()
        bot.reply_to(message, "⚠️ You don't have a character assigned to your team.\nUse /myteam to select one.")
        return
    # Fetch devils
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, image, level FROM devils")
    devils = cursor.fetchall()
    conn.close()

    if not devils:
        bot.reply_to(message, "No devils found in the database.")
        return

    selected_devil = random.choice(devils)
    name, image, level = selected_devil

    # Use invisible character to embed image URL
    invisible = "‎"
    hyperlink = f'<a href="{image}">{invisible}</a>'

    quotes = [
        "Will you embrace the darkness or be consumed by it?",
        "Will you fight the devils within, or bow to your fears?",
        "Will you stand with bloodied fists or run with trembling legs?",
        "Will you become the hunter or end up the hunted?",
        "Will you scream in terror or roar in defiance?",
        "Will you face the devil head-on or beg for mercy in the shadows?",
        "Will you carve your name into legend or vanish without a trace?",
        "Will you protect the weak or join the corpses they leave behind?",
        "Will you rise with steel in your heart or break under pressure?",
        "Will you walk the path of chaos or cower behind false peace?", 
        "Will you charge into the abyss with fire in your heart, or cower in the shadows of fear?", 
        "Will you stand tall with blade in hand, or kneel before the monsters that haunt your soul?"
        "Will you embrace the darkness and fight, or run until the night swallows you whole?", 
        "Will you forge your fate in blood and fury, or be forgotten like a whisper in the wind?", 
        "Will you become legend, or fade as another nameless coward?", 
        "Will you conquer your demons, or let them rule you?", 
        "Will you rise with vengeance in your veins, or fall with regret in your eyes?"
    ]
    random_quote = random.choice(quotes)

    caption = (f"""{hyperlink}<b>▰▰▰▰▰▰▰▰▰▰▰▰▰</b>
<b>A wild {name.title()} (lvl {level}),</b>  
<b>has challenged you!</b>
<b>▰▰▰▰▰▰▰▰▰▰▰▰▰</b>
<b>{random_quote}</b>
<b>▰▰▰▰▰▰▰▰▰▰▰▰▰▰</b>""")

    markup = types.InlineKeyboardMarkup()
    hunt_button = types.InlineKeyboardButton(text="Hunt 🔫", callback_data=f"hunt_devil_{user_id}")
    markup.add(hunt_button)

    bot.send_message(
        chat_id=message.chat.id,
        text=caption,
        parse_mode="HTML",
        reply_to_message_id=message.message_id,
        reply_markup=markup
    )


# Chest drop logic as a separate function
def handle_chest_drop(user_id, chat_id):
    chests = [
        ("D rank chest", "https://files.catbox.moe/sdoe76.jpg", [("Yens", 500), ("Yens", 800)], 90),
        ("C rank chest", "https://files.catbox.moe/d090y2.jpg", [("Yens", 1000), ("Yens", 1500), ("Crystals", 100), ("Crystals", 300)], 50),
        ("B rank chest", "https://files.catbox.moe/ohz2rr.jpg", [("Crystals", 200), ("Crystals", 500), ("Tickets", 20)], 20),
        ("A rank chest", "https://files.catbox.moe/su5stl.jpg", [("Crystals", 500), ("Crystals", 600), ("Tickets", 40)], 5)
    ]

    random.shuffle(chests)  # Randomize order

    for chest_name, chest_img, rewards, drop_rate in chests:
        if random.randint(1, 100) <= drop_rate:
            reward_type, reward_amount = random.choice(rewards)

            conn = sqlite3.connect("chainsaw.db")
            cursor = conn.cursor()

            if reward_type == "Yens":
                cursor.execute("UPDATE user_data SET yens = yens + ? WHERE user_id = ?", (reward_amount, user_id))
            elif reward_type == "crystals":
                cursor.execute("UPDATE user_data SET crystals = crystals + ? WHERE user_id = ?", (reward_amount, user_id))
            elif reward_type == "Tickets":
                try:
                    cursor.execute("ALTER TABLE user_data ADD COLUMN tickets INTEGER DEFAULT 0")
                except:
                    pass
                cursor.execute("UPDATE user_data SET tickets = tickets + ? WHERE user_id = ?", (reward_amount, user_id))

            conn.commit()
            conn.close()

            reward_caption = (
                f"<b>{chest_name}</b>\n"
                f"Reward: <b>{reward_amount} {reward_type}</b>"
            )
            bot.send_photo(
                chat_id=chat_id,
                photo=chest_img,
                caption=reward_caption,
                parse_mode="HTML"
            )
            break  # Exit after first chest drop
import random
import sqlite3

def handle_chest_drop(user_id, chat_id):
    chests = [
        ("A-Rank Chest", "https://files.catbox.moe/su5stl.jpg", [("Crystals", 500), ("Crystals", 600), ("Tickets", 40)], 0.5),
        ("B-Rank Chest", "https://files.catbox.moe/ohz2rr.jpg", [("Crystals", 200), ("Crystals", 500), ("Tickets", 20)], 1.0),
        ("C-Rank Chest", "https://files.catbox.moe/d090y2.jpg", [("Yens", 1000), ("Yens", 1500), ("Crystals", 100), ("Crystals", 300)], 2.0),
        ("D-Rank Chest", "https://files.catbox.moe/sdoe76.jpg", [("Yens", 500), ("Yens", 800)], 2.5)
    ]

    roll = random.uniform(0, 100)
    cumulative = 0
    selected_chest = None

    for chest in reversed(chests):  # Start from A-rank for rarity check
        cumulative += chest[3]
        if roll <= cumulative:
            selected_chest = chest
            break

    if not selected_chest:
        return  # No chest dropped

    chest_name, chest_img, rewards, _ = selected_chest
    reward_type, reward_amount = random.choice(rewards)

    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    if reward_type == "Yens":
        cursor.execute("UPDATE user_data SET yens = yens + ? WHERE user_id = ?", (reward_amount, user_id))
    elif reward_type == "Crystals":
        cursor.execute("UPDATE user_data SET crystals = crystals + ? WHERE user_id = ?", (reward_amount, user_id))
    elif reward_type == "Tickets":
        try:
            cursor.execute("ALTER TABLE user_data ADD COLUMN tickets INTEGER DEFAULT 0")
        except:
            pass
        cursor.execute("UPDATE user_data SET tickets = tickets + ? WHERE user_id = ?", (reward_amount, user_id))

    conn.commit()
    conn.close()

    reward_caption = (
        f"<b>🎁 {chest_name} Appears!</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"<b>You've obtained:</b>\n"
        f"<b>{reward_amount} {reward_type}</b>\n"
        f"━━━━━━━━━━━━━\n"
        f"Keep hunting, brave warrior!"
    )

    bot.send_photo(
        chat_id=chat_id,
        photo=chest_img,
        caption=reward_caption,
        parse_mode="HTML"
    )
def start_battle(user_id, character_id, call):
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()

    # Get user's character level
    cursor.execute("SELECT level FROM user_characters WHERE user_id = ? AND character_id = ?", (user_id, character_id))
    user_data = cursor.fetchone()
    if not user_data:
        conn.close()
        return
    user_level = user_data[0]

    # Get character moves and unlock levels
    cursor.execute('''
        SELECT move_1, move_1_unlock_level,
               move_2, move_2_unlock_level,
               move_3, move_3_unlock_level,
               special_ability, special_ability_unlock_level
        FROM character_base_stats
        WHERE character_id = ?
    ''', (character_id,))
    moves = cursor.fetchone()
    conn.close()

    move_1, lvl_1, move_2, lvl_2, move_3, lvl_3, special, special_lvl = moves

    # Inline keyboard
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup(row_width=2)

    buttons = []
    if user_level >= lvl_1:
        buttons.append(InlineKeyboardButton(text=move_1, callback_data=f"move:{move_1}"))
    if user_level >= lvl_2:
        buttons.append(InlineKeyboardButton(text=move_2, callback_data=f"move:{move_2}"))
    if user_level >= lvl_3:
        buttons.append(InlineKeyboardButton(text=move_3, callback_data=f"move:{move_3}"))
    if user_level >= special_lvl:
        buttons.append(InlineKeyboardButton(text=special, callback_data=f"special:{special}"))

    markup.add(*buttons)

    # Edit original message with inline keyboard
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="⚔️ Choose your move!",
        reply_markup=markup
    )    
@bot.callback_query_handler(func=lambda call: call.data.startswith("hunt_devil_"))
def hunt_devil(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    conn = sqlite3.connect("chainsaw.db")
    cursor = conn.cursor()
    cursor.execute("SELECT character_id FROM user_characters WHERE user_id = ?", (user_id,))
    char_result = cursor.fetchone()
    conn.close()
    if not char_result:
        bot.answer_callback_query(call.id, "You haven't selected a character yet.")
        return
    character_id = char_result[0]

    # (Optional) devil battle logic here...

    # Then handle the chest drop
    handle_chest_drop(user_id, chat_id)
    start_battle(user_id, character_id, call)
    bot.answer_callback_query(call.id, "You battled the devil!")   
@bot.message_handler(commands=['user_info'])
def user_info(message):
    admin_id = 6306216999  # Replace with your Telegram ID

    if message.from_user.id != admin_id:
        bot.reply_to(message, "You're not authorized to use this command.")
        return

    # Get the replied user
    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a user's message to get their info.")
        return

    target_user = message.reply_to_message.from_user
    user_id = target_user.id
    username = target_user.first_name

    try:
        conn = sqlite3.connect("chainsaw.db")
        cursor = conn.cursor()

        # Fetch characters
        cursor.execute('''
            SELECT cb. name FROM user_characters uc
            JOIN character_base_stats cb ON uc.character_id = cb.character_id
            WHERE uc.user_id = ?
        ''', (user_id,))
        characters = [row[0] for row in cursor.fetchall()]
        character_list = "\n• " + "\n• ".join(characters) if characters else "No characters"

        # Fetch resources
        cursor.execute('''
            SELECT yens, crystals, tickets, exp, level FROM user_data WHERE user_id = ?
        ''', (user_id,))
        data = cursor.fetchone()

        if not data:
            bot.reply_to(message, "User not found in database.")
            return

        yens, crystals, tickets, exp, level = data

        msg = (
            f"<b>👤 User Info</b>\n"
            f"<code>User ID:</code> <b>{user_id}</b>\n"
            f"<code>Name:</code> <b>{username}</b>\n"
            "━━━━━━━━━━━━━\n"
            f"<b>Characters:</b>{character_list}\n"
            "━━━━━━━━━━━━━\n"
            f"<b>Resources:</b>\n"
            f"Yens: <b>{yens}</b>\n"
            f"Crystals: <b>{crystals}</b>\n"
            f"Tickets: <b>{tickets}</b>\n"
            f"EXP: <b>{exp}</b>\n"
            f"Level: <b>{level}</b>\n"
        )

        bot.reply_to(message, msg, parse_mode="HTML")

    except Exception as e:
        print(f"[User Info Error] {e}")
        bot.reply_to(message, "Something went wrong.")
    finally:
        conn.close()
bot.polling(none_stop=True)
