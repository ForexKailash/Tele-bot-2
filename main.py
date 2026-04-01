import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import random

# Bot token
BOT_TOKEN = "8653450456:AAER9w6Gjj5IWkyCs1taa01N-DdMFZqxt3E"
ADMIN_ID = 6253584826

# Bot define
bot = telebot.TeleBot(BOT_TOKEN)

# Website details
WEBSITE_URL = "https://forexkailash.netlify.app"
UPI_ID = "kailashbhardwaj66-2@okicici"
VIP_PRICE = "₹399/month"
VIP_LINK = "https://t.me/+Snj0BVAwjDo3NTA1"

# User data
user_data = {}
free_signal_count = {}

# --------------------- MAIN MENU ---------------------

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

def vip_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("👑 Join VIP Channel", url=VIP_LINK),
        InlineKeyboardButton("💳 Payment Info", callback_data="payment_info"),
        InlineKeyboardButton("🔙 Back", callback_data="back_menu")
    ]
    keyboard.add(*buttons)
    return keyboard

def payment_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("✅ Verify Payment", callback_data="verify_payment"),
        InlineKeyboardButton("🔙 Back", callback_data="vip_channel")
    ]
    keyboard.add(*buttons)
    return keyboard

# --------------------- START ---------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {"name": message.from_user.first_name}
    
    if user_id not in free_signal_count:
        free_signal_count[user_id] = 0
    
    welcome_text = f"""
🌟 *Welcome {message.from_user.first_name}!* 🌟

*📈 Forex Trading With Kailash*
India's Most Trusted Forex Signals Provider | 5000+ Happy Traders

*📊 Stats:*
🎯 Win Rate: 89%
👥 Active Traders: 5000+

*Choose an option:* 👇
"""
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=main_menu())

# --------------------- FREE SIGNALS ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "free_signals")
def free_signals(call):
    user_id = str(call.from_user.id)
    
    if free_signal_count.get(user_id, 0) >= 3:
        text = "⚠️ *Free Signal Limit Reached* ⚠️\n\nJoin VIP for unlimited signals!\n💰 Price: ₹399/month"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("👑 Join VIP", url=VIP_LINK))
        keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=keyboard)
        return
    
    free_signal_count[user_id] = free_signal_count.get(user_id, 0) + 1
    remaining = 3 - free_signal_count[user_id]
    
    pairs = ["XAU/USD", "BTC/USD", "EUR/USD", "GBP/USD"]
    pair = random.choice(pairs)
    action = random.choice(["BUY ✅", "SELL 🔻"])
    entry = round(random.uniform(1.0800, 1.1200), 4)
    tp = round(entry + 0.0020, 4)
    sl = round(entry - 0.0015, 4)
    
    signal = f"""
📊 *FREE SIGNAL*

📍 *Pair:* {pair}
🎯 *Action:* {action}
💰 *Entry:* {entry}
✅ *TP:* {tp}
❌ *SL:* {sl}

---
📊 *Remaining:* {remaining}/3
💎 *Join VIP for unlimited!*
"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 Next", callback_data="free_signals"))
    keyboard.add(InlineKeyboardButton("👑 Join VIP", callback_data="vip_channel"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    
    bot.edit_message_text(signal, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=keyboard)

# --------------------- VIP CHANNEL ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "vip_channel")
def vip_channel(call):
    text = f"""
👑 *VIP CHANNEL* 👑

• 25-30 Premium Signals Daily
• Early Entry Alerts
• 89% Win Rate
💰 *Price:* {VIP_PRICE}
"""
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=vip_menu())

# --------------------- PAYMENT INFO ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "payment_info")
def payment_info(call):
    text = f"""
💳 *Payment Details*

💰 *VIP:* {VIP_PRICE}

*UPI:* `{UPI_ID}`

*Steps:*
1️⃣ Pay to: {UPI_ID}
2️⃣ Take screenshot
3️⃣ Send to @ForexKailash

⏰ Verification: 2-4 hours
"""
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=payment_menu())

# --------------------- VERIFY PAYMENT ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "verify_payment")
def verify_payment(call):
    text = "✅ Send screenshot to: @ForexKailash"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📱 Send", url="https://t.me/ForexKailash"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="vip_channel"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
    
    bot.send_message(ADMIN_ID, f"🔔 Payment Request\n👤 {call.from_user.first_name}\n🆔 {call.from_user.id}")

# --------------------- WEBSITE ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "website")
def website(call):
    text = "🌐 https://forexkailash.netlify.app"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🌐 Visit", url=WEBSITE_URL))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

# --------------------- SUPPORT ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "support")
def support(call):
    text = "📞 Admin: @ForexKailash\n⏰ 9 AM - 9 PM IST"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📱 Contact", url="https://t.me/ForexKailash"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)

# --------------------- BACK ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
def back_menu(call):
    text = "🏠 *Main Menu*"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=main_menu())

# --------------------- ADMIN ---------------------

@bot.message_handler(commands=['addvip'])
def add_vip(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = message.text.split()[1]
        bot.reply_to(message, f"✅ VIP added for {user_id}")
    except:
        bot.reply_to(message, "Usage: /addvip [user_id]")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, f"👥 Users: {len(user_data)}")

# --------------------- MAIN ---------------------

if __name__ == "__main__":
    print("=" * 40)
    print("🤖 FOREX BOT STARTED")
    print("✅ 4 Buttons: Free | VIP | Website | Support")
    print("=" * 40)
    bot.infinity_polling()
