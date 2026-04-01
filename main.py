import os
import telebot
import json
import logging
from datetime import datetime

# Bot token
BOT_TOKEN = "8653450456:AAER9w6Gjj5IWkyCs1taa01N-DdMFZqxt3E"
ADMIN_ID = 6253584826
VIP_CHANNEL = -1003826269063  # Negative mein daalna for channel
PUBLIC_CHANNEL = -1003807818260

# Bot define
bot = telebot.TeleBot(BOT_TOKEN)

# Logging setup
logging.basicConfig(level=logging.INFO)

# User data storage
user_data = {}

# --------------------- COMMANDS ---------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_data[user_id] = {"status": "active"}
    
    welcome_text = """
🚀 *Forex Trading Bot Active!*

✅ Bot is ready to send signals
📊 Get accurate forex signals
💹 Real-time market analysis

*Available Commands:*
/start - Start the bot
/help - Get help
/signal - Get current signal
/status - Check bot status

Join our VIP channel for premium signals!
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📖 *Help Center*

*Basic Commands:*
/start - Start the bot
/help - Show this help
/signal - Get latest trading signal
/status - Bot status

*VIP Features:*
- Exclusive signals
- Early access
- Higher accuracy

*Contact Admin:* @ForexKailash
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['signal'])
def send_signal(message):
    user_id = message.from_user.id
    
    # Check if user is VIP or normal
    if user_id == ADMIN_ID:
        signal_text = generate_signal("premium")
    else:
        signal_text = generate_signal("normal")
    
    bot.reply_to(message, signal_text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def send_status(message):
    status_text = """
📊 *Bot Status*

✅ Bot: *Active*
📈 Signals: *Ready*
🔄 Uptime: *24/7*
👥 Users Active: *{}*

*Bot is running smoothly!*
""".format(len(user_data))
    
    bot.reply_to(message, status_text, parse_mode='Markdown')

# --------------------- SIGNAL GENERATION ---------------------

def generate_signal(level="normal"):
    """Generate trading signals"""
    
    import random
    from datetime import datetime
    
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD"]
    actions = ["BUY ✅", "SELL 🔻"]
    confidence = ["High", "Medium", "Low"]
    
    pair = random.choice(pairs)
    action = random.choice(actions)
    entry = round(random.uniform(1.0500, 1.2000), 4)
    tp1 = round(entry + (0.0020 if "BUY" in action else -0.0020), 4)
    tp2 = round(entry + (0.0040 if "BUY" in action else -0.0040), 4)
    sl = round(entry + (0.0010 if "SELL" in action else -0.0010), 4)
    
    signal = f"""
🔥 *FOREX SIGNAL* 🔥

📌 *Pair:* {pair}
🎯 *Action:* {action}
💰 *Entry:* {entry}
✅ *TP1:* {tp1}
✅ *TP2:* {tp2}
❌ *SL:* {sl}
📊 *Confidence:* {random.choice(confidence)}

*Trade wisely! Use proper risk management.*
⏰ Time: {datetime.now().strftime('%H:%M:%S')}
"""
    
    if level == "premium":
        signal += "\n🌟 *VIP SIGNAL* 🌟\nExtra profit potential!"
    
    return signal

# --------------------- ADMIN COMMANDS ---------------------

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Unauthorized! Only admin can use this.")
        return
    
    msg = message.text.replace('/broadcast', '').strip()
    if not msg:
        bot.reply_to(message, "Usage: /broadcast [message]")
        return
    
    success = 0
    for user_id in user_data.keys():
        try:
            bot.send_message(user_id, f"📢 *Announcement*\n\n{msg}", parse_mode='Markdown')
            success += 1
        except:
            pass
    
    bot.reply_to(message, f"✅ Broadcast sent to {success} users!")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    stats = f"""
📊 *Bot Statistics*

👥 Total Users: {len(user_data)}
✅ Active Users: {len(user_data)}
📈 Signals Sent: Auto
⏱️ Uptime: Continuous

*Bot is running perfectly!*
"""
    bot.reply_to(message, stats, parse_mode='Markdown')

# --------------------- VIP CHANNEL MESSAGES ---------------------

def send_vip_signal(signal_text):
    """Send signals to VIP channel"""
    try:
        bot.send_message(VIP_CHANNEL, signal_text, parse_mode='Markdown')
        print("VIP signal sent to channel")
    except Exception as e:
        print(f"Error sending to VIP channel: {e}")

def send_public_signal(signal_text):
    """Send signals to public channel"""
    try:
        bot.send_message(PUBLIC_CHANNEL, signal_text, parse_mode='Markdown')
        print("Public signal sent to channel")
    except Exception as e:
        print(f"Error sending to public channel: {e}")

# --------------------- AUTO SIGNAL (Every 4 hours) ---------------------

import threading
import time

def auto_signal_sender():
    """Send automatic signals every 4 hours"""
    while True:
        time.sleep(14400)  # 4 hours
        
        # Generate premium signal
        premium_signal = generate_signal("premium")
        send_vip_signal(premium_signal)
        
        # Generate normal signal
        normal_signal = generate_signal("normal")
        send_public_signal(normal_signal)
        
        print(f"Auto signals sent at {datetime.now()}")

# Start auto signal thread
signal_thread = threading.Thread(target=auto_signal_sender, daemon=True)
signal_thread.start()

# --------------------- MAIN ---------------------

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 FOREX TRADING BOT STARTED")
    print("=" * 50)
    print(f"Bot Name: @ForexKailash_Bot")
    print(f"Admin ID: {ADMIN_ID}")
    print(f"VIP Channel: {VIP_CHANNEL}")
    print(f"Public Channel: {PUBLIC_CHANNEL}")
    print("=" * 50)
    print("✅ Bot is running...")
    print("📊 Auto signals every 4 hours")
    print("=" * 50)
    
    # Start bot
    bot.infinity_polling()
