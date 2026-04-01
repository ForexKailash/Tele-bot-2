import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import threading
import time
import json
import logging

# Import modules
from signals import SignalGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "8653450456:AAER9w6Gjj5IWkyCs1taa01N-DdMFZqxt3E"
ADMIN_ID = 6253584826

# Website details
WEBSITE_URL = "https://forexkailash.netlify.app"
UPI_ID = "kailashbhardwaj66-2@okicici"
VIP_PRICE = "₹399/month"
VIP_LINK = "https://t.me/+Snj0BVAwjDo3NTA1"

# =====================================================
# 🔴 IMPORTANT: YAHAN APNE CHANNEL IDs DALEN 🔴
# =====================================================
# Channel ID kaise nikale:
# 1. Channel mein bot ko admin banao
# 2. @userinfobot se channel se koi message forward karo
# 3. Negative number mil jayega (jaise -1001234567890)
# =====================================================

# Public channel ID (jahan free signals jayenge)
PUBLIC_CHANNEL = -1003807818260  # <- APNA PUBLIC CHANNEL ID DALO

# VIP channel ID (jahan premium signals jayenge)  
VIP_CHANNEL = -1003826269063     # <- APNA VIP CHANNEL ID DALO

# =====================================================
# Agar channel ID nahi hai to None rakh do:
# PUBLIC_CHANNEL = None
# VIP_CHANNEL = None
# =====================================================

# Initialize bot and signal generator
bot = telebot.TeleBot(BOT_TOKEN)
signal_gen = SignalGenerator()

# User data
user_data = {}
free_signal_count = {}
active_trades = {}

# Load data
try:
    with open('user_data.json', 'r') as f:
        user_data = json.load(f)
except:
    pass

try:
    with open('free_count.json', 'r') as f:
        free_signal_count = json.load(f)
except:
    pass

# Save functions
def save_user_data():
    with open('user_data.json', 'w') as f:
        json.dump(user_data, f)

def save_free_count():
    with open('free_count.json', 'w') as f:
        json.dump(free_signal_count, f)

# --------------------- BUTTONS ---------------------

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("📊 Free Signal", callback_data="free_signal"),
        InlineKeyboardButton("👑 VIP Channel", callback_data="vip_channel"),
        InlineKeyboardButton("📈 Live Rates", callback_data="live_rates"),
        InlineKeyboardButton("🌐 Website", callback_data="website"),
        InlineKeyboardButton("📞 Support", callback_data="support")
    ]
    keyboard.add(*buttons)
    return keyboard

def vip_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("👑 Join VIP", url=VIP_LINK),
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
        user_data[user_id] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username,
            "joined": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
💎 VIP Signals: 25-30/day

*Choose an option:* 👇
"""
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=main_menu())

# --------------------- FREE SIGNAL (LIVE DATA) ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "free_signal")
def free_signal_handler(call):
    user_id = str(call.from_user.id)
    
    # Check free limit
    if free_signal_count.get(user_id, 0) >= 3:
        limit_text = """
⚠️ *Free Signal Limit Reached* ⚠️

You have received 3 free signals today.

🌟 *Join VIP for Unlimited Signals!* 🌟

*VIP Benefits:*
• 25-30 Premium Signals Daily
• Early Entry (Before Public)
• Live Market Analysis
• 1-on-1 VIP Support
• 89% Win Rate

💰 *Price:* ₹399/month
"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("👑 Join VIP", url=VIP_LINK))
        keyboard.add(InlineKeyboardButton("💳 Payment Info", callback_data="payment_info"))
        keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        
        bot.edit_message_text(limit_text, call.message.chat.id, call.message.message_id, 
                             parse_mode='Markdown', reply_markup=keyboard)
        bot.answer_callback_query(call.id, "Daily limit reached! Join VIP for more")
        return
    
    # Show loading
    bot.edit_message_text("🔍 *Analyzing live market data...*\n\nFetching real-time prices and generating signal...", 
                         call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    # Get best signal from live data
    signal = signal_gen.get_best_signal()
    
    if not signal:
        error_text = """
❌ *No Signal Available Right Now* ❌

Market conditions are not ideal for a trade.

📊 *Why?*
• Waiting for clear confirmation
• Indicators not aligned
• Low volatility period

⏰ *Next scan in 15 minutes*
"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔄 Try Again", callback_data="free_signal"))
        keyboard.add(InlineKeyboardButton("👑 VIP Early Access", callback_data="vip_channel"))
        keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        
        bot.edit_message_text(error_text, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=keyboard)
        bot.answer_callback_query(call.id, "No signal currently. Try again later!")
        return
    
    # Format and send signal
    signal_text = signal_gen.format_signal_message(signal, is_vip=False)
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 New Signal", callback_data="free_signal"))
    keyboard.add(InlineKeyboardButton("👑 Get VIP", callback_data="vip_channel"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    
    bot.edit_message_text(signal_text, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=keyboard)
    
    # Increment free count
    free_signal_count[user_id] = free_signal_count.get(user_id, 0) + 1
    save_free_count()
    
    # Send to public channel if configured
    if PUBLIC_CHANNEL:
        try:
            bot.send_message(PUBLIC_CHANNEL, signal_text, parse_mode='Markdown')
            logger.info(f"Signal sent to public channel at {datetime.now()}")
        except Exception as e:
            logger.error(f"Error sending to public channel: {e}")
    
    bot.answer_callback_query(call.id, f"📊 Signal generated! {3 - free_signal_count[user_id]} free left")

# --------------------- LIVE RATES ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "live_rates")
def live_rates_handler(call):
    from market_data import MarketData
    md = MarketData()
    
    pairs = {
        "XAUUSD=X": "🟡 Gold",
        "EURUSD=X": "💶 EUR/USD",
        "GBPUSD=X": "💷 GBP/USD",
        "BTC-USD": "₿ Bitcoin",
        "NQ=F": "📊 NAS100"
    }
    
    rates_text = "📈 *Live Market Rates*\n\n"
    
    for symbol, name in pairs.items():
        price = md.get_live_price(symbol)
        if price:
            rates_text += f"{name}: ${price:.2f}\n"
        else:
            rates_text += f"{name}: 🔴 Offline\n"
    
    rates_text += f"\n⏰ Updated: {datetime.now().strftime('%H:%M:%S')} IST"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 Refresh", callback_data="live_rates"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    
    bot.edit_message_text(rates_text, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=keyboard)
    bot.answer_callback_query(call.id)

# --------------------- VIP CHANNEL ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "vip_channel")
def vip_channel_handler(call):
    vip_text = f"""
👑 *VIP CHANNEL* 👑

*VIP Benefits:*
• 25-30 Premium Signals Daily
• Early Entry (5-10 min before public)
• Live Market Analysis
• 1-on-1 VIP Support
• 89% Win Rate Guarantee

💰 *Price:* {VIP_PRICE}

👇 *Join now for instant access*
"""
    bot.edit_message_text(vip_text, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=vip_menu())
    bot.answer_callback_query(call.id)

# --------------------- PAYMENT INFO ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "payment_info")
def payment_info_handler(call):
    payment_text = f"""
💳 *Payment Details*

💰 *VIP Plan:* {VIP_PRICE}

*UPI Payment:*
