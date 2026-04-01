import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import threading
import time
import random
import json

# Bot token
BOT_TOKEN = "8653450456:AAER9w6Gjj5IWkyCs1taa01N-DdMFZqxt3E"
ADMIN_ID = 6253584826

# Website details
WEBSITE_URL = "https://forexkailash.netlify.app"
UPI_ID = "kailashbhardwaj66-2@okicici"
VIP_PRICE = "₹399/month"
VIP_SIGNALS = "25-30 Premium Signals Daily"
VIP_LINK = "https://t.me/+Snj0BVAwjDo3NTA1"

# Bot define - YAHI IMPORTANT HAI!
bot = telebot.TeleBot(BOT_TOKEN)

# User data storage
user_data = {}
vip_users = {}
free_signal_count = {}

# Load existing data
try:
    with open('user_data.json', 'r') as f:
        user_data = json.load(f)
except:
    pass

try:
    with open('vip_users.json', 'r') as f:
        vip_users = json.load(f)
except:
    pass

try:
    with open('free_count.json', 'r') as f:
        free_signal_count = json.load(f)
except:
    pass

# --------------------- MAIN MENU BUTTONS ---------------------

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("📊 Free Signals", callback_data="free_signals"),
        InlineKeyboardButton("👑 VIP Channel", callback_data="vip_channel"),
        InlineKeyboardButton("🌐 Website", callback_data="website"),
        InlineKeyboardButton("📞 Support", callback_data="support")
    ]
    keyboard.add(*buttons)
    return keyboard

def vip_join_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("👑 Join VIP Channel", url=VIP_LINK),
        InlineKeyboardButton("💳 Payment Info", callback_data="payment_info"),
        InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")
    ]
    keyboard.add(*buttons)
    return keyboard

def payment_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("✅ Verify Payment", callback_data="verify_payment"),
        InlineKeyboardButton("🔙 Back to VIP", callback_data="vip_channel")
    ]
    keyboard.add(*buttons)
    return keyboard

# --------------------- START COMMAND ---------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username,
            "joined_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "status": "active"
        }
        save_user_data()
    
    if user_id not in free_signal_count:
        free_signal_count[user_id] = 0
        save_free_count()
    
    welcome_text = f"""
🌟 *Welcome {message.from_user.first_name}!* 🌟

*📈 Forex Trading With Kailash*
India's Most Trusted Forex Signals Provider | 5000+ Happy Traders

*📊 Stats:*
🎯 Win Rate: 89%
👥 Active Traders: 5000+
⏰ Support: 24/7

*Choose an option below:* 👇
"""
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode='Markdown',
        reply_markup=main_menu()
    )

# --------------------- FREE SIGNALS ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "free_signals")
def free_signals(call):
    user_id = str(call.from_user.id)
    
    if user_id not in free_signal_count:
        free_signal_count[user_id] = 0
    
    if free_signal_count[user_id] >= 3:
        limit_reached_text = """
⚠️ *Free Signal Limit Reached* ⚠️

You have already received 3 free signals.

🌟 *Join VIP Channel for Unlimited Signals!* 🌟

*VIP Benefits:*
• 25-30 Premium Signals Daily
• Early Entry Alerts
• Live Market Analysis
• 1-on-1 VIP Support
• 89% Win Rate Guarantee

💰 *Price:* ₹399/month
"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("👑 Join VIP Channel", url=VIP_LINK))
        keyboard.add(InlineKeyboardButton("💳 Payment Info", callback_data="payment_info"))
        keyboard.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=limit_reached_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        return
    
    signal = generate_free_signal()
    free_signal_count[user_id] += 1
    save_free_count()
    
    remaining = 3 - free_signal_count[user_id]
    
    signal_text = f"""
{signal}

---
📊 *Free Signals Remaining:* {remaining}/3
💎 *Join VIP for unlimited signals!*
"""
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 Next Signal", callback_data="free_signals"))
    keyboard.add(InlineKeyboardButton("👑 Join VIP", callback_data="vip_channel"))
    keyboard.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=signal_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

def generate_free_signal():
    from datetime import datetime
    
    pairs = ["XAU/USD (Gold)", "BTC/USD", "EUR/USD", "GBP/USD", "NAS100", "USOIL"]
    actions = ["BUY ✅", "SELL 🔻"]
    
    pair = random.choice(pairs)
    action = random.choice(actions)
    
    entry = round(random.uniform(1.0800, 1.1200), 4)
    tp1 = round(entry + 0.0020, 4)
    tp2 = round(entry + 0.0040, 4)
    sl = round(entry - 0.0015, 4)
    
    if "Gold" in pair:
        entry = random.randint(2150, 2180)
        tp1 = entry + 15
        tp2 = entry + 30
        sl = entry - 10
    elif "BTC" in pair:
        entry = random.randint(65000, 68000)
        tp1 = entry + 500
        tp2 = entry + 1000
        sl = entry - 300
    
    signal = f"""
📊 *FREE SIGNAL*

📍 *Pair:* {pair}
🎯 *Action:* {action}
💰 *Entry:* {entry}
✅ *TP1:* {tp1}
✅ *TP2:* {tp2}
❌ *SL:* {sl}

⏰ Time: {datetime.now().strftime('%H:%M:%S')} IST
"""
    return signal

# --------------------- VIP CHANNEL ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "vip_channel")
def vip_channel(call):
    vip_text = f"""
👑 *VIP CHANNEL* 👑

*VIP Benefits:*
• {VIP_SIGNALS}
• Early Entry Alerts
• Live Market Analysis
• 1-on-1 VIP Support
• 89% Win Rate Guarantee

💰 *Price:* {VIP_PRICE}

👇 *Click below to join*
"""
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=vip_text,
        parse_mode='Markdown',
        reply_markup=vip_join_menu()
    )

# --------------------- PAYMENT INFO ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "payment_info")
def payment_info(call):
    payment_text = f"""
💳 *Payment Details*

💰 *Plan:* VIP Monthly
💵 *Amount:* {VIP_PRICE}

*UPI Payment:*
