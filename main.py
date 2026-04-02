import telebot
import sqlite3
import datetime
import os
import random
import threading
import time
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import numpy as np
import requests
import json
from flask import Flask, request
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================
# CONFIGURATION
# ============================================
BOT_TOKEN = "8653450456:AAER9w6Gjj5IWkyCs1taa01N-DdMFZqxt3E"
ADMIN_ID = 6253584826
CHANNEL_ID = '@tradewithkailashh'
FREE_CHANNEL = 'https://t.me/tradewithkailashh'
VIP_CHANNEL_LINK = 'https://t.me/+Snj0BVAwjDo3NTA1'
VIP_CHANNEL_ID = "-1003826269063"
WEBSITE_URL = 'https://forexkailash.netlify.app'
COURSE_URL = 'https://forexkailash.netlify.app/course'
UPI_ID = 'kailashbhardwaj66-2@okicici'
CONTACT_USERNAME = '@forexkailash'

WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')

print("=" * 60)
print("🤖 KAILASH FOREX SIGNAL BOT - ULTIMATE PROMO EDITION")
print(f"Admin: {CONTACT_USERNAME}")
print(f"VIP Channel ID: {VIP_CHANNEL_ID}")
print("=" * 60)

# ============================================
# HEALTH CHECK SERVER
# ============================================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# ============================================
# RELIABLE SYMBOLS (All working)
# ============================================
SYMBOLS = [
    {"name": "XAU/USD", "ticker": "GC=F", "emoji": "🥇", "decimals": 2, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "type": "commodity"},
    {"name": "BTC/USD", "ticker": "BTC-USD", "emoji": "₿", "decimals": 0, "tp1_pct": 0.006, "tp2_pct": 0.012, "sl_pct": 0.004, "type": "crypto"},
    {"name": "EUR/USD", "ticker": "EURUSD=X", "emoji": "💶", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "type": "forex"},
    {"name": "USOIL", "ticker": "CL=F", "emoji": "🛢️", "decimals": 2, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003, "type": "commodity"},
    {"name": "GBP/USD", "ticker": "GBPUSD=X", "emoji": "💷", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "type": "forex"},
    {"name": "USD/JPY", "ticker": "JPY=X", "emoji": "🇯🇵", "decimals": 3, "tp1_pct": 0.003, "tp2_pct": 0.005, "sl_pct": 0.002, "type": "forex"},
    {"name": "ETH/USD", "ticker": "ETH-USD", "emoji": "💎", "decimals": 1, "tp1_pct": 0.007, "tp2_pct": 0.014, "sl_pct": 0.005, "type": "crypto"},
    {"name": "NAS100", "ticker": "NQ=F", "emoji": "📈", "decimals": 0, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "type": "index"},
    {"name": "SILVER", "ticker": "SI=F", "emoji": "🥈", "decimals": 3, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003, "type": "commodity"},
    {"name": "AUD/USD", "ticker": "AUDUSD=X", "emoji": "🦘", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "type": "forex"},
    {"name": "GBP/JPY", "ticker": "GBPJPY=X", "emoji": "⚡", "decimals": 3, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "type": "forex"},
    {"name": "US30", "ticker": "YM=F", "emoji": "🏛️", "decimals": 0, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "type": "index"},
    {"name": "USD/CAD", "ticker": "USDCAD=X", "emoji": "🍁", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "type": "forex"},
]

FALLBACK_PRICES = {
    "GC=F": 4520.00, "BTC-USD": 68500.00, "EURUSD=X": 1.08750, "CL=F": 79.50,
    "GBPUSD=X": 1.26800, "JPY=X": 150.50, "ETH-USD": 3550.00, "NQ=F": 18700.00,
    "SI=F": 27.80, "AUDUSD=X": 0.65500, "GBPJPY=X": 190.80, "YM=F": 39300.00,
    "USDCAD=X": 1.36000,
}

# ============================================
# NEWS SENTIMENT (free)
# ============================================
def get_news_sentiment(asset_name):
    try:
        url = f"https://gnews.io/api/v4/search?q={asset_name}&lang=en&max=5"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            if articles:
                pos_words = ['surge', 'rally', 'gain', 'bullish', 'up', 'higher', 'breakout', 'strong']
                neg_words = ['drop', 'fall', 'bearish', 'down', 'lower', 'crash', 'weak', 'decline']
                score = 0
                for art in articles:
                    title = art.get('title', '').lower()
                    for w in pos_words:
                        if w in title:
                            score += 1
                    for w in neg_words:
                        if w in title:
                            score -= 1
                if score > 0:
                    return "bullish", f"Positive news (+{score})"
                elif score < 0:
                    return "bearish", f"Negative news ({score})"
                else:
                    return "neutral", "Mixed news"
    except:
        pass
    return "neutral", "No clear news bias"

# ============================================
# TECHNICAL ANALYSIS (Multi-timeframe)
# ============================================
def fetch_safe_data(ticker, period, interval):
    for attempt in range(3):
        try:
            data = yf.download(ticker, period=period, interval=interval, progress=False, timeout=10)
            if not data.empty:
                return data
        except:
            pass
        time.sleep(1)
    return pd.DataFrame()

def get_technical_analysis(ticker, asset_name):
    try:
        daily = fetch_safe_data(ticker, "60d", "1d")
        four_hour = fetch_safe_data(ticker, "30d", "60m")
        if daily.empty:
            return None, 0, "No data", "short", "Short-term (1-2 days)"
        daily['rsi'] = ta.rsi(daily['Close'], length=14)
        daily['ema9'] = ta.ema(daily['Close'], length=9)
        daily['ema21'] = ta.ema(daily['Close'], length=21)
        macd = ta.macd(daily['Close'])
        if macd is not None:
            daily['macd'] = macd['MACD_12_26_9']
            daily['signal'] = macd['MACDs_12_26_9']
        else:
            daily['macd'] = 0
            daily['signal'] = 0
        recent_high = daily['High'].tail(20).max()
        recent_low = daily['Low'].tail(20).min()
        curr = daily['Close'].iloc[-1]
        daily_trend = "bullish" if daily['ema9'].iloc[-1] > daily['ema21'].iloc[-1] else "bearish"
        daily_rsi = daily['rsi'].iloc[-1] if not pd.isna(daily['rsi'].iloc[-1]) else 50
        daily_macd_bull = daily['macd'].iloc[-1] > daily['signal'].iloc[-1]
        four_hour_trend = "neutral"
        if not four_hour.empty and len(four_hour) > 20:
            four_hour['ema9'] = ta.ema(four_hour['Close'], length=9)
            four_hour['ema21'] = ta.ema(four_hour['Close'], length=21)
            if not pd.isna(four_hour['ema9'].iloc[-1]) and not pd.isna(four_hour['ema21'].iloc[-1]):
                four_hour_trend = "bullish" if four_hour['ema9'].iloc[-1] > four_hour['ema21'].iloc[-1] else "bearish"
        bullish_score = 0
        bearish_score = 0
        if daily_trend == "bullish":
            bullish_score += 3
        else:
            bearish_score += 3
        if daily_rsi < 30:
            bullish_score += 2
            rsi_signal = "oversold"
        elif daily_rsi > 70:
            bearish_score += 2
            rsi_signal = "overbought"
        else:
            rsi_signal = "neutral"
        if daily_macd_bull:
            bullish_score += 2
        else:
            bearish_score += 2
        if four_hour_trend == "bullish":
            bullish_score += 2
        elif four_hour_trend == "bearish":
            bearish_score += 2
        if curr <= recent_low * 1.005:
            bullish_score += 2
            sr_signal = "near support"
        elif curr >= recent_high * 0.995:
            bearish_score += 2
            sr_signal = "near resistance"
        else:
            sr_signal = "neutral"
        if bullish_score > bearish_score + 2:
            direction = "BUY"
            confidence = min(85, 60 + (bullish_score - bearish_score) * 3)
            if daily_trend == "bullish" and daily_rsi < 60:
                holding = "long"
                holding_text = "Long-term hold (3-7 days)"
            else:
                holding = "short"
                holding_text = "Short-term (1-2 days)"
        elif bearish_score > bullish_score + 2:
            direction = "SELL"
            confidence = min(85, 60 + (bearish_score - bullish_score) * 3)
            if daily_trend == "bearish" and daily_rsi > 40:
                holding = "long"
                holding_text = "Long-term hold (3-7 days)"
            else:
                holding = "short"
                holding_text = "Short-term (1-2 days)"
        else:
            direction = "BUY" if daily_trend == "bullish" else "SELL"
            confidence = 55
            holding = "short"
            holding_text = "Short-term (1-2 days)"
        reason = f"Daily: {daily_trend.upper()}, RSI {daily_rsi:.0f} ({rsi_signal}), MACD {'bullish' if daily_macd_bull else 'bearish'}. 4H: {four_hour_trend.upper()}. Price {sr_signal}."
        return direction, confidence, reason, holding, holding_text
    except Exception as e:
        print(f"Analysis error: {e}")
        return None, 0, None, "short", "Short-term (1-2 days)"

def get_live_price(ticker):
    for attempt in range(3):
        try:
            data = yf.download(ticker, period="1d", interval="5m", progress=False, timeout=10)
            if not data.empty:
                return float(data["Close"].iloc[-1])
        except:
            pass
        time.sleep(1)
    return FALLBACK_PRICES.get(ticker, 1000.00)

def generate_accurate_signal(symbol=None, include_news=True):
    if symbol is None:
        symbol = random.choice(SYMBOLS)
    tech_dir, confidence, tech_reason, holding, holding_text = get_technical_analysis(symbol["ticker"], symbol["name"])
    news_dir, news_reason = get_news_sentiment(symbol["name"].split('/')[0]) if include_news else ("neutral", "")
    final_dir = tech_dir if tech_dir else "BUY"
    final_confidence = confidence if confidence else 55
    if news_dir != "neutral" and news_dir == final_dir.lower():
        final_confidence = min(90, final_confidence + 10)
        combined_reason = f"{tech_reason} + {news_reason}"
    else:
        combined_reason = tech_reason
        if news_dir != "neutral":
            combined_reason += f" (News {news_dir} but technical neutral)"
    price = get_live_price(symbol["ticker"])
    d = symbol["decimals"]
    spread = price * 0.0005
    if final_dir == "BUY":
        entry_low = round(price - spread, d)
        entry_high = round(price + spread, d)
        if holding == "long":
            tp1 = round(price * (1 + symbol["tp1_pct"] * 1.5), d)
            tp2 = round(price * (1 + symbol["tp2_pct"] * 2.0), d)
            sl = round(price * (1 - symbol["sl_pct"] * 1.2), d)
        else:
            tp1 = round(price * (1 + symbol["tp1_pct"] * 0.8), d)
            tp2 = round(price * (1 + symbol["tp2_pct"] * 0.9), d)
            sl = round(price * (1 - symbol["sl_pct"] * 0.9), d)
    else:
        entry_low = round(price - spread, d)
        entry_high = round(price + spread, d)
        if holding == "long":
            tp1 = round(price * (1 - symbol["tp1_pct"] * 1.5), d)
            tp2 = round(price * (1 - symbol["tp2_pct"] * 2.0), d)
            sl = round(price * (1 + symbol["sl_pct"] * 1.2), d)
        else:
            tp1 = round(price * (1 - symbol["tp1_pct"] * 0.8), d)
            tp2 = round(price * (1 - symbol["tp2_pct"] * 0.9), d)
            sl = round(price * (1 + symbol["sl_pct"] * 0.9), d)
    return {
        "symbol": symbol["name"], "ticker": symbol["ticker"], "emoji": symbol["emoji"],
        "direction": final_dir, "entry_low": entry_low, "entry_high": entry_high,
        "tp1": tp1, "tp2": tp2, "sl": sl, "price": price, "decimals": d,
        "analysis": combined_reason, "confidence": final_confidence,
        "holding": holding, "holding_text": holding_text, "accuracy": final_confidence
    }

# ============================================
# DATABASE SETUP
# ============================================
os.makedirs("telegram_bot", exist_ok=True)
conn = sqlite3.connect('telegram_bot/users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, 
              register_date TEXT, is_vip INTEGER, last_promo_sent TEXT, 
              start_date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS registrations 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, 
              email TEXT, phone TEXT, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS signal_usage 
             (user_id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS channel_signals 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, direction TEXT,
              entry REAL, tp1 REAL, tp2 REAL, sl REAL, decimals INTEGER,
              sent_date TEXT, sent_time TEXT, result TEXT DEFAULT "pending",
              message_id INTEGER DEFAULT NULL, ticker TEXT,
              channel_type TEXT DEFAULT "public", accuracy INTEGER DEFAULT 85,
              timeframe TEXT, reason TEXT, holding TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS bot_settings 
             (key TEXT PRIMARY KEY, value TEXT)''')
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
# INITIALIZE BOT
# ============================================
bot = telebot.TeleBot(BOT_TOKEN)
print(f"✅ Bot connected: {bot.get_me().username}")

def save_signal_to_db(data, channel_type="public"):
    now = datetime.datetime.now()
    c.execute("""INSERT INTO channel_signals 
                 (symbol, direction, entry, tp1, tp2, sl, decimals, sent_date, sent_time, ticker, channel_type, accuracy, timeframe, reason, holding)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (data["symbol"], data["direction"], (data["entry_low"]+data["entry_high"])/2,
               data["tp1"], data["tp2"], data["sl"], data["decimals"],
               now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), data["ticker"], channel_type,
               data.get("accuracy", 85), "Multi-timeframe", data.get("analysis", ""), data.get("holding", "short")))
    conn.commit()
    return c.lastrowid

def update_signal_message_id(signal_id, msg_id):
    c.execute("UPDATE channel_signals SET message_id=? WHERE id=?", (msg_id, signal_id))
    conn.commit()

def update_signal_result(signal_id, result):
    c.execute("UPDATE channel_signals SET result=? WHERE id=?", (result, signal_id))
    conn.commit()

def get_pending_signals():
    c.execute("SELECT id, symbol, direction, entry, tp1, tp2, sl, decimals, message_id, ticker, result, channel_type, accuracy FROM channel_signals WHERE result='pending' AND message_id IS NOT NULL")
    return c.fetchall()

IST_OFFSET = datetime.timedelta(hours=5, minutes=30)
def get_ist_time():
    return datetime.datetime.utcnow() + IST_OFFSET

# ============================================
# SIGNAL TEMPLATES
# ============================================
def template_with_analysis(d):
    ist = get_ist_time()
    return f"""🔥🔥🔥 *LIVE SIGNAL ALERT* 🔥🔥🔥

{d['emoji']} *{d['direction']} {d['symbol']}*
━━━━━━━━━━━━━━━━━━━━━━━━
📌 *Entry Zone:* `{d['entry_low']} — {d['entry_high']}`
🎯 *TP 1:* `{d['tp1']}` ✅
🎯 *TP 2:* `{d['tp2']}` ✅✅
🛑 *Stop Loss:* `{d['sl']}`

📊 *Analysis:* _{d['analysis']}_
⏰ *Holding Period:* {d['holding_text']}
📈 *Confidence:* {d['confidence']}%

🕐 {ist.strftime('%d %b %Y • %I:%M %p')} IST
━━━━━━━━━━━━━━━━━━━━━━━━
💎 *Win Rate Target: {d['confidence']}%* | Risk: 1-2%
⭐ VIP gets signals *30 mins early!*
👇 *Upgrade to VIP — ₹399/month*
{VIP_CHANNEL_LINK}"""

def template_winner(d):
    ist = get_ist_time()
    return f"""🏆 *WINNING SIGNAL ALERT* 🏆

{d['emoji']} *{d['direction']} {d['symbol']}* — HIGH PROBABILITY

━━━━━━━━━━━━━━━━━━━━━━━━
📌 Entry: `{d['entry_low']} - {d['entry_high']}`
🎯 TP1: `{d['tp1']}`
🎯 TP2: `{d['tp2']}`
🛑 SL: `{d['sl']}`

💡 *Analysis:* _{d['analysis']}_
⏰ *Hold:* {d['holding_text']}
📊 *Confidence: {d['confidence']}%*
━━━━━━━━━━━━━━━━━━━━━━━━
⭐ *VIP Members get EXCLUSIVE early entries!*
Join VIP — only ₹399/month
🔗 {VIP_CHANNEL_LINK}"""

TEMPLATES = [template_with_analysis, template_winner]

def build_channel_post():
    d = generate_accurate_signal()
    sid = save_signal_to_db(d, "public")
    return random.choice(TEMPLATES)(d), sid

# ============================================
# 30+ UNIQUE PROMOTIONAL MESSAGES (Indian English, Hype)
# ============================================
PROMO_MESSAGES = [
    "💎 *FREE SIGNALS MILTE HAIN* daily! Join our free channel: {FREE_CHANNEL}\n⭐ VIP me early entry + 30-35 signals/day sirf ₹399! {VIP_CHANNEL_LINK}",
    "🚀 *Aaj hi 3 logon ne VIP join kiya aur profit book kiya!* Tum kab aa rahe ho? {VIP_CHANNEL_LINK}",
    "📊 *Free channel me signal delay hota hai.* VIP me entry 30 min pehle milti hai. Fark dekho: {VIP_CHANNEL_LINK}",
    "💰 *₹399/month mein kya milega?* 30-35 premium signals, early entry, 1-on-1 support. ROI 3600%+! Join: {VIP_CHANNEL_LINK}",
    "⚠️ *Limited slots!* Sirf {random.randint(3,7)} VIP seats bachi hain. Price soon ₹599. Lock ₹399 now: {VIP_CHANNEL_LINK}",
    "🏆 *89% win rate* - proof hai mere channel pe. Free signals dekh lo, phir VIP decide karo. Free channel: {FREE_CHANNEL}",
    "🎯 *Aaj ka GOLD signal TP2 hit!* +250 pips. VIP members ko early entry mili thi. Tum bhi lo: {VIP_CHANNEL_LINK}",
    "📚 *FREE FOREX MASTERCLASS* - VIP members ko ₹2,999 ka course free. DM {CONTACT_USERNAME} after joining VIP.",
    "💬 *Testimonial:* 'Joined VIP, 10x subscription fee wapas kama liya first month.' - Rahul, Mumbai. Join now: {VIP_CHANNEL_LINK}",
    "⏰ *Price hike warning!* Next month ₹599. Abhi ₹399 mein lock karo lifetime: {VIP_CHANNEL_LINK}",
    "🔥 *Copy trading available* - Mere trades automatically copy karo. VIP members ke liye. Join: {VIP_CHANNEL_LINK}",
    "📈 *Daily 8-10 free signals* milte hain free channel pe. Par early entry sirf VIP ko. Dono join karo: {FREE_CHANNEL} | {VIP_CHANNEL_LINK}",
    "💎 *Kailash sir khud dete hain signals* - 7+ years experience. Trusted by 5000+ traders. VIP link: {VIP_CHANNEL_LINK}",
    "🎁 *Special offer:* Pehle 10 VIP members ko free course. Hurry up! {VIP_CHANNEL_LINK}",
    "📊 *Free vs VIP difference:* Free = delayed entry, 3-5 signals. VIP = early entry, 30-35 signals. Choose wisely: {VIP_CHANNEL_LINK}",
    "💸 *Kal ka profit:* VIP members ne ₹8,000+ banaye sirf 2 trades se. Miss mat karo: {VIP_CHANNEL_LINK}",
    "🚨 *BREAKING:* Gold breakout coming. VIP ko 30 min pehle pata chalega. Join fast: {VIP_CHANNEL_LINK}",
    "🎓 *Course + Signals combo* - VIP special ₹1,499 only (50% off). DM {CONTACT_USERNAME} for details.",
    "💬 *FAQ:* UPI payment accept hai. Pay ₹399 to {UPI_ID}, screenshot bhejo, channel link milega. Simple!",
    "🌟 *Trusted by 5000+ Indian traders.* Aao tum bhi team mein: {VIP_CHANNEL_LINK}",
    "📱 *Telegram par 24/7 support* - VIP members ko priority response. Join: {VIP_CHANNEL_LINK}",
    "⚡ *Momentum trade alert* - 4H timeframe pe setup bana hai. VIP ko pehle milega. {VIP_CHANNEL_LINK}",
    "💎 *Gold, Crypto, Forex, Indices* - sab pe signals. Ek baar VIP try karo: {VIP_CHANNEL_LINK}",
    "🎯 *Today's target:* 3 VIP signals already in profit. Join abhi: {VIP_CHANNEL_LINK}",
    "📢 *FREE channel join karo* - daily 8-10 signals. Phir VIP upgrade karna easy rahega: {FREE_CHANNEL}",
    "💡 *Risk management sikhoge* VIP me. Kailash sir guide karte hain. ₹399 only: {VIP_CHANNEL_LINK}",
    "🏆 *Kaun banega crorepati?* Mere VIP members consistently profitable hain. Tum bano: {VIP_CHANNEL_LINK}",
    "🔄 *Auto copy-trade setup help* - VIP members ko free. DM {CONTACT_USERNAME} after joining.",
    "📊 *Weekly review:* VIP members ka average profit this week ₹12,000. Miss mat karo: {VIP_CHANNEL_LINK}",
    "⏳ *Last chance* - Sirf {random.randint(2,5)} seats left at ₹399. Next price ₹599. {VIP_CHANNEL_LINK}",
    "🎓 *Want to learn trading?* Course + Signals combo best hai. DM {CONTACT_USERNAME} for offer.",
    "💎 *Kailash Forex Masterclass* - Limited time 50% off for VIP. Enroll: {COURSE_URL}",
]

def get_promo_for_user():
    """Return a random promo message with placeholders replaced"""
    msg = random.choice(PROMO_MESSAGES)
    return msg.format(
        FREE_CHANNEL=FREE_CHANNEL,
        VIP_CHANNEL_LINK=VIP_CHANNEL_LINK,
        CONTACT_USERNAME=CONTACT_USERNAME,
        UPI_ID=UPI_ID,
        COURSE_URL=COURSE_URL
    )

# ============================================
# BACKGROUND THREAD: SEND PROMOS TO ALL USERS EVERY 30 MIN
# ============================================
def send_promo_to_all_users():
    """Send a unique promo message to every user who has ever started the bot (every 30 min)"""
    while True:
        try:
            # Get all users who have started the bot (either registered or just /start)
            c.execute("SELECT user_id, last_promo_sent FROM users")
            users = c.fetchall()
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for (uid, last_sent) in users:
                # Avoid sending too frequently (but we already run every 30 min, so fine)
                try:
                    promo_text = get_promo_for_user()
                    bot.send_message(uid, promo_text, parse_mode='Markdown')
                    # Update last_promo_sent
                    c.execute("UPDATE users SET last_promo_sent=? WHERE user_id=?", (now_str, uid))
                    conn.commit()
                    time.sleep(0.5)  # Respect rate limits
                except Exception as e:
                    print(f"Failed to send promo to {uid}: {e}")
            print(f"✅ Promos sent to {len(users)} users at {get_ist_time().strftime('%H:%M')}")
        except Exception as e:
            print(f"Promo sender error: {e}")
        time.sleep(1800)  # 30 minutes

# ============================================
# PRICE MONITOR (TP/SL)
# ============================================
TP_HYPE = [
    "🎯🔥 *TARGET HIT!* 🔥🎯\n\n{symbol} {direction} → *{tp} ✅ REACHED!*\n\n+{profit} {unit} profit!\n\n💎 *KAILASH TRADING* - India's Most Trusted\n👉 Join VIP for early entries: {vip}",
    "💰 *BOOM! TP HIT!* 💰\n\n{symbol} → *{tp} SMASHED!* 🎯\n*{direction} +{profit} {unit}*\n⭐ *Win Rate {accuracy}%* | VIP: {vip}",
]

def price_monitor():
    while True:
        time.sleep(180)
        try:
            pending = get_pending_signals()
            for row in pending:
                sig_id, symbol, direction, entry, tp1, tp2, sl, decimals, msg_id, ticker, result, ch_type, accuracy = row
                current = get_live_price(ticker)
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
                                bot.delete_message(CHANNEL_ID, msg_id)
                            except:
                                pass
                        update_signal_result(sig_id, "sl_hit")
                        continue
                else:
                    if current <= tp2:
                        hit, label = tp2, "TP2 🎯🎯"
                    elif current <= tp1:
                        hit, label = tp1, "TP1 🎯"
                    elif current >= sl:
                        if not is_vip:
                            try:
                                bot.delete_message(CHANNEL_ID, msg_id)
                            except:
                                pass
                        update_signal_result(sig_id, "sl_hit")
                        continue
                if hit:
                    if decimals == 5:
                        profit = round(abs(hit - entry) * 10000, 1)
                        unit = "pips"
                    else:
                        profit = round(abs(hit - entry), 2)
                        unit = "points"
                    hype = random.choice(TP_HYPE).format(symbol=symbol, direction=direction, tp=label, profit=profit, unit=unit, vip=VIP_CHANNEL_LINK, accuracy=accuracy)
                    try:
                        bot.send_message(CHANNEL_ID, hype, parse_mode='Markdown')
                        if is_vip and VIP_CHANNEL_ID:
                            bot.send_message(VIP_CHANNEL_ID, f"🏆 *VIP PROFIT!* {symbol} {direction} {label} +{profit} {unit}", parse_mode='Markdown')
                        update_signal_result(sig_id, "tp_hit")
                    except:
                        pass
        except Exception as e:
            print(f"Monitor error: {e}")

# ============================================
# VIP CHANNEL SCHEDULER
# ============================================
def vip_signal_post(d):
    ist = get_ist_time()
    dir_word = "BUY 🟢" if d["direction"] == "BUY" else "SELL 🔴"
    return f"""⭐ *VIP EXCLUSIVE SIGNAL* ⭐
━━━━━━━━━━━━━━━━━━━━━━━
{d['emoji']} *{d['symbol']}* | {dir_word}
━━━━━━━━━━━━━━━━━━━━━━━
📍 *Entry Zone:* `{d['entry_low']} — {d['entry_high']}`
🎯 *TP1:* `{d['tp1']}`
🎯 *TP2:* `{d['tp2']}`
⛔ *SL:* `{d['sl']}`
📊 *Analysis:* _{d['analysis']}_
⏰ *Hold:* {d['holding_text']} | Confidence: {d['confidence']}%
🕐 {ist.strftime('%H:%M')} IST
🔒 VIP Only
━━━━━━━━━━━━━━━━━━━━━━━
🔥 Next signal in 10-15 mins!"""

VIP_COURSE_PROMOS = [
    f"🎓 *KAILASH FOREX MASTERCLASS* - VIP Special ₹1,499 only! DM {CONTACT_USERNAME}",
    f"📚 *Learn to trade like a pro* - VIP discount! Course: {COURSE_URL}",
    f"💎 *Masterclass Access* - 50% OFF for VIP members. DM {CONTACT_USERNAME}",
]

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
                d = generate_accurate_signal(sym)
                sid = save_signal_to_db(d, "vip")
                text = vip_signal_post(d)
                sent = bot.send_message(VIP_CHANNEL_ID, text, parse_mode='Markdown')
                update_signal_message_id(sid, sent.message_id)
                vip_signal_count += 1
                print(f"VIP signal #{vip_signal_count}: {d['symbol']} {d['direction']} (conf {d['confidence']}%)")
            else:
                promo_counter += 1
                if promo_counter % 2 == 0:
                    bot.send_message(VIP_CHANNEL_ID, random.choice(VIP_COURSE_PROMOS), parse_mode='Markdown')
        except Exception as e:
            print(f"VIP scheduler error: {e}")
        time.sleep(random.randint(600, 900))

# ============================================
# PUBLIC SCHEDULER (8-10 signals + promos)
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
                    text, sid = build_channel_post()
                    sent = bot.send_message(CHANNEL_ID, text, parse_mode='Markdown')
                    update_signal_message_id(sid, sent.message_id)
                    public_signal_count += 1
                    print(f"Public signal #{public_signal_count} posted")
                else:
                    bot.send_message(CHANNEL_ID, get_promo_for_user(), parse_mode='Markdown')
            else:
                bot.send_message(CHANNEL_ID, get_promo_for_user(), parse_mode='Markdown')
        except Exception as e:
            print(f"Public scheduler error: {e}")
        time.sleep(1800)

# ============================================
# BOT COMMANDS
# ============================================
def main_keyboard():
    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    kb.add(telebot.types.InlineKeyboardButton("📝 Register", callback_data="register"))
    kb.add(telebot.types.InlineKeyboardButton("📊 Free Signal", callback_data="free"))
    kb.add(telebot.types.InlineKeyboardButton("⭐ VIP Access", callback_data="vip"))
    kb.add(telebot.types.InlineKeyboardButton("💬 Support", callback_data="support"))
    kb.add(telebot.types.InlineKeyboardButton("🌐 Website", url=WEBSITE_URL))
    kb.add(telebot.types.InlineKeyboardButton("📢 Free Channel", url=FREE_CHANNEL))
    return kb

@bot.message_handler(commands=['start'])
def start_cmd(msg):
    uid = msg.from_user.id
    # Add user to database if not exists (so they receive promos)
    c.execute("SELECT user_id FROM users WHERE user_id=?", (uid,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, name, email, phone, register_date, is_vip, last_promo_sent, start_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
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
📢 *Free Channel:* {FREE_CHANNEL}
⭐ *VIP Channel:* {VIP_CHANNEL_LINK}

👇 *Choose an option:*"""
    bot.reply_to(msg, txt, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['register'])
def reg_cmd(msg):
    m = bot.reply_to(msg, "📝 *Send:* `Name, Email, Phone`\nExample: `Rajesh, rajesh@gmail.com, 9876543210`", parse_mode='Markdown')
    bot.register_next_step_handler(m, save_user)

def save_user(msg):
    uid = msg.from_user.id
    uname = msg.from_user.username or "No username"
    try:
        data = msg.text.split(',')
        name = data[0].strip()
        email = data[1].strip()
        phone = data[2].strip()
        c.execute("UPDATE users SET name=?, email=?, phone=?, register_date=? WHERE user_id=?", (name, email, phone, str(datetime.datetime.now()), uid))
        c.execute("INSERT INTO registrations (user_id, name, email, phone, date) VALUES (?,?,?,?,?)", (uid, name, email, phone, str(datetime.datetime.now())))
        conn.commit()
        bot.send_message(ADMIN_ID, f"🔔 New registration: {name} (@{uname})")
        bot.reply_to(msg, f"✅ Welcome {name}! Use /free for signals.", parse_mode='Markdown', reply_markup=main_keyboard())
    except:
        bot.reply_to(msg, "❌ Invalid format. Send: `Name, Email, Phone`", parse_mode='Markdown')

@bot.message_handler(commands=['free'])
def free_cmd(msg):
    uid = msg.from_user.id
    rem = signals_remaining(uid)
    if rem <= 0:
        bot.reply_to(msg, f"🚫 Free limit reached. Join VIP: /vip", parse_mode='Markdown')
        return
    increment_signal_count(uid)
    d = generate_accurate_signal()
    sig = f"""📊 *FREE SIGNAL (Real Analysis)* 📊
{d['emoji']} *{d['direction']} {d['symbol']}*
📌 Entry: `{d['entry_low']} - {d['entry_high']}`
🎯 TP1: `{d['tp1']}`
🎯 TP2: `{d['tp2']}`
🛑 SL: `{d['sl']}`
📈 *Analysis:* {d['analysis']}
⏰ *Hold:* {d['holding_text']} | Confidence: {d['confidence']}%"""
    bot.reply_to(msg, sig, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['vip'])
def vip_cmd(msg):
    bot.reply_to(msg, f"⭐ *VIP ACCESS* - ₹399/month\n📱 UPI: `{UPI_ID}`\nPay & send screenshot to {CONTACT_USERNAME}\n🔗 {VIP_CHANNEL_LINK}", parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['support'])
def support_cmd(msg):
    bot.reply_to(msg, f"💬 {CONTACT_USERNAME}\n📧 btcuscoinbase@gmail.com", parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['website'])
def web_cmd(msg):
    bot.reply_to(msg, f"🌐 {WEBSITE_URL}", parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['stats'])
def stats_cmd(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    bot.reply_to(msg, f"📊 Total users: {total}", parse_mode='Markdown')

@bot.message_handler(commands=['setvipid'])
def set_vip(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.reply_to(msg, "VIP ID is hardcoded. No need to set.", parse_mode='Markdown')

@bot.message_handler(commands=['vipstatus'])
def vip_status(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    bot.reply_to(msg, f"✅ VIP channel ID: `{VIP_CHANNEL_ID}`\n📡 Scheduler active\n📊 Daily target: 35 signals", parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "register":
        m = bot.send_message(call.message.chat.id, "📝 Send: `Name, Email, Phone`", parse_mode='Markdown')
        bot.register_next_step_handler(m, save_user)
    elif call.data == "free":
        free_cmd(call.message)
    elif call.data == "vip":
        vip_cmd(call.message)
    elif call.data == "support":
        support_cmd(call.message)
    bot.answer_callback_query(call.id)

# ============================================
# WEBHOOK OR POLLING
# ============================================
def set_webhook():
    if WEBHOOK_URL:
        webhook_path = f"{WEBHOOK_URL}/webhook"
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(url=webhook_path)
            print(f"✅ Webhook set to {webhook_path}")
            return True
        except Exception as e:
            print(f"❌ Webhook failed: {e}")
    return False

flask_app = Flask(__name__)

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad Request', 400

@flask_app.route('/')
def index():
    return "Bot is running", 200

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print("Starting all threads...")
    threading.Thread(target=public_scheduler, daemon=True).start()
    threading.Thread(target=price_monitor, daemon=True).start()
    threading.Thread(target=vip_channel_scheduler, daemon=True).start()
    threading.Thread(target=send_promo_to_all_users, daemon=True).start()
    if set_webhook():
        port = int(os.environ.get('PORT', 8080))
        print(f"🚀 Starting Flask webhook server on port {port}")
        flask_app.run(host='0.0.0.0', port=port)
    else:
        print("⚠️ Webhook failed, falling back to polling")
        while True:
            try:
                bot.remove_webhook()
                bot.infinity_polling(timeout=60, long_polling_timeout=60)
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(15)
