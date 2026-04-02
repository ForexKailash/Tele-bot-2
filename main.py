import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import threading
import time
import json
import logging
import random
import hashlib

from signals import SignalGenerator
from market_data import MarketData

# === YOUR CONFIGURATION (ALL FILLED) ===
BOT_TOKEN = "8653450456:AAER9w6Gjj5IWkyCs1taa01N-DdMFZqxt3E"
ADMIN_ID = 6253584826
WEBSITE_URL = "https://forexkailash.netlify.app"
UPI_ID = "kailashbhardwaj66-2@okicici"
VIP_PRICE = "₹399/month"
VIP_LINK = "https://t.me/+Snj0BVAwjDo3NTA1"
FREE_CHANNEL_LINK = "https://t.me/tradewithkailashh"

# Channel IDs (negative numbers as required by Telegram)
PUBLIC_CHANNEL = -1003807818260
VIP_CHANNEL = -1003826269063
# =======================================

# === INITIALISE ===
bot = telebot.TeleBot(BOT_TOKEN)
signal_gen = SignalGenerator()
md = MarketData()

# === DATA STORAGE ===
user_data = {}
free_signal_count = {}
vip_users = {}
active_trades = {}

for fname, var in [('user_data.json', user_data), ('free_count.json', free_signal_count),
                   ('vip_users.json', vip_users), ('active_trades.json', active_trades)]:
    try:
        with open(fname, 'r') as f:
            var.update(json.load(f))
    except:
        pass

def save_data():
    with open('user_data.json', 'w') as f:
        json.dump(user_data, f)
    with open('free_count.json', 'w') as f:
        json.dump(free_signal_count, f)
    with open('vip_users.json', 'w') as f:
        json.dump(vip_users, f)
    with open('active_trades.json', 'w') as f:
        json.dump(active_trades, f)

# === KEYBOARDS ===
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Free Signal", callback_data="free_signal"),
        InlineKeyboardButton("👑 VIP Channel", callback_data="vip_channel"),
        InlineKeyboardButton("📢 Free Channel", callback_data="free_channel"),
        InlineKeyboardButton("📈 Live Rates", callback_data="live_rates"),
        InlineKeyboardButton("🎓 Courses", callback_data="courses"),
        InlineKeyboardButton("🌐 Website", callback_data="website"),
        InlineKeyboardButton("📞 Support", callback_data="support")
    )
    return kb

def vip_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("👑 Join VIP", url=VIP_LINK),
        InlineKeyboardButton("💳 Payment Info", callback_data="payment_info"),
        InlineKeyboardButton("🎓 Courses", callback_data="courses"),
        InlineKeyboardButton("🔙 Back", callback_data="back_menu")
    )
    return kb

def courses_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📚 Forex Mastery", callback_data="course_forex"),
        InlineKeyboardButton("💰 Smart Money", callback_data="course_smc"),
        InlineKeyboardButton("🎯 Price Action", callback_data="course_pa"),
        InlineKeyboardButton("✨ VIP + Bundle", callback_data="course_bundle"),
        InlineKeyboardButton("🔙 Back", callback_data="back_menu")
    )
    return kb

def payment_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("✅ Verify Payment", callback_data="verify_payment"),
        InlineKeyboardButton("🔙 Back", callback_data="vip_channel")
    )
    return kb

# === HANDLERS ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    uid = str(message.from_user.id)
    if uid not in user_data:
        user_data[uid] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username,
            "joined": datetime.now().isoformat()
        }
        save_data()
    if uid not in free_signal_count:
        free_signal_count[uid] = 0
        save_data()

    text = f"""
🌟 *Welcome {message.from_user.first_name}!* 🌟

*📈 Forex Trading With Kailash*
India's Most Trusted Forex Signals Provider | 5000+ Happy Traders

*📊 Stats:*
🎯 Win Rate: 89%
👥 Active Traders: 5000+
⏰ Support: 24/7

*Channel Signals:*
👑 VIP: 25-30 Premium Signals/Day
📊 Public: 8-10 Free Signals/Day

*Choose an option:* 👇
"""
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "free_channel")
def free_channel_cb(call):
    txt = f"📢 *Join our Free Channel for regular signals!*\n\n🔗 {FREE_CHANNEL_LINK}"
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔗 Join Free Channel", url=FREE_CHANNEL_LINK),
           InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=kb)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "free_signal")
def free_signal_cb(call):
    uid = str(call.from_user.id)
    if free_signal_count.get(uid, 0) >= 3:
        txt = "⚠️ *Free Signal Limit Reached*\n\nJoin VIP for unlimited signals!\n💰 ₹399/month"
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("👑 Join VIP", url=VIP_LINK),
               InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=kb)
        return

    bot.edit_message_text("🔍 *Analyzing live market data...*",
                         call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    sig = signal_gen.get_best_signal(signal_type="public")
    if not sig:
        txt = "❌ No signal available right now. Try again later."
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("🔄 Try Again", callback_data="free_signal"),
               InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=kb)
        return

    msg = signal_gen.format_public_signal(sig)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔄 New Signal", callback_data="free_signal"),
           InlineKeyboardButton("👑 Get VIP", callback_data="vip_channel"),
           InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=kb)

    free_signal_count[uid] = free_signal_count.get(uid, 0) + 1
    save_data()
    bot.answer_callback_query(call.id, f"Signal {free_signal_count[uid]}/3 used")

@bot.callback_query_handler(func=lambda call: call.data == "vip_channel")
def vip_cb(call):
    txt = f"""
👑 *VIP CHANNEL* 👑

• 25-30 Premium Signals/Day
• Early Entry (5-10 min before public)
• Live Market Analysis
• 1-on-1 Support
• 89% Win Rate

💰 *Price:* {VIP_PRICE}
🎓 *Bundle:* ₹9999 (VIP + All Courses)

👇 Join now
"""
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=vip_menu())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "courses")
def courses_cb(call):
    txt = """
🎓 *KAILASH TRADING COURSES* 🎓

📚 *Forex Mastery* - ₹2999
💰 *Smart Money Concepts* - ₹3999
🎯 *Price Action Pro* - ₹3499
✨ *VIP + ALL COURSES BUNDLE* - ₹9999

💳 UPI: kailashbhardwaj66-2@okicici
"""
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=courses_menu())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
def course_detail(call):
    courses = {
        "course_forex": {"name": "Forex Mastery", "price": "₹2999",
                         "desc": "Complete forex foundation, technical analysis, risk management, 10+ hours."},
        "course_smc": {"name": "Smart Money Concepts", "price": "₹3999",
                       "desc": "Institutional trading, order blocks, liquidity, advanced strategies."},
        "course_pa": {"name": "Price Action Pro", "price": "₹3499",
                      "desc": "Candlestick patterns, supply/demand, entry/exit mastery."},
        "course_bundle": {"name": "VIP + All Courses Bundle", "price": "₹9999",
                          "desc": "Lifetime VIP signals + all 3 courses + personal mentorship."}
    }
    c = courses.get(call.data)
    if c:
        txt = f"""
🎓 *{c['name']}* 🎓

💰 *Price:* {c['price']}

📘 *Details:* {c['desc']}

*How to Enroll:*
1️⃣ Pay to: `kailashbhardwaj66-2@okicici`
2️⃣ Send screenshot to @ForexKailash
3️⃣ Get instant access
"""
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💳 Pay Now", callback_data="payment_info"),
               InlineKeyboardButton("🔙 Back", callback_data="courses"))
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                             parse_mode='Markdown', reply_markup=kb)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "payment_info")
def payment_info_cb(call):
    txt = f"""
💳 *Payment Details*

*VIP Plan:* {VIP_PRICE}
*Courses:* ₹2999–₹3999
*Bundle:* ₹9999

*UPI:* `{UPI_ID}`

*Steps:*
1️⃣ Pay to UPI
2️⃣ Take screenshot
3️⃣ Click "Verify Payment"
4️⃣ Send screenshot to @ForexKailash

⏰ Verification: 2‑4 hours
"""
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=payment_menu())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "verify_payment")
def verify_cb(call):
    txt = "✅ Send screenshot to @ForexKailash with your username and plan."
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📱 Send", url="https://t.me/ForexKailash"),
           InlineKeyboardButton("🔙 Back", callback_data="vip_channel"))
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=kb)
    bot.send_message(ADMIN_ID, f"🔔 Payment request from {call.from_user.first_name} (ID: {call.from_user.id})")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "live_rates")
def live_rates_cb(call):
    from market_data import MarketData
    md_local = MarketData()
    pairs = {
        "XAUUSD=X": "🟡 Gold",
        "EURUSD=X": "💶 EUR/USD",
        "GBPUSD=X": "💷 GBP/USD",
        "AUDUSD=X": "🇦🇺 AUD/USD",
        "USDJPY=X": "💴 USD/JPY",
        "USDCAD=X": "🇨🇦 USD/CAD",
        "NZDUSD=X": "🇳🇿 NZD/USD",
        "BTC-USD": "₿ Bitcoin",
        "ETH-USD": "🔷 Ethereum",
        "NQ=F": "📊 NAS100",
        "CL=F": "🛢️ USOIL"
    }
    txt = "📈 *Live Market Rates*\n\n"
    for sym, name in pairs.items():
        p = md_local.get_live_price(sym)
        txt += f"{name}: ${p:.2f}\n" if p else f"{name}: 🔴 Offline\n"
    txt += f"\n⏰ Updated: {datetime.now().strftime('%H:%M:%S')} IST"
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔄 Refresh", callback_data="live_rates"),
           InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=kb)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "website")
def website_cb(call):
    txt = "🌐 *Official Website*\n\nhttps://forexkailash.netlify.app"
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🌐 Visit", url=WEBSITE_URL),
           InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=kb)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "support")
def support_cb(call):
    txt = """
📞 *Support*

👤 Admin: @ForexKailash
⏰ Hours: 9 AM – 9 PM IST

*FAQ:*
- VIP: ₹399/month → Pay → Verify → Get Access
- Courses: Pay → Verify → Receive materials

We're here to help! 🤝
"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📱 Contact", url="https://t.me/ForexKailash"),
           InlineKeyboardButton("🔙 Back", callback_data="back_menu"))
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=kb)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_menu")
def back_cb(call):
    bot.edit_message_text("🏠 *Main Menu*", call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown', reply_markup=main_menu())
    bot.answer_callback_query(call.id)

# === REAL-TIME MONITORING LOOP ===
def monitor_trades():
    while True:
        try:
            for trade_id, trade in list(active_trades.items()):
                symbol = trade['symbol']
                current_price = md.get_live_price(symbol)
                if current_price is None:
                    continue

                # SL hit – delete from public channel
                if (trade['action'] == "BUY ✅" and current_price <= trade['sl']) or \
                   (trade['action'] == "SELL 🔻" and current_price >= trade['sl']):
                    if trade['channel_type'] == 'public':
                        try:
                            bot.delete_message(PUBLIC_CHANNEL, trade['message_id'])
                        except:
                            pass
                    del active_trades[trade_id]
                    save_data()
                    continue

                # TP1 hit – send course promotion in VIP channel
                if not trade.get('tp1_hit', False):
                    if (trade['action'] == "BUY ✅" and current_price >= trade['tp1']) or \
                       (trade['action'] == "SELL 🔻" and current_price <= trade['tp1']):
                        trade['tp1_hit'] = True
                        if trade['channel_type'] == 'vip':
                            msg = f"""
🎯 *TP1 HIT!* 🎯

✅ *{trade['pair']}*  
💰 Profit: +{trade['profit_pct']:.1f}%

━━━━━━━━━━━━━━━━━━━━━━
🎓 *Ready to master trading?*  
Enroll in our courses and get even better results!

📚 *Forex Mastery* - ₹2999  
💰 *Smart Money* - ₹3999  
🎯 *Price Action* - ₹3499  
✨ *Bundle (VIP+All Courses)* - ₹9999

💳 UPI: kailashbhardwaj66-2@okicici  
👉 Contact @ForexKailash to join

🚀 *Don't miss the next TP2!*
"""
                            try:
                                bot.send_message(VIP_CHANNEL, msg, parse_mode='Markdown')
                            except:
                                pass
                        save_data()

                # TP2 hit – congratulate and remove trade
                if not trade.get('tp2_hit', False):
                    if (trade['action'] == "BUY ✅" and current_price >= trade['tp2']) or \
                       (trade['action'] == "SELL 🔻" and current_price <= trade['tp2']):
                        trade['tp2_hit'] = True
                        if trade['channel_type'] == 'vip':
                            msg = f"""
🏆 *TP2 HIT!* 🏆

✅ *{trade['pair']}*  
💰 Profit: +{trade['profit_pct']*2:.1f}%

🎉 Congratulations! You've captured full profit.

━━━━━━━━━━━━━━━━━━━━━━
Want more winning trades?  
Join our VIP channel for 25-30 signals/day!

👉 @ForexKailash
"""
                            try:
                                bot.send_message(VIP_CHANNEL, msg, parse_mode='Markdown')
                            except:
                                pass
                        del active_trades[trade_id]
                        save_data()
                        continue

                # SL warning for VIP only
                if trade['channel_type'] == 'vip':
                    if trade['action'] == "BUY ✅":
                        dist_pct = (trade['sl'] - current_price) / trade['sl'] * 100
                        if dist_pct < 0.5 and not trade.get('sl_warning_sent', False):
                            trade['sl_warning_sent'] = True
                            msg = f"""
⚠️ *SL WARNING* ⚠️

Pair: {trade['pair']}
Price is approaching Stop Loss ({trade['sl']}).

Consider managing your risk. If you haven't already, you may want to close partial position.

🔒 *VIP members get early exit alerts!*
"""
                            try:
                                bot.send_message(VIP_CHANNEL, msg, parse_mode='Markdown')
                            except:
                                pass
                            save_data()
            time.sleep(5)
        except Exception as e:
            logging.error(f"Monitor error: {e}")
            time.sleep(5)

# === REAL-TIME SIGNAL LOOP ===
def real_time_signal_loop():
    last_vip_signal_time = 0
    last_public_signal_time = 0
    last_promo_hour = -1

    while True:
        try:
            now = datetime.now()
            # VIP signals (max 30/day)
            if signal_gen.can_send_vip_signal():
                sig = signal_gen.get_best_signal(signal_type="vip")
                if sig and (now - last_vip_signal_time).seconds >= 60:
                    msg = signal_gen.format_vip_signal(sig)
                    if VIP_CHANNEL:
                        try:
                            sent = bot.send_message(VIP_CHANNEL, msg, parse_mode='Markdown')
                            trade_id = hashlib.md5(f"{sig['pair']}_{sig['entry']}_{now}".encode()).hexdigest()
                            active_trades[trade_id] = {
                                'symbol': sig['symbol'],
                                'pair': sig['pair'],
                                'action': sig['action'],
                                'entry': sig['entry'],
                                'tp1': sig['tp1'],
                                'tp2': sig['tp2'],
                                'sl': sig['sl'],
                                'profit_pct': sig['profit_pct'],
                                'message_id': sent.message_id,
                                'channel_type': 'vip',
                                'tp1_hit': False,
                                'tp2_hit': False,
                                'sl_warning_sent': False,
                                'time': now.isoformat()
                            }
                            signal_gen.increment_vip_count()
                            save_data()
                            last_vip_signal_time = now
                            logging.info(f"VIP signal sent ({signal_gen.vip_signals_today}/30)")
                        except Exception as e:
                            logging.error(f"VIP send error: {e}")

            # Public signals (max 10/day)
            if signal_gen.can_send_public_signal():
                sig = signal_gen.get_best_signal(signal_type="public")
                if sig and (now - last_public_signal_time).seconds >= 120:
                    msg = signal_gen.format_public_signal(sig)
                    if PUBLIC_CHANNEL:
                        try:
                            sent = bot.send_message(PUBLIC_CHANNEL, msg, parse_mode='Markdown')
                            trade_id = hashlib.md5(f"{sig['pair']}_{sig['entry']}_{now}".encode()).hexdigest()
                            active_trades[trade_id] = {
                                'symbol': sig['symbol'],
                                'pair': sig['pair'],
                                'action': sig['action'],
                                'entry': sig['entry'],
                                'tp1': sig['tp1'],
                                'tp2': sig['tp2'],
                                'sl': sig['sl'],
                                'profit_pct': sig['profit_pct'],
                                 'message_id': sent.message_id,
                                'channel_type': 'public',
                                'tp1_hit': False,
                                'tp2_hit': False,
                                'sl_warning_sent': False,
                                'time': now.isoformat()
                            }
                            signal_gen.increment_public_count()
                            save_data()
                            last_public_signal_time = now
                            logging.info(f"Public signal sent ({signal_gen.public_signals_today}/10)")
                        except Exception as e:
                            logging.error(f"Public send error: {e}")

            # Promotion every 4 hours in public channel
            if PUBLIC_CHANNEL and now.hour % 4 == 0 and now.hour != last_promo_hour:
                promo = f"""
🔥 *EXCLUSIVE VIP ACCESS – LIMITED SEATS* 🔥

✨ *Upgrade to VIP & Get:*
• 25-30 Premium Signals/Day (vs 8-10 free)
• ⏰ Early Entry – 5-10 min before public
• 📊 Live Market Analysis & News
• 💬 1-on-1 VIP Support
• 🎯 89% Proven Win Rate

💰 *Only {VIP_PRICE}*  
🎓 *VIP + Course Bundle:* ₹9999 (Save ₹2999)

💳 *Pay:* `{UPI_ID}`  
📱 *Join:* @ForexKailash after payment

⏳ *Limited spots available – don't miss out!*
"""
                try:
                    bot.send_message(PUBLIC_CHANNEL, promo, parse_mode='Markdown')
                    last_promo_hour = now.hour
                    logging.info("Promotion sent")
                except Exception as e:
                    logging.error(f"Promotion send error: {e}")

            time.sleep(5)
        except Exception as e:
            logging.error(f"Signal loop error: {e}")
            time.sleep(5)

# === ADMIN COMMANDS ===
@bot.message_handler(commands=['addvip'])
def add_vip(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = message.text.split()[1]
        vip_users[uid] = {"activated": datetime.now().isoformat()}
        save_data()
        bot.reply_to(message, f"✅ VIP added for {uid}")
        try:
            bot.send_message(int(uid), f"🎉 VIP access activated! Join: {VIP_LINK}", parse_mode='Markdown')
        except:
            pass
    except:
        bot.reply_to(message, "Usage: /addvip [user_id]")

@bot.message_handler(commands=['resetfree'])
def reset_free(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = message.text.split()[1]
        free_signal_count[uid] = 0
        save_data()
        bot.reply_to(message, f"✅ Free count reset for {uid}")
    except:
        bot.reply_to(message, "Usage: /resetfree [user_id]")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = message.text.replace('/broadcast', '').strip()
    if not msg:
        bot.reply_to(message, "Usage: /broadcast [message]")
        return
    cnt = 0
    for uid in user_data:
        try:
            bot.send_message(int(uid), f"📢 *Announcement*\n\n{msg}", parse_mode='Markdown')
            cnt += 1
        except:
            pass
    bot.reply_to(message, f"✅ Sent to {cnt} users")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    txt = f"""
📊 *Bot Stats*

👥 Users: {len(user_data)}
👑 VIP: {len(vip_users)}
📊 Active: {len(user_data)}

📈 Today's signals:
👑 VIP: {signal_gen.vip_signals_today}/30
📊 Public: {signal_gen.public_signals_today}/10

💰 VIP Price: {VIP_PRICE}
"""
    bot.reply_to(message, txt, parse_mode='Markdown')

@bot.message_handler(commands=['forcesignal'])
def force_signal(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "🔍 Generating...")
    vip_sig = signal_gen.get_best_signal("vip")
    pub_sig = signal_gen.get_best_signal("public")
    if vip_sig and VIP_CHANNEL:
        sent = bot.send_message(VIP_CHANNEL, signal_gen.format_vip_signal(vip_sig), parse_mode='Markdown')
        trade_id = hashlib.md5(f"{vip_sig['pair']}_{vip_sig['entry']}_{datetime.now()}".encode()).hexdigest()
        active_trades[trade_id] = {
            'symbol': vip_sig['symbol'],
            'pair': vip_sig['pair'],
            'action': vip_sig['action'],
            'entry': vip_sig['entry'],
            'tp1': vip_sig['tp1'],
            'tp2': vip_sig['tp2'],
            'sl': vip_sig['sl'],
            'profit_pct': vip_sig['profit_pct'],
            'message_id': sent.message_id,
            'channel_type': 'vip',
            'tp1_hit': False,
            'tp2_hit': False,
            'sl_warning_sent': False,
            'time': datetime.now().isoformat()
        }
        signal_gen.increment_vip_count()
    if pub_sig and PUBLIC_CHANNEL:
        sent = bot.send_message(PUBLIC_CHANNEL, signal_gen.format_public_signal(pub_sig), parse_mode='Markdown')
        trade_id = hashlib.md5(f"{pub_sig['pair']}_{pub_sig['entry']}_{datetime.now()}".encode()).hexdigest()
        active_trades[trade_id] = {
            'symbol': pub_sig['symbol'],
            'pair': pub_sig['pair'],
            'action': pub_sig['action'],
            'entry': pub_sig['entry'],
            'tp1': pub_sig['tp1'],
            'tp2': pub_sig['tp2'],
            'sl': pub_sig['sl'],
            'profit_pct': pub_sig['profit_pct'],
            'message_id': sent.message_id,
            'channel_type': 'public',
            'tp1_hit': False,
            'tp2_hit': False,
            'sl_warning_sent': False,
            'time': datetime.now().isoformat()
        }
        signal_gen.increment_public_count()
    save_data()
    bot.reply_to(message, f"✅ VIP: {signal_gen.vip_signals_today}/30, Public: {signal_gen.public_signals_today}/10")

# === START THREADS ===
threading.Thread(target=real_time_signal_loop, daemon=True).start()
threading.Thread(target=monitor_trades, daemon=True).start()

# === MAIN ===
if __name__ == "__main__":
    print("="*70)
    print("🤖 KAILASH FOREX SIGNAL BOT – REAL-TIME EDITION")
    print("="*70)
    print("✅ VIP: 25-30 signals/day + course promos on TP")
    print("✅ Public: 8-10 signals/day + auto-delete on SL")
    print("✅ Real-time monitoring (every 5 seconds)")
    print("✅ SL warnings for VIP")
    print("✅ TP updates with course FOMO")
    print("✅ Free Channel button added")
    print("✅ Trading pairs: Gold, EUR/USD, GBP/USD, AUD/USD, USD/JPY, USD/CAD, NZD/USD, BTC, ETH, NAS100, USOIL")
    print("="*70)
    bot.infinity_polling
          
