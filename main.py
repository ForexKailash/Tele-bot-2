# main.py
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import threading
import time
import json
import logging

# Import custom modules
from config import *
from signals import SignalGenerator
from database import Database

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize modules
signal_gen = SignalGenerator()
db = Database()

# Track sent messages for editing
sent_messages = {}

# --------------------- BUTTONS ---------------------

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("📊 Free Signal", callback_data="free_signal"),
        InlineKeyboardButton("👑 VIP Channel", callback_data="vip_channel"),
        InlineKeyboardButton("📈 Live Rates", callback_data="live_rates"),
        InlineKeyboardButton("🎓 Courses", callback_data="courses"),
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
        InlineKeyboardButton("🎓 Courses", callback_data="courses"),
        InlineKeyboardButton("🔙 Back", callback_data="back_menu")
    ]
    keyboard.add(*buttons)
    return keyboard

def courses_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("📚 Forex Mastery Course", callback_data="course_forex"),
        InlineKeyboardButton("💰 Smart Money Concepts", callback_data="course_smc"),
        InlineKeyboardButton("🎯 Price Action Pro", callback_data="course_pa"),
        InlineKeyboardButton("👑 VIP + Course Bundle", callback_data="course_bundle"),
        InlineKeyboardButton("🔙 Back", callback_data="back_menu")
    ]
    keyboard.add(*buttons)
    return keyboard

def payment_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("✅ Verify Payment", callback_data="verify_payment"),
        InlineKeyboardButton("🎓 Courses", callback_data="courses"),
        InlineKeyboardButton("🔙 Back", callback_data="vip_channel")
    ]
    keyboard.add(*buttons)
    return keyboard

# --------------------- START COMMAND ---------------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    db.add_user(user_id, message.from_user.first_name, message.from_user.username)
    
    welcome_text = f"""
🌟 *Welcome {message.from_user.first_name}!* 🌟

*📈 Forex Trading With Kailash*
India's Most Trusted Forex Signals Provider

*📊 Our Stats:*
🎯 Win Rate: 89%
👥 Active Traders: 5000+
⏰ Support: 24/7
💎 VIP Signals: 25-30/day

*Choose an option below:* 👇
"""
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=main_menu()
    )

# --------------------- FREE SIGNAL ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "free_signal")
def free_signal_handler(call):
    user_id = call.from_user.id
    free_count = db.get_free_count(user_id)
    
    if free_count >= 3 and not db.is_vip(user_id):
        limit_text = """
⚠️ *Free Signal Limit Reached* ⚠️

You have received 3 free signals today.

🌟 *Join VIP for Unlimited Signals!* 🌟

*VIP Benefits:*
• 25-30 Premium Signals Daily
• Early Entry (Before Public)
• 1-on-1 Support
• 89% Win Rate

💰 *Price:* ₹399/month

👇 *Click below to join*
"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("👑 Join VIP", url=VIP_LINK))
        keyboard.add(InlineKeyboardButton("💳 Payment Info", callback_data="payment_info"))
        keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=limit_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id, "⚠️ Daily limit reached! Join VIP for more")
        return
    
    # Show loading
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🔍 *Analyzing market... Please wait* 🔍\n\nFetching live data and generating signal...",
        parse_mode='Markdown'
    )
    
    # Get best signal
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
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=error_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        bot.answer_callback_query(call.id, "No signal currently. Try again later!")
        return
    
    # Format message
    signal_text = signal_gen.format_signal_message(signal, is_vip=False)
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 New Signal", callback_data="free_signal"))
    keyboard.add(InlineKeyboardButton("👑 Get VIP", callback_data="vip_channel"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=signal_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    
    # Increment free count
    db.increment_free_count(user_id)
    
    # Send to public channel (if configured)
    if PUBLIC_CHANNEL:
        try:
            public_msg = bot.send_message(PUBLIC_CHANNEL, signal_text, parse_mode='Markdown')
            # Store for potential deletion if SL hit
            import hashlib
            trade_id = hashlib.md5(f"{signal['pair']}_{signal['entry']}_{datetime.now()}".encode()).hexdigest()
            db.add_active_trade(trade_id, signal, public_msg.message_id, 'public')
        except Exception as e:
            logger.error(f"Error sending to public channel: {e}")
    
    bot.answer_callback_query(call.id, "📊 Signal generated!")

# --------------------- VIP CHANNEL ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "vip_channel")
def vip_channel_handler(call):
    vip_text = f"""
👑 *VIP CHANNEL* 👑

*India's Most Trusted Forex Signals Provider*

*VIP Benefits:*
• 25-30 Premium Signals Daily
• Early Entry (5-10 min before public)
• Live Market Analysis
• 1-on-1 VIP Support
• Trade Management Guidance
• 89% Win Rate Guarantee

💰 *Price:* {VIP_PRICE}

👇 *Join now for instant access*
"""
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=vip_text,
        parse_mode='Markdown',
        reply_markup=vip_menu()
    )
    bot.answer_callback_query(call.id)

# --------------------- COURSES ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "courses")
def courses_handler(call):
    courses_text = """
🎓 *KAILASH TRADING COURSES* 🎓

*📚 Forex Mastery Course* - ₹2999
• Complete forex foundation
• Technical analysis
• Risk management
• 10+ hours content

*💰 Smart Money Concepts* - ₹3999
• Institutional trading
• Order blocks
• Liquidity concepts
• Advanced strategies

*🎯 Price Action Pro* - ₹3499
• Candlestick patterns
• Supply & demand
• Entry/exit techniques
• Live examples

*👑 VIP + All Courses Bundle* - ₹9999
• Lifetime VIP signals
• All 3 courses
• Personal mentorship
• 24/7 support

💳 *Payment:* {UPI_ID}

📱 *Contact:* @ForexKailash after payment
"""
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=courses_text,
        parse_mode='Markdown',
        reply_markup=courses_menu()
    )
    bot.answer_callback_query(call.id)

# --------------------- LIVE RATES ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "live_rates")
def live_rates_handler(call):
    from market_data import MarketData
    md = MarketData()
    
    rates_text = "📈 *Live Market Rates*\n\n"
    
    for symbol in TRADING_PAIRS:
        price = md.get_live_price(symbol)
        if price:
            name = PAIR_NAMES.get(symbol, symbol)
            rates_text += f"{name}: ${price:.2f}\n"
    
    rates_text += "\n⏰ *Updated:* Just now"
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 Refresh", callback_data="live_rates"))
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=rates_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    bot.answer_callback_query(call.id)

# --------------------- PAYMENT INFO ---------------------

@bot.callback_query_handler(func=lambda call: call.data == "payment_info")
def payment_info_handler(call):
    payment_text = f"""
💳 *Payment Details*

💰 *VIP Plan:* {VIP_PRICE}
🎓 *Courses:* Starting ₹2999

*UPI Payment:*
