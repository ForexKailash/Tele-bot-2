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
from http.server import HTTPServer, BaseHTTPRequestHandler

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

print("=" * 60)
print("🤖 KAILASH FOREX SIGNAL BOT - ULTIMATE EDITION")
print(f"Public channel: {PUBLIC_CHANNEL_LINK}")
print(f"VIP channel: {VIP_CHANNEL_LINK}")
print("=" * 60)

# ============================================
# HEALTH CHECK SERVER (for Railway)
# ============================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# ============================================
# TRADING SYMBOLS (13 reliable pairs)
# ============================================
SYMBOLS = [
    {"name": "XAU/USD", "ticker": "GC=F", "emoji": "🥇", "decimals": 2, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003},
    {"name": "BTC/USD", "ticker": "BTC-USD", "emoji": "₿", "decimals": 0, "tp1_pct": 0.006, "tp2_pct": 0.012, "sl_pct": 0.004},
    {"name": "EUR/USD", "ticker": "EURUSD=X", "emoji": "💶", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002},
    {"name": "USOIL", "ticker": "CL=F", "emoji": "🛢️", "decimals": 2, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003},
    {"name": "GBP/USD", "ticker": "GBPUSD=X", "emoji": "💷", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002},
    {"name": "USD/JPY", "ticker": "JPY=X", "emoji": "🇯🇵", "decimals": 3, "tp1_pct": 0.003, "tp2_pct": 0.005, "sl_pct": 0.002},
    {"name": "ETH/USD", "ticker": "ETH-USD", "emoji": "💎", "decimals": 1, "tp1_pct": 0.007, "tp2_pct": 0.014, "sl_pct": 0.005},
    {"name": "NAS100", "ticker": "NQ=F", "emoji": "📈", "decimals": 0, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003},
    {"name": "SILVER", "ticker": "SI=F", "emoji": "🥈", "decimals": 3, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003},
    {"name": "AUD/USD", "ticker": "AUDUSD=X", "emoji": "🦘", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002},
    {"name": "GBP/JPY", "ticker": "GBPJPY=X", "emoji": "⚡", "decimals": 3, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003},
    {"name": "US30", "ticker": "YM=F", "emoji": "🏛️", "decimals": 0, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002},
    {"name": "USD/CAD", "ticker": "USDCAD=X", "emoji": "🍁", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002},
]

FALLBACK_PRICES = {
    "GC=F": 4520.00, "BTC-USD": 68500.00, "EURUSD=X": 1.08750, "CL=F": 79.50,
    "GBPUSD=X": 1.26800, "JPY=X": 150.50, "ETH-USD": 3550.00, "NQ=F": 18700.00,
    "SI=F": 27.80, "AUDUSD=X": 0.65500, "GBPJPY=X": 190.80, "YM=F": 39300.00,
    "USDCAD=X": 1.36000,
}

# ============================================
# TECHNICAL ANALYSIS (SMA + RSI)
# ============================================
def get_live_price(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="5m", progress=False, timeout=5)
        if not data.empty:
            return float(data["Close"].iloc[-1])
    except:
        pass
    return FALLBACK_PRICES.get(ticker, 1000.00)

def get_sma(ticker, period=20):
    try:
        data = yf.download(ticker, period="60d", interval="1d", progress=False, timeout=8)
        if not data.empty and len(data) > period:
            sma = data["Close"].rolling(period).mean().iloc[-1]
            curr = data["Close"].iloc[-1]
            return curr, sma
    except:
        pass
    return None, None

def get_rsi(ticker, period=14):
    try:
        data = yf.download(ticker, period="60d", interval="1d", progress=False, timeout=8)
        if not data.empty and len(data) > period:
            delta = data["Close"].diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            return rsi
    except:
        pass
    return 50

def get_technical_analysis(ticker, asset_name):
    curr, sma20 = get_sma(ticker, 20)
    rsi = get_rsi(ticker, 14)
    if curr is not None and sma20 is not None:
        if curr > sma20:
            direction = "BUY"
            confidence = 70 + (10 if rsi < 30 else 0) - (5 if rsi > 70 else 0)
            confidence = min(85, max(60, confidence))
            reason = f"Price above 20-day SMA (${sma20:.2f}), uptrend. RSI: {rsi:.1f}"
        else:
            direction = "SELL"
            confidence = 70 + (10 if rsi > 70 else 0) - (5 if rsi < 30 else 0)
            confidence = min(85, max(60, confidence))
            reason = f"Price below 20-day SMA (${sma20:.2f}), downtrend. RSI: {rsi:.1f}"
        holding = "short"
        holding_text = "Short-term (1-2 days)"
        return direction, confidence, reason, holding, holding_text
    else:
        direction = random.choice(["BUY", "SELL"])
        confidence = 60
        reason = f"Fallback analysis for {asset_name} (data limited)"
        holding = "short"
        holding_text = "Short-term (1-2 days)"
        return direction, confidence, reason, holding, holding_text

def generate_signal(symbol=None):
    if symbol is None:
        symbol = random.choice(SYMBOLS)
    direction, confidence, reason, holding, holding_text = get_technical_analysis(symbol["ticker"], symbol["name"])
    price = get_live_price(symbol["ticker"])
    d = symbol["decimals"]
    spread = price * 0.0005
    if direction == "BUY":
        entry_low = round(price - spread, d)
        entry_high = round(price + spread, d)
        tp1 = round(price * (1 + symbol["tp1_pct"]), d)
        tp2 = round(price * (1 + symbol["tp2_pct"]), d)
        sl = round(price * (1 - symbol["sl_pct"]), d)
    else:
        entry_low = round(price - spread, d)
        entry_high = round(price + spread, d)
        tp1 = round(price * (1 - symbol["tp1_pct"]), d)
        tp2 = round(price * (1 - symbol["tp2_pct"]), d)
        sl = round(price * (1 + symbol["sl_pct"]), d)
    # Safety to avoid zero difference
    if tp1 == entry_low:
        tp1 = entry_low + (0.01 if d <= 2 else 0.00001)
    if tp2 == tp1:
        tp2 = tp1 + (0.02 if d <= 2 else 0.00002)
    if sl == entry_high:
        sl = entry_high - (0.01 if d <= 2 else 0.00001)
    return {
        "symbol": symbol["name"], "emoji": symbol["emoji"], "direction": direction,
        "entry_low": entry_low, "entry_high": entry_high,
        "tp1": tp1, "tp2": tp2, "sl": sl, "decimals": d,
        "analysis": reason, "confidence": confidence, "holding_text": holding_text
    }

# ============================================
# DATABASE SETUP
# ============================================
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/bot.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, start_date TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, direction TEXT, entry REAL, tp1 REAL, tp2 REAL, sl REAL, sent_date TEXT, channel TEXT, result TEXT, message_id INTEGER)")
conn.commit()

def save_signal(data, channel_type):
    now = datetime.datetime.now()
    entry_avg = (data["entry_low"] + data["entry_high"]) / 2
    c.execute("INSERT INTO signals (symbol, direction, entry, tp1, tp2, sl, sent_date, channel, result) VALUES (?,?,?,?,?,?,?,?,?)",
              (data["symbol"], data["direction"], entry_avg, data["tp1"], data["tp2"], data["sl"], now.strftime("%Y-%m-%d %H:%M:%S"), channel_type, "pending"))
    conn.commit()
    return c.lastrowid

def update_signal_result(sig_id, result, msg_id=None):
    if msg_id:
        c.execute("UPDATE signals SET result=?, message_id=? WHERE id=?", (result, msg_id, sig_id))
    else:
        c.execute("UPDATE signals SET result=? WHERE id=?", (result, sig_id))
    conn.commit()

def get_pending_signals():
    c.execute("SELECT id, symbol, direction, entry, tp1, tp2, sl, message_id, channel FROM signals WHERE result='pending' AND message_id IS NOT NULL")
    return c.fetchall()

# ============================================
# TELEGRAM BOT
# ============================================
bot = telebot.TeleBot(BOT_TOKEN)
print(f"✅ Bot connected: @{bot.get_me().username}")

# ============================================
# COMMANDS
# ============================================
@bot.message_handler(commands=['start'])
def start_cmd(msg):
    uid = msg.from_user.id
    c.execute("INSERT OR IGNORE INTO users (user_id, name, start_date) VALUES (?, ?, ?)",
              (uid, msg.from_user.first_name, str(datetime.datetime.now())))
    conn.commit()
    txt = f"""🚀 *Forex Trading With Kailash* 🚀

India's Most Trusted Forex Signals Provider

📊 *Services:*
✅ FREE Signals - Daily 8-10 calls (Real Analysis)
⭐ VIP Channel - ₹399/month (30-35 calls)
🔄 Copy Trading Available
📈 89% Win Rate | 5000+ Traders

📢 *Free Channel:* {PUBLIC_CHANNEL_LINK}
⭐ *VIP Channel:* {VIP_CHANNEL_LINK}

👇 *Commands:* /free, /vip, /register, /support, /website"""
    bot.reply_to(msg, txt, parse_mode="Markdown")
    print(f"✅ /start sent to {uid}")

@bot.message_handler(commands=['register'])
def reg_cmd(msg):
    m = bot.reply_to(msg, "📝 *Send:* `Name, Email, Phone`\nExample: `Rajesh, rajesh@gmail.com, 9876543210`", parse_mode="Markdown")
    bot.register_next_step_handler(m, save_user)

def save_user(msg):
    uid = msg.from_user.id
    uname = msg.from_user.username or "No username"
    try:
        data = msg.text.split(',')
        name = data[0].strip()
        email = data[1].strip()
        phone = data[2].strip()
        # Update user record (if exists)
        c.execute("UPDATE users SET name=? WHERE user_id=?", (name, uid))
        # Store registration separately
        c.execute("INSERT INTO registrations (user_id, name, email, phone, date) VALUES (?,?,?,?,?)",
                  (uid, name, email, phone, str(datetime.datetime.now())))
        conn.commit()
        bot.send_message(ADMIN_ID, f"🔔 New registration: {name} (@{uname})")
        bot.reply_to(msg, f"✅ Welcome {name}! Use /free for signals.", parse_mode="Markdown")
    except:
        bot.reply_to(msg, "❌ Invalid format. Send: `Name, Email, Phone`", parse_mode="Markdown")

@bot.message_handler(commands=['free'])
def free_cmd(msg):
    s = generate_signal()
    dec = s["decimals"]
    entry_str = f"{s['entry_low']:.{dec}f}" if dec > 0 else str(int(s['entry_low']))
    tp1_str = f"{s['tp1']:.{dec}f}" if dec > 0 else str(int(s['tp1']))
    tp2_str = f"{s['tp2']:.{dec}f}" if dec > 0 else str(int(s['tp2']))
    sl_str = f"{s['sl']:.{dec}f}" if dec > 0 else str(int(s['sl']))
    sig = f"""📊 *FREE SIGNAL* 📊
{s['emoji']} *{s['direction']} {s['symbol']}*
📌 Entry: `{entry_str}`
🎯 TP1: `{tp1_str}`
🎯 TP2: `{tp2_str}`
🛑 SL: `{sl_str}`
📈 *Analysis:* {s['analysis']}
⏰ *Hold:* {s['holding_text']} | Confidence: {s['confidence']}%"""
    bot.reply_to(msg, sig, parse_mode="Markdown")

@bot.message_handler(commands=['vip'])
def vip_cmd(msg):
    bot.reply_to(msg, f"⭐ *VIP ACCESS* - ₹399/month\n📱 UPI: `{UPI_ID}`\nPay & send screenshot to {CONTACT_USERNAME}\n🔗 {VIP_CHANNEL_LINK}", parse_mode="Markdown")

@bot.message_handler(commands=['support'])
def support_cmd(msg):
    bot.reply_to(msg, f"💬 {CONTACT_USERNAME}\n📧 btcuscoinbase@gmail.com", parse_mode="Markdown")

@bot.message_handler(commands=['website'])
def web_cmd(msg):
    bot.reply_to(msg, f"🌐 {WEBSITE_URL}", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_cmd(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    bot.reply_to(msg, f"📊 Total users: {total}", parse_mode="Markdown")

@bot.message_handler(commands=['vipstatus'])
def vipstatus_cmd(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.reply_to(msg, f"✅ VIP channel ID: {VIP_CHANNEL_ID}\n📡 Scheduler active", parse_mode="Markdown")

@bot.message_handler(commands=['setvipid'])
def setvip_cmd(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.reply_to(msg, "VIP ID is hardcoded, no need to set.", parse_mode="Markdown")

# ============================================
# 30+ PROMOTIONAL MESSAGES (Indian English, Hype)
# ============================================
PROMOS = [
    f"💎 *FREE SIGNALS MILTE HAIN* daily! Join free channel: {PUBLIC_CHANNEL_LINK}\n⭐ VIP me early entry + 30-35 signals/day sirf ₹399! {VIP_CHANNEL_LINK}",
    f"🚀 *Aaj hi 3 logon ne VIP join kiya aur profit book kiya!* Tum kab aa rahe ho? {VIP_CHANNEL_LINK}",
    f"📊 *Free channel me signal delay hota hai.* VIP me entry 30 min pehle milti hai. Fark dekho: {VIP_CHANNEL_LINK}",
    f"💰 *₹399/month mein kya milega?* 30-35 premium signals, early entry, 1-on-1 support. ROI 3600%+! Join: {VIP_CHANNEL_LINK}",
    f"⚠️ *Limited slots!* Sirf {random.randint(3,7)} VIP seats bachi hain. Price soon ₹599. Lock ₹399 now: {VIP_CHANNEL_LINK}",
    f"🏆 *89% win rate* - proof hai mere channel pe. Free signals dekh lo, phir VIP decide karo. Free channel: {PUBLIC_CHANNEL_LINK}",
    f"🎯 *Aaj ka GOLD signal TP2 hit!* +250 pips. VIP members ko early entry mili thi. Tum bhi lo: {VIP_CHANNEL_LINK}",
    f"📚 *FREE FOREX MASTERCLASS* - VIP members ko ₹2,999 ka course free. DM {CONTACT_USERNAME} after joining VIP.",
    f"💬 *Testimonial:* 'Joined VIP, 10x subscription fee wapas kama liya first month.' - Rahul, Mumbai. Join now: {VIP_CHANNEL_LINK}",
    f"⏰ *Price hike warning!* Next month ₹599. Abhi ₹399 mein lock karo lifetime: {VIP_CHANNEL_LINK}",
    f"🔥 *Copy trading available* - Mere trades automatically copy karo. VIP members ke liye. Join: {VIP_CHANNEL_LINK}",
    f"📈 *Daily 8-10 free signals* milte hain free channel pe. Par early entry sirf VIP ko. Dono join karo: {PUBLIC_CHANNEL_LINK} | {VIP_CHANNEL_LINK}",
    f"💎 *Kailash sir khud dete hain signals* - 7+ years experience. Trusted by 5000+ traders. VIP link: {VIP_CHANNEL_LINK}",
    f"🎁 *Special offer:* Pehle 10 VIP members ko free course. Hurry up! {VIP_CHANNEL_LINK}",
    f"📊 *Free vs VIP difference:* Free = delayed entry, 3-5 signals. VIP = early entry, 30-35 signals. Choose wisely: {VIP_CHANNEL_LINK}",
    f"💸 *Kal ka profit:* VIP members ne ₹8,000+ banaye sirf 2 trades se. Miss mat karo: {VIP_CHANNEL_LINK}",
    f"🚨 *BREAKING:* Gold breakout coming. VIP ko 30 min pehle pata chalega. Join fast: {VIP_CHANNEL_LINK}",
    f"🎓 *Course + Signals combo* - VIP special ₹1,499 only (50% off). DM {CONTACT_USERNAME} for details.",
    f"💬 *FAQ:* UPI payment accept hai. Pay ₹399 to {UPI_ID}, screenshot bhejo, channel link milega. Simple!",
    f"🌟 *Trusted by 5000+ Indian traders.* Aao tum bhi team mein: {VIP_CHANNEL_LINK}",
    f"📱 *Telegram par 24/7 support* - VIP members ko priority response. Join: {VIP_CHANNEL_LINK}",
    f"⚡ *Momentum trade alert* - 4H timeframe pe setup bana hai. VIP ko pehle milega. {VIP_CHANNEL_LINK}",
    f"💎 *Gold, Crypto, Forex, Indices* - sab pe signals. Ek baar VIP try karo: {VIP_CHANNEL_LINK}",
    f"🎯 *Today's target:* 3 VIP signals already in profit. Join abhi: {VIP_CHANNEL_LINK}",
    f"📢 *FREE channel join karo* - daily 8-10 signals. Phir VIP upgrade karna easy rahega: {PUBLIC_CHANNEL_LINK}",
    f"💡 *Risk management sikhoge* VIP me. Kailash sir guide karte hain. ₹399 only: {VIP_CHANNEL_LINK}",
    f"🏆 *Kaun banega crorepati?* Mere VIP members consistently profitable hain. Tum bano: {VIP_CHANNEL_LINK}",
    f"🔄 *Auto copy-trade setup help* - VIP members ko free. DM {CONTACT_USERNAME} after joining.",
    f"📊 *Weekly review:* VIP members ka average profit this week ₹12,000. Miss mat karo: {VIP_CHANNEL_LINK}",
    f"⏳ *Last chance* - Sirf {random.randint(2,5)} seats left at ₹399. Next price ₹599. {VIP_CHANNEL_LINK}",
    f"🎓 *Want to learn trading?* Course + Signals combo best hai. DM {CONTACT_USERNAME} for offer.",
    f"💎 *Kailash Forex Masterclass* - Limited time 50% off for VIP. Enroll: {COURSE_URL}",
]

def get_promo():
    return random.choice(PROMOS)

# ============================================
# USER PROMO THREAD (every 30 min, rate limited)
# ============================================
def send_promos():
    while True:
        try:
            c.execute("SELECT user_id FROM users")
            users = c.fetchall()
            for (uid,) in users:
                try:
                    bot.send_message(uid, get_promo(), parse_mode="Markdown")
                    time.sleep(0.5)  # avoid rate limit
                except Exception as e:
                    print(f"Promo fail {uid}: {e}")
            print(f"✅ Promos sent to {len(users)} users")
        except Exception as e:
            print(f"Promo thread error: {e}")
        time.sleep(1800)

# ============================================
# PUBLIC CHANNEL SCHEDULER (8-10 signals/day + promos)
# ============================================
public_count = 0
public_last_date = ""

def public_scheduler():
    global public_count, public_last_date
    while True:
        try:
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
            today = now.strftime("%Y-%m-%d")
            if today != public_last_date:
                public_count = 0
                public_last_date = today
                print(f"New day for public channel: {today}")
            if public_count < 8:
                s = generate_signal()
                dec = s["decimals"]
                entry_low_str = f"{s['entry_low']:.{dec}f}" if dec > 0 else str(int(s['entry_low']))
                entry_high_str = f"{s['entry_high']:.{dec}f}" if dec > 0 else str(int(s['entry_high']))
                tp1_str = f"{s['tp1']:.{dec}f}" if dec > 0 else str(int(s['tp1']))
                tp2_str = f"{s['tp2']:.{dec}f}" if dec > 0 else str(int(s['tp2']))
                sl_str = f"{s['sl']:.{dec}f}" if dec > 0 else str(int(s['sl']))
                msg = f"""🔥🔥🔥 *LIVE SIGNAL ALERT* 🔥🔥🔥

{s['emoji']} *{s['direction']} {s['symbol']}*
━━━━━━━━━━━━━━━━━━━━━━━━
📌 *Entry Zone:* `{entry_low_str} — {entry_high_str}`
🎯 *TP 1:* `{tp1_str}` ✅
🎯 *TP 2:* `{tp2_str}` ✅✅
🛑 *Stop Loss:* `{sl_str}`

📊 *Analysis:* {s['analysis']}
⏰ *Holding Period:* {s['holding_text']}
📈 *Confidence:* {s['confidence']}%

🕐 {now.strftime('%d %b %Y • %I:%M %p')} IST
━━━━━━━━━━━━━━━━━━━━━━━━
💎 *Win Rate Target: {s['confidence']}%* | Risk: 1-2%
⭐ VIP gets signals *30 mins early!*
👇 *Upgrade to VIP — ₹399/month*
{VIP_CHANNEL_LINK}"""
                sent = bot.send_message(PUBLIC_CHANNEL_ID, msg, parse_mode="Markdown")
                # Save signal for monitoring
                sig_id = save_signal(s, "public")
                update_signal_result(sig_id, "pending", sent.message_id)
                public_count += 1
                print(f"📢 Public signal #{public_count} sent")
            else:
                bot.send_message(PUBLIC_CHANNEL_ID, get_promo(), parse_mode="Markdown")
                print("📣 Promo sent to public channel (daily limit)")
        except Exception as e:
            print(f"Public scheduler error: {e}")
        time.sleep(1800)

# ============================================
# VIP CHANNEL SCHEDULER (30-35 signals/day + course promos)
# ============================================
vip_count = 0
vip_last_date = ""

def vip_scheduler():
    global vip_count, vip_last_date
    while True:
        try:
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
            today = now.strftime("%Y-%m-%d")
            if today != vip_last_date:
                vip_count = 0
                vip_last_date = today
                print(f"New day for VIP channel: {today}")
            if vip_count < 35:
                s = generate_signal()
                dec = s["decimals"]
                entry_low_str = f"{s['entry_low']:.{dec}f}" if dec > 0 else str(int(s['entry_low']))
                entry_high_str = f"{s['entry_high']:.{dec}f}" if dec > 0 else str(int(s['entry_high']))
                tp1_str = f"{s['tp1']:.{dec}f}" if dec > 0 else str(int(s['tp1']))
                tp2_str = f"{s['tp2']:.{dec}f}" if dec > 0 else str(int(s['tp2']))
                sl_str = f"{s['sl']:.{dec}f}" if dec > 0 else str(int(s['sl']))
                msg = f"""⭐ *VIP EXCLUSIVE SIGNAL* ⭐
━━━━━━━━━━━━━━━━━━━━━━━
{s['emoji']} *{s['symbol']}* | {s['direction']}
━━━━━━━━━━━━━━━━━━━━━━━
📍 *Entry Zone:* `{entry_low_str} — {entry_high_str}`
🎯 *TP1:* `{tp1_str}`
🎯 *TP2:* `{tp2_str}`
⛔ *SL:* `{sl_str}`

📊 *Analysis:* {s['analysis']}
⏰ *Holding Period:* {s['holding_text']}
📈 *Confidence:* {s['confidence']}%

🕐 {now.strftime('%H:%M')} IST
🔒 *VIP Only*
━━━━━━━━━━━━━━━━━━━━━━━
🔥 Next signal in 10-15 mins!"""
                sent = bot.send_message(VIP_CHANNEL_ID, msg, parse_mode="Markdown")
                sig_id = save_signal(s, "vip")
                update_signal_result(sig_id, "pending", sent.message_id)
                vip_count += 1
                print(f"⭐ VIP signal #{vip_count} sent")
            else:
                # Course promo every 30 min after daily limit
                promo = f"🎓 *KAILASH FOREX MASTERCLASS* - VIP Special ₹1,499 only! DM {CONTACT_USERNAME}\n🌐 {COURSE_URL}"
                bot.send_message(VIP_CHANNEL_ID, promo, parse_mode="Markdown")
                print("📚 Course promo sent to VIP channel")
        except Exception as e:
            print(f"VIP scheduler error: {e}")
        time.sleep(900)  # 15 minutes

# ============================================
# PRICE MONITOR (TP/SL detection + auto-delete + hype)
# ============================================
TP_HYPE = [
    "🎯🔥 *TARGET HIT!* 🔥🎯\n\n{symbol} {direction} → *{tp} ✅ REACHED!*\n\n+{profit} {unit} profit!\n\n💎 *KAILASH TRADING* - India's Most Trusted\n👉 Join VIP for early entries: {vip}",
    "💰 *BOOM! TP HIT!* 💰\n\n{symbol} → *{tp} SMASHED!* 🎯\n*{direction} +{profit} {unit}*\n⭐ *Win Rate {accuracy}%* | VIP: {vip}",
]

def price_monitor():
    while True:
        time.sleep(180)  # every 3 minutes
        try:
            pending = get_pending_signals()
            for (sid, symbol, direction, entry, tp1, tp2, sl, msg_id, channel) in pending:
                # Get current price for the symbol's ticker
                ticker = next((s["ticker"] for s in SYMBOLS if s["name"] == symbol), None)
                if not ticker:
                    continue
                current = get_live_price(ticker)
                if current is None:
                    continue
                is_vip = (channel == "vip")
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
                                print(f"🗑️ Deleted losing signal: {symbol} {direction}")
                            except:
                                pass
                        update_signal_result(sid, "sl_hit")
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
                                print(f"🗑️ Deleted losing signal: {symbol} {direction}")
                            except:
                                pass
                        update_signal_result(sid, "sl_hit")
                        continue
                if hit:
                    # Determine profit and unit
                    decimals = 2 if "XAU" in symbol else (5 if "EUR" in symbol or "GBP" in symbol else 0)
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
                        profit=profit, unit=unit, vip=VIP_CHANNEL_LINK, accuracy=85
                    )
                    try:
                        bot.send_message(PUBLIC_CHANNEL_ID, hype, parse_mode="Markdown")
                        if is_vip and VIP_CHANNEL_ID:
                            bot.send_message(VIP_CHANNEL_ID, f"🏆 *VIP PROFIT!* {symbol} {direction} {label} +{profit} {unit}", parse_mode="Markdown")
                        update_signal_result(sid, "tp_hit")
                        print(f"🎯 TP hit: {symbol} {direction} {label}")
                    except Exception as e:
                        print(f"TP message error: {e}")
        except Exception as e:
            print(f"Price monitor error: {e}")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print("Starting background threads...")
    threading.Thread(target=public_scheduler, daemon=True).start()
    threading.Thread(target=vip_scheduler, daemon=True).start()
    threading.Thread(target=send_promos, daemon=True).start()
    threading.Thread(target=price_monitor, daemon=True).start()
    print("✅ All threads started. Bot is running in polling mode.")
    print("🚀 Bot is ready! Send /start on Telegram.")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Polling error: {e}")
        time.sleep(10)
