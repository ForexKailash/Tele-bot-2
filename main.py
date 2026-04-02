import telebot
import sqlite3
import datetime
import os
import random
import threading
import time
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from flask import Flask, request
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import our advanced modules
from analysis import generate_signal, get_live_price
from promotions import get_hype_promo

# ============================================
# HARDCODED CONFIGURATION (YOUR DETAILS)
# ============================================
BOT_TOKEN = "8653450456:AAER9w6Gjj5IWkyCs1taa01N-DdMFZqxt3E"
ADMIN_ID = 6253584826
PUBLIC_CHANNEL_ID = "-1003807818260"
PUBLIC_CHANNEL_LINK = "https://t.me/tradewithkailashh"
VIP_CHANNEL_ID = "-1003826269063"
VIP_CHANNEL_LINK = "https://t.me/+Snj0BVAwjDo3NTA1"
FREE_CHANNEL = PUBLIC_CHANNEL_LINK
WEBSITE_URL = "https://forexkailash.netlify.app"
COURSE_URL = "https://forexkailash.netlify.app/course"
UPI_ID = "kailashbhardwaj66-2@okicici"
CONTACT_USERNAME = "@forexkailash"

WEBHOOK_URL = "https://tele-bot-2-production.up.railway.app"
PORT = int(os.environ.get("PORT", 8443))

print("=" * 60)
print("🤖 KAILASH FOREX SIGNAL BOT - ADVANCED ANALYSIS EDITION")
print(f"Admin: {CONTACT_USERNAME}")
print(f"Public channel: {PUBLIC_CHANNEL_LINK}")
print(f"VIP channel: {VIP_CHANNEL_LINK}")
print("=" * 60)

# ============================================
# HEALTH CHECK SERVER
# ============================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("HEALTH_PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# ============================================
# TRADING SYMBOLS (same as before)
# ============================================
SYMBOLS = [
    {"name": "XAU/USD", "ticker": "GC=F", "emoji": "🥇", "decimals": 2, "type": "commodity"},
    {"name": "BTC/USD", "ticker": "BTC-USD", "emoji": "₿", "decimals": 0, "type": "crypto"},
    {"name": "EUR/USD", "ticker": "EURUSD=X", "emoji": "💶", "decimals": 5, "type": "forex"},
    {"name": "USOIL", "ticker": "CL=F", "emoji": "🛢️", "decimals": 2, "type": "commodity"},
    {"name": "GBP/USD", "ticker": "GBPUSD=X", "emoji": "💷", "decimals": 5, "type": "forex"},
    {"name": "USD/JPY", "ticker": "JPY=X", "emoji": "🇯🇵", "decimals": 3, "type": "forex"},
    {"name": "ETH/USD", "ticker": "ETH-USD", "emoji": "💎", "decimals": 1, "type": "crypto"},
    {"name": "NAS100", "ticker": "NQ=F", "emoji": "📈", "decimals": 0, "type": "index"},
    {"name": "SILVER", "ticker": "SI=F", "emoji": "🥈", "decimals": 3, "type": "commodity"},
    {"name": "AUD/USD", "ticker": "AUDUSD=X", "emoji": "🦘", "decimals": 5, "type": "forex"},
    {"name": "GBP/JPY", "ticker": "GBPJPY=X", "emoji": "⚡", "decimals": 3, "type": "forex"},
    {"name": "US30", "ticker": "YM=F", "emoji": "🏛️", "decimals": 0, "type": "index"},
    {"name": "USD/CAD", "ticker": "USDCAD=X", "emoji": "🍁", "decimals": 5, "type": "forex"},
]

# ============================================
# DATABASE SETUP (unchanged)
# ============================================
os.makedirs("telegram_bot", exist_ok=True)
conn = sqlite3.connect("telegram_bot/users.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT,
              register_date TEXT, is_vip INTEGER, last_promo_sent TEXT, start_date TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS registrations 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT,
              email TEXT, phone TEXT, date TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS signal_usage 
             (user_id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)""")
c.execute("""CREATE TABLE IF NOT EXISTS channel_signals 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, direction TEXT,
              entry REAL, tp1 REAL, tp2 REAL, sl REAL, decimals INTEGER,
              sent_date TEXT, sent_time TEXT, result TEXT DEFAULT "pending",
              message_id INTEGER DEFAULT NULL, ticker TEXT,
              channel_type TEXT DEFAULT "public", accuracy INTEGER DEFAULT 85,
              timeframe TEXT, reason TEXT, holding TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS bot_settings 
             (key TEXT PRIMARY KEY, value TEXT)""")
conn.commit()

def get_setting(key, default=None):
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone()
    return row[0] if row else default

def set_setting(key, value):
    c.execute("INSERT INTO bot_settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?", (key, value, value))
    conn.commit()

if not get_setting("vip_channel_id"):
    set_setting("vip_channel_id", VIP_CHANNEL_ID)

FREE_SIGNAL_LIMIT = 3

def get_signal_count(user_id):
    c.execute("SELECT count FROM signal_usage WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row[0] if row else 0

def increment_signal_count(user_id):
    c.execute("INSERT INTO signal_usage (user_id, count) VALUES (?, 1) ON CONFLICT(user_id) DO UPDATE SET count = count + 1", (user_id,))
    conn.commit()

def signals_remaining(user_id):
    return max(0, FREE_SIGNAL_LIMIT - get_signal_count(user_id))

# ============================================
# INITIALIZE TELEGRAM BOT
# ============================================
bot = telebot.TeleBot(BOT_TOKEN)
print(f"✅ Bot connected: @{bot.get_me().username}")

def save_signal_to_db(data, channel_type="public"):
    now = datetime.datetime.now()
    entry_avg = (data["entry_low"] + data["entry_high"]) / 2
    c.execute("""INSERT INTO channel_signals 
                 (symbol, direction, entry, tp1, tp2, sl, decimals, sent_date, sent_time, ticker, channel_type, accuracy, timeframe, reason, holding)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (data["symbol"], data["direction"], entry_avg,
               data["tp1"], data["tp2"], data["sl"], data["decimals"],
               now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), data["ticker"], channel_type,
               data.get("accuracy", 85), "Multi-timeframe", data.get("analysis", ""), data.get("holding", "short")))
    conn.commit()
    return c.lastrowid

def update_signal_message_id(signal_id, message_id):
    c.execute("UPDATE channel_signals SET message_id=? WHERE id=?", (message_id, signal_id))
    conn.commit()

def update_signal_result(signal_id, result):
    c.execute("UPDATE channel_signals SET result=? WHERE id=?", (result, signal_id))
    conn.commit()

def get_pending_signals():
    c.execute("""SELECT id, symbol, direction, entry, tp1, tp2, sl, decimals, message_id, ticker, result, channel_type, accuracy
                 FROM channel_signals WHERE result='pending' AND message_id IS NOT NULL""")
    return c.fetchall()

IST_OFFSET = datetime.timedelta(hours=5, minutes=30)
def get_ist_time():
    return datetime.datetime.utcnow() + IST_OFFSET

# ============================================
# SIGNAL TEMPLATES (using new analysis)
# ============================================
def public_signal_post(d):
    ist = get_ist_time()
    dir_word = "🟢 BUY" if d["direction"] == "BUY" else "🔴 SELL"
    dec = d["decimals"]
    tp1_str = f"{d['tp1']:.{dec}f}" if dec > 0 else str(int(d["tp1"]))
    tp2_str = f"{d['tp2']:.{dec}f}" if dec > 0 else str(int(d["tp2"]))
    sl_str = f"{d['sl']:.{dec}f}" if dec > 0 else str(int(d["sl"]))
    entry_low_str = f"{d['entry_low']:.{dec}f}" if dec > 0 else str(int(d["entry_low"]))
    entry_high_str = f"{d['entry_high']:.{dec}f}" if dec > 0 else str(int(d["entry_high"]))
    return f"""🔥🔥🔥 *LIVE SIGNAL ALERT* 🔥🔥🔥

{d['emoji']} *{d['symbol']}* {dir_word}
━━━━━━━━━━━━━━━━━━━━━━━━
📌 *Entry Zone:* `{entry_low_str} — {entry_high_str}`
🎯 *TP 1:* `{tp1_str}` ✅
🎯 *TP 2:* `{tp2_str}` ✅✅
🛑 *Stop Loss:* `{sl_str}`

📊 *Analysis:* {d['analysis']}
⏰ *Holding Period:* {d['holding_text']}
📈 *Confidence:* {d['confidence']}%

🕐 {ist.strftime('%d %b %Y • %I:%M %p')} IST
━━━━━━━━━━━━━━━━━━━━━━━━
💎 *Win Rate Target: {d['confidence']}%* | Risk: 1-2%
⭐ VIP gets signals *30 mins early!*
👇 *Upgrade to VIP — ₹399/month*
{VIP_CHANNEL_LINK}"""

def vip_signal_post(d):
    ist = get_ist_time()
    dir_word = "BUY 🟢" if d["direction"] == "BUY" else "SELL 🔴"
    dec = d["decimals"]
    tp1_str = f"{d['tp1']:.{dec}f}" if dec > 0 else str(int(d["tp1"]))
    tp2_str = f"{d['tp2']:.{dec}f}" if dec > 0 else str(int(d["tp2"]))
    sl_str = f"{d['sl']:.{dec}f}" if dec > 0 else str(int(d["sl"]))
    entry_low_str = f"{d['entry_low']:.{dec}f}" if dec > 0 else str(int(d["entry_low"]))
    entry_high_str = f"{d['entry_high']:.{dec}f}" if dec > 0 else str(int(d["entry_high"]))
    return f"""⭐ *VIP EXCLUSIVE SIGNAL* ⭐
━━━━━━━━━━━━━━━━━━━━━━━
{d['emoji']} *{d['symbol']}* | {dir_word}
━━━━━━━━━━━━━━━━━━━━━━━
📍 *Entry Zone:* `{entry_low_str} — {entry_high_str}`
🎯 *TP1:* `{tp1_str}`
🎯 *TP2:* `{tp2_str}`
⛔ *SL:* `{sl_str}`

📊 *Analysis:* {d['analysis']}
⏰ *Holding Period:* {d['holding_text']}
📈 *Confidence:* {d['confidence']}%

🕐 {ist.strftime('%H:%M')} IST
🔒 *VIP Only*
━━━━━━━━━━━━━━━━━━━━━━━
🔥 Next signal in 10-15 mins!"""

def build_public_signal():
    symbol = random.choice(SYMBOLS)
    d = generate_signal(symbol)   # uses advanced analysis from analysis.py
    sid = save_signal_to_db(d, "public")
    return public_signal_post(d), sid

def build_vip_signal(symbol=None):
    if symbol is None:
        symbol = random.choice(SYMBOLS)
    d = generate_signal(symbol)
    sid = save_signal_to_db(d, "vip")
    return vip_signal_post(d), sid

# ============================================
# PROMOTIONS (using hype messages)
# ============================================
def get_random_promo():
    return get_hype_promo(PUBLIC_CHANNEL_LINK, VIP_CHANNEL_LINK, CONTACT_USERNAME, UPI_ID, COURSE_URL)

def send_promo_to_all_users():
    while True:
        try:
            c.execute("SELECT user_id FROM users")
            users = c.fetchall()
            for (uid,) in users:
                try:
                    bot.send_message(uid, get_random_promo(), parse_mode="Markdown")
                    time.sleep(0.5)
                except:
                    pass
            print(f"✅ Promos sent to {len(users)} users at {get_ist_time().strftime('%H:%M')}")
        except Exception as e:
            print(f"Promo error: {e}")
        time.sleep(1800)

# ============================================
# PRICE MONITOR (TP/SL HIT DETECTION) - improved hype
# ============================================
TP_HYPE = [
    "🎯🔥 *TARGET HIT!* 🔥🎯\n\n{symbol} {direction} → *{tp} ✅ REACHED!*\n\n+{profit} {unit} profit!\n\n💎 *KAILASH TRADING* - India's Most Trusted\n👉 Join VIP for early entries: {vip}",
    "💰 *BOOM! TP HIT!* 💰\n\n{symbol} → *{tp} SMASHED!* 🎯\n*{direction} +{profit} {unit}*\n⭐ *Win Rate {accuracy}%* | VIP: {vip}",
    "🏆 *PROFIT BOOKED!* 🏆\n\n{symbol} {direction} → {tp} achieved! +{profit} {unit}\n\nThis is why {accuracy}% of our trades win.\n👉 Upgrade to VIP: {vip}",
]

def price_monitor():
    while True:
        time.sleep(180)  # every 3 minutes
        try:
            pending = get_pending_signals()
            for row in pending:
                (sig_id, symbol, direction, entry, tp1, tp2, sl, decimals,
                 msg_id, ticker, result, ch_type, accuracy) = row
                current = get_live_price(ticker)  # from analysis.py
                if current is None:
                    continue
                is_vip = (ch_type == "vip")
                hit = None
                label = None
                if direction == "BUY":
                    if current >= tp2:
                        hit, label = tp2, "TP2 🎯🎯"
                    elif current >= tp1:
                        hit, label = tp1, "TP1 🎯"
                    elif current <= sl:
                        if not is_vip:
                            try:
                                bot.delete_message(PUBLIC_CHANNEL_ID, msg_id)
                            except:
                                pass
                        update_signal_result(sig_id, "sl_hit")
                        continue
                else:  # SELL
                    if current <= tp2:
                        hit, label = tp2, "TP2 🎯🎯"
                    elif current <= tp1:
                        hit, label = tp1, "TP1 🎯"
                    elif current >= sl:
                        if not is_vip:
                            try:
                                bot.delete_message(PUBLIC_CHANNEL_ID, msg_id)
                            except:
                                pass
                        update_signal_result(sig_id, "sl_hit")
                        continue
                if hit:
                    if decimals == 5:
                        profit = round(abs(hit - entry) * 10000, 1)
                        unit = "pips"
                    elif decimals == 0:
                        profit = round(abs(hit - entry), 0)
                        unit = "points"
                    else:
                        profit = round(abs(hit - entry), 2)
                        unit = "points"
                    hype = random.choice(TP_HYPE).format(
                        symbol=symbol, direction=direction, tp=label,
                        profit=profit, unit=unit, vip=VIP_CHANNEL_LINK, accuracy=accuracy
                    )
                    try:
                        bot.send_message(PUBLIC_CHANNEL_ID, hype, parse_mode="Markdown")
                        if is_vip and VIP_CHANNEL_ID:
                            bot.send_message(VIP_CHANNEL_ID, f"🏆 *VIP PROFIT!* {symbol} {direction} {label} +{profit} {unit}", parse_mode="Markdown")
                        update_signal_result(sig_id, "tp_hit")
                    except Exception as e:
                        print(f"TP message error: {e}")
        except Exception as e:
            print(f"Price monitor error: {e}")

# ============================================
# VIP CHANNEL SCHEDULER
# ============================================
def vip_channel_scheduler():
    vip_signal_count = 0
    last_date = ""
    promo_counter = 0
    while True:
        if not VIP_CHANNEL_ID:
            time.sleep(60)
            continue
        try:
            ist = get_ist_time()
            today = ist.strftime("%Y-%m-%d")
            if today != last_date:
                vip_signal_count = 0
                last_date = today
                promo_counter = 0
            if vip_signal_count < 35:
                sym = random.choice(SYMBOLS)
                text, sid = build_vip_signal(sym)
                sent = bot.send_message(VIP_CHANNEL_ID, text, parse_mode="Markdown")
                update_signal_message_id(sid, sent.message_id)
                vip_signal_count += 1
                print(f"VIP signal #{vip_signal_count} sent")
            else:
                promo_counter += 1
                if promo_counter % 2 == 0:
                    promo = f"🎓 *KAILASH FOREX MASTERCLASS* - VIP Special ₹1,499 only! DM {CONTACT_USERNAME}\n🌐 {COURSE_URL}"
                    bot.send_message(VIP_CHANNEL_ID, promo, parse_mode="Markdown")
        except Exception as e:
            print(f"VIP scheduler error: {e}")
        time.sleep(random.randint(600, 900))

# ============================================
# PUBLIC CHANNEL SCHEDULER
# ============================================
public_signal_count = 0
last_pub_date = ""
post_counter = 0

def public_scheduler():
    global public_signal_count, last_pub_date, post_counter
    while True:
        try:
            ist = get_ist_time()
            today = ist.strftime("%Y-%m-%d")
            if today != last_pub_date:
                public_signal_count = 0
                last_pub_date = today
                print(f"New day: {today}")
            post_counter += 1
            if post_counter % 2 == 0:
                if public_signal_count < 8:
                    text, sid = build_public_signal()
                    sent = bot.send_message(PUBLIC_CHANNEL_ID, text, parse_mode="Markdown")
                    update_signal_message_id(sid, sent.message_id)
                    public_signal_count += 1
                    print(f"Public signal #{public_signal_count} posted")
                else:
                    bot.send_message(PUBLIC_CHANNEL_ID, get_random_promo(), parse_mode="Markdown")
            else:
                bot.send_message(PUBLIC_CHANNEL_ID, get_random_promo(), parse_mode="Markdown")
        except Exception as e:
            print(f"Public scheduler error: {e}")
        time.sleep(1800)

# ============================================
# TELEGRAM BOT COMMANDS (unchanged)
# ============================================
def main_keyboard():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(telebot.types.InlineKeyboardButton("📝 Register", callback_data="register"))
    kb.add(telebot.types.InlineKeyboardButton("📊 Free Signal", callback_data="free"))
    kb.add(telebot.types.InlineKeyboardButton("⭐ VIP Access", callback_data="vip"))
    kb.add(telebot.types.InlineKeyboardButton("💬 Support", callback_data="support"))
    kb.add(telebot.types.InlineKeyboardButton("🌐 Website", url=WEBSITE_URL))
    kb.add(telebot.types.InlineKeyboardButton("📢 Free Channel", url=PUBLIC_CHANNEL_LINK))
    return kb

@bot.message_handler(commands=["start"])
def start_cmd(msg):
    uid = msg.from_user.id
    c.execute("SELECT user_id FROM users WHERE user_id=?", (uid,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, email, phone, register_date, is_vip, last_promo_sent, start_date) VALUES (?,?,?,?,?,?,?,?)",
                  (uid, msg.from_user.first_name or "User", "", "", str(datetime.datetime.now()), 0, str(datetime.datetime.now()), str(datetime.datetime.now())))
        conn.commit()
    txt = f"""🚀 *Forex Trading With Kailash* 🚀

India's Most Trusted Forex Signals Provider

📊 *Services:*
✅ FREE Signals - Daily 8-10 calls (Real Analysis)
⭐ VIP Channel - ₹399/month (30-35 calls)
🔄 Copy Trading Available
📈 89% Win Rate | 5000+ Traders

🌐 *Website:* {WEBSITE_URL}
📢 *Free Channel:* {PUBLIC_CHANNEL_LINK}
⭐ *VIP Channel:* {VIP_CHANNEL_LINK}

👇 *Choose an option:*"""
    bot.reply_to(msg, txt, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(commands=["register"])
def reg_cmd(msg):
    m = bot.reply_to(msg, "📝 *Send:* `Name, Email, Phone`\nExample: `Rajesh, rajesh@gmail.com, 9876543210`", parse_mode="Markdown")
    bot.register_next_step_handler(m, save_user)

def save_user(msg):
    uid = msg.from_user.id
    uname = msg.from_user.username or "No username"
    try:
        data = msg.text.split(",")
        name = data[0].strip()
        email = data[1].strip()
        phone = data[2].strip()
        c.execute("UPDATE users SET name=?, email=?, phone=?, register_date=? WHERE user_id=?", (name, email, phone, str(datetime.datetime.now()), uid))
        c.execute("INSERT INTO registrations (user_id, name, email, phone, date) VALUES (?,?,?,?,?)", (uid, name, email, phone, str(datetime.datetime.now())))
        conn.commit()
        bot.send_message(ADMIN_ID, f"🔔 New registration: {name} (@{uname})")
        bot.reply_to(msg, f"✅ Welcome {name}! Use /free for signals.", parse_mode="Markdown", reply_markup=main_keyboard())
    except:
        bot.reply_to(msg, "❌ Invalid format. Send: `Name, Email, Phone`", parse_mode="Markdown")

@bot.message_handler(commands=["free"])
def free_cmd(msg):
    uid = msg.from_user.id
    rem = signals_remaining(uid)
    if rem <= 0:
        bot.reply_to(msg, f"🚫 Free limit reached. Join VIP: /vip", parse_mode="Markdown")
        return
    increment_signal_count(uid)
    symbol = random.choice(SYMBOLS)
    d = generate_signal(symbol)
    dec = d["decimals"]
    tp1_str = f"{d['tp1']:.{dec}f}" if dec > 0 else str(int(d["tp1"]))
    tp2_str = f"{d['tp2']:.{dec}f}" if dec > 0 else str(int(d["tp2"]))
    sl_str = f"{d['sl']:.{dec}f}" if dec > 0 else str(int(d["sl"]))
    entry_low_str = f"{d['entry_low']:.{dec}f}" if dec > 0 else str(int(d["entry_low"]))
    entry_high_str = f"{d['entry_high']:.{dec}f}" if dec > 0 else str(int(d["entry_high"]))
    sig = f"""📊 *FREE SIGNAL* 📊
{d['emoji']} *{d['direction']} {d['symbol']}*
📌 Entry: `{entry_low_str} - {entry_high_str}`
🎯 TP1: `{tp1_str}`
🎯 TP2: `{tp2_str}`
🛑 SL: `{sl_str}`
📈 *Analysis:* {d['analysis']}
⏰ *Hold:* {d['holding_text']} | Confidence: {d['confidence']}%"""
    bot.reply_to(msg, sig, parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(commands=["vip"])
def vip_cmd(msg):
    bot.reply_to(msg, f"⭐ *VIP ACCESS* - ₹399/month\n📱 UPI: `{UPI_ID}`\nPay & send screenshot to {CONTACT_USERNAME}\n🔗 {VIP_CHANNEL_LINK}", parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(commands=["support"])
def support_cmd(msg):
    bot.reply_to(msg, f"💬 {CONTACT_USERNAME}\n📧 btcuscoinbase@gmail.com", parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(commands=["website"])
def web_cmd(msg):
    bot.reply_to(msg, f"🌐 {WEBSITE_URL}", parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(commands=["stats"])
def stats_cmd(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    bot.reply_to(msg, f"📊 Total users: {total}", parse_mode="Markdown")

@bot.message_handler(commands=["setvipid"])
def set_vip(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.reply_to(msg, "VIP ID is hardcoded. No need to set.", parse_mode="Markdown")

@bot.message_handler(commands=["vipstatus"])
def vip_status(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.reply_to(msg, f"✅ VIP channel ID: `{VIP_CHANNEL_ID}`\n📡 Scheduler active", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "register":
        m = bot.send_message(call.message.chat.id, "📝 Send: `Name, Email, Phone`", parse_mode="Markdown")
        bot.register_next_step_handler(m, save_user)
    elif call.data == "free":
        free_cmd(call.message)
    elif call.data == "vip":
        vip_cmd(call.message)
    elif call.data == "support":
        support_cmd(call.message)
    bot.answer_callback_query(call.id)

# ============================================
# FLASK WEBHOOK SERVER
# ============================================
flask_app = Flask(__name__)

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Bad Request", 400

@flask_app.route("/")
def index():
    return "Telegram Bot is running", 200

def set_webhook():
    try:
        bot.remove_webhook()
        time.sleep(1)
        webhook_url = f"{WEBHOOK_URL}/webhook"
        bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook set to {webhook_url}")
        return True
    except Exception as e:
        print(f"❌ Failed to set webhook: {e}")
        return False

# ============================================
# MAIN ENTRY POINT
# ============================================
if __name__ == "__main__":
    print("Starting background threads...")
    threading.Thread(target=public_scheduler, daemon=True).start()
    threading.Thread(target=price_monitor, daemon=True).start()
    threading.Thread(target=vip_channel_scheduler, daemon=True).start()
    threading.Thread(target=send_promo_to_all_users, daemon=True).start()
    
    if set_webhook():
        print(f"🚀 Starting Flask webhook server on port {PORT}")
        flask_app.run(host="0.0.0.0", port=PORT)
    else:
        print("⚠️ Webhook failed, falling back to long polling")
        while True:
            try:
                bot.remove_webhook()
                bot.infinity_polling(timeout=60, long_polling_timeout=60)
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(15)
