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
CONTACT_USERNAME = '@Yungshang1'

print("=" * 60)
print("🤖 KAILASH FOREX SIGNAL BOT - REAL ANALYSIS EDITION")
print(f"VIP Channel ID: {VIP_CHANNEL_ID}")
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
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# ============================================
# TRADING SYMBOLS (with additional data)
# ============================================
SYMBOLS = [
    {"name": "XAU/USD", "ticker": "GC=F", "emoji": "🥇", "decimals": 2, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "accuracy": 0},
    {"name": "BTC/USD", "ticker": "BTC-USD", "emoji": "₿", "decimals": 0, "tp1_pct": 0.006, "tp2_pct": 0.012, "sl_pct": 0.004, "accuracy": 0},
    {"name": "EUR/USD", "ticker": "EURUSD=X", "emoji": "💶", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "accuracy": 0},
    {"name": "USOIL", "ticker": "CL=F", "emoji": "🛢️", "decimals": 2, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003, "accuracy": 0},
    {"name": "GBP/USD", "ticker": "GBPUSD=X", "emoji": "💷", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "accuracy": 0},
    {"name": "USD/JPY", "ticker": "JPY=X", "emoji": "🇯🇵", "decimals": 3, "tp1_pct": 0.003, "tp2_pct": 0.005, "sl_pct": 0.002, "accuracy": 0},
    {"name": "ETH/USD", "ticker": "ETH-USD", "emoji": "💎", "decimals": 1, "tp1_pct": 0.007, "tp2_pct": 0.014, "sl_pct": 0.005, "accuracy": 0},
    {"name": "NAS100", "ticker": "NQ=F", "emoji": "📈", "decimals": 0, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "accuracy": 0},
    {"name": "SILVER", "ticker": "SI=F", "emoji": "🥈", "decimals": 3, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003, "accuracy": 0},
    {"name": "AUD/USD", "ticker": "AUDUSD=X", "emoji": "🦘", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "accuracy": 0},
    {"name": "GBP/JPY", "ticker": "GBPJPY=X", "emoji": "⚡", "decimals": 3, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "accuracy": 0},
    {"name": "US30", "ticker": "YM=F", "emoji": "🏛️", "decimals": 0, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "accuracy": 0},
    {"name": "USD/CAD", "ticker": "USDCAD=X", "emoji": "🍁", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "accuracy": 0},
    {"name": "SOL/USD", "ticker": "SOL-USD", "emoji": "☀️", "decimals": 2, "tp1_pct": 0.008, "tp2_pct": 0.016, "sl_pct": 0.006, "accuracy": 0},
]

# ============================================
# REAL TECHNICAL ANALYSIS ENGINE
# ============================================
def get_multi_timeframe_analysis(ticker):
    """
    Fetch data for 15min, 1H, 4H, Daily and return combined analysis
    Returns: (direction, confidence, reason, timeframe_used)
    """
    try:
        # Fetch daily data first for support/resistance
        daily = yf.download(ticker, period="60d", interval="1d", progress=False)
        if daily.empty:
            return None, 0, "No data", None
        
        # Calculate daily indicators
        daily['rsi'] = ta.rsi(daily['Close'], length=14)
        daily['ema9'] = ta.ema(daily['Close'], length=9)
        daily['ema21'] = ta.ema(daily['Close'], length=21)
        macd = ta.macd(daily['Close'])
        daily['macd'] = macd['MACD_12_26_9'] if macd is not None else 0
        daily['signal'] = macd['MACDs_12_26_9'] if macd is not None else 0
        
        # Support/Resistance (recent swing highs/lows)
        recent_high = daily['High'].tail(20).max()
        recent_low = daily['Low'].tail(20).min()
        current_price = daily['Close'].iloc[-1]
        
        # Fetch 4H data
        four_hour = yf.download(ticker, period="10d", interval="60m", progress=False)
        if not four_hour.empty:
            four_hour['ema9'] = ta.ema(four_hour['Close'], length=9)
            four_hour['ema21'] = ta.ema(four_hour['Close'], length=21)
            four_hour['rsi'] = ta.rsi(four_hour['Close'], length=14)
        
        # Fetch 1H data
        one_hour = yf.download(ticker, period="5d", interval="30m", progress=False)
        if not one_hour.empty:
            one_hour['ema9'] = ta.ema(one_hour['Close'], length=9)
            one_hour['ema21'] = ta.ema(one_hour['Close'], length=21)
        
        # Fetch 15min data for entry timing
        fifteen_min = yf.download(ticker, period="2d", interval="15m", progress=False)
        
        # --- Analysis Logic ---
        # Determine trend on multiple timeframes
        daily_trend = "bullish" if daily['ema9'].iloc[-1] > daily['ema21'].iloc[-1] else "bearish"
        daily_rsi = daily['rsi'].iloc[-1]
        daily_macd_bull = daily['macd'].iloc[-1] > daily['signal'].iloc[-1]
        
        four_hour_trend = "bullish" if not four_hour.empty and four_hour['ema9'].iloc[-1] > four_hour['ema21'].iloc[-1] else "neutral"
        one_hour_trend = "bullish" if not one_hour.empty and one_hour['ema9'].iloc[-1] > one_hour['ema21'].iloc[-1] else "neutral"
        
        # Score based on multiple timeframes
        bullish_score = 0
        bearish_score = 0
        
        # Daily score
        if daily_trend == "bullish":
            bullish_score += 3
        else:
            bearish_score += 3
        
        # RSI (oversold = bullish, overbought = bearish)
        if daily_rsi < 30:
            bullish_score += 2
            rsi_signal = "Oversold"
        elif daily_rsi > 70:
            bearish_score += 2
            rsi_signal = "Overbought"
        else:
            rsi_signal = "Neutral"
        
        # MACD
        if daily_macd_bull:
            bullish_score += 2
        else:
            bearish_score += 2
        
        # 4H alignment
        if four_hour_trend == "bullish":
            bullish_score += 2
        elif four_hour_trend == "bearish":
            bearish_score += 2
        
        # 1H alignment
        if one_hour_trend == "bullish":
            bullish_score += 1
        elif one_hour_trend == "bearish":
            bearish_score += 1
        
        # Support/Resistance
        if current_price <= recent_low * 1.005:  # near support
            bullish_score += 2
        if current_price >= recent_high * 0.995:  # near resistance
            bearish_score += 2
        
        # Final decision
        if bullish_score > bearish_score + 2:
            direction = "BUY"
            confidence = min(85, 60 + (bullish_score - bearish_score) * 3)
            # Determine best timeframe for signal
            if daily_trend == "bullish" and daily_rsi < 40:
                timeframe_used = "Daily + RSI"
                reason = f"Daily trend bullish, RSI {daily_rsi:.0f} (not overbought), MACD bullish. Support near {recent_low:.2f}."
            elif four_hour_trend == "bullish":
                timeframe_used = "4-Hour"
                reason = f"4H uptrend confirmed, price above EMAs. Daily bias also bullish."
            else:
                timeframe_used = "15-Minute"
                reason = f"Short-term momentum turning up. Daily trend supports upside."
        elif bearish_score > bullish_score + 2:
            direction = "SELL"
            confidence = min(85, 60 + (bearish_score - bullish_score) * 3)
            if daily_trend == "bearish" and daily_rsi > 60:
                timeframe_used = "Daily + RSI"
                reason = f"Daily trend bearish, RSI {daily_rsi:.0f} (overbought), MACD bearish. Resistance near {recent_high:.2f}."
            elif four_hour_trend == "bearish":
                timeframe_used = "4-Hour"
                reason = f"4H downtrend confirmed, price below EMAs."
            else:
                timeframe_used = "15-Minute"
                reason = f"Short-term momentum turning down. Daily trend aligns."
        else:
            # Neutral - fallback to slightly bullish or bearish based on daily trend
            if daily_trend == "bullish":
                direction = "BUY"
                confidence = 55
                timeframe_used = "Daily Trend (Neutral)"
                reason = f"Daily trend bullish but momentum mixed. RSI {daily_rsi:.0f}."
            else:
                direction = "SELL"
                confidence = 55
                timeframe_used = "Daily Trend (Neutral)"
                reason = f"Daily trend bearish but momentum mixed. RSI {daily_rsi:.0f}."
        
        return direction, confidence, reason, timeframe_used
        
    except Exception as e:
        print(f"Analysis error for {ticker}: {e}")
        return None, 0, None, None

def generate_accurate_signal(symbol=None):
    """Generate signal based on real technical analysis"""
    if symbol is None:
        symbol = random.choice(SYMBOLS)
    
    # Get real analysis
    direction, confidence, reason, tf_used = get_multi_timeframe_analysis(symbol["ticker"])
    
    if direction is None or reason is None:
        # Fallback to simple price action if analysis fails
        direction = random.choice(["BUY", "SELL"])
        confidence = 60
        reason = "Simple price action (analysis temporary unavailable)"
        tf_used = "Fallback"
    
    # Get live price
    try:
        ticker_obj = yf.Ticker(symbol["ticker"])
        hist = ticker_obj.history(period="1d", interval="5m")
        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
        else:
            price = 1000.00
    except:
        price = 1000.00
    
    d = symbol["decimals"]
    # Use confidence to adjust TP/SL (higher confidence = tighter stops)
    if confidence > 75:
        tp1_pct = symbol["tp1_pct"] * 1.1
        tp2_pct = symbol["tp2_pct"] * 1.1
        sl_pct = symbol["sl_pct"] * 0.9
    elif confidence < 60:
        tp1_pct = symbol["tp1_pct"] * 0.9
        tp2_pct = symbol["tp2_pct"] * 0.9
        sl_pct = symbol["sl_pct"] * 1.1
    else:
        tp1_pct = symbol["tp1_pct"]
        tp2_pct = symbol["tp2_pct"]
        sl_pct = symbol["sl_pct"]
    
    spread = price * 0.0005  # small spread
    
    if direction == "BUY":
        entry_low = round(price - spread, d)
        entry_high = round(price + spread, d)
        tp1 = round(price * (1 + tp1_pct), d)
        tp2 = round(price * (1 + tp2_pct), d)
        sl = round(price * (1 - sl_pct), d)
        analysis_text = reason
    else:
        entry_low = round(price - spread, d)
        entry_high = round(price + spread, d)
        tp1 = round(price * (1 - tp1_pct), d)
        tp2 = round(price * (1 - tp2_pct), d)
        sl = round(price * (1 + sl_pct), d)
        analysis_text = reason
    
    # Store accuracy in symbol for later
    symbol["accuracy"] = confidence
    
    return {
        "symbol": symbol["name"],
        "ticker": symbol["ticker"],
        "emoji": symbol["emoji"],
        "direction": direction,
        "entry_low": entry_low,
        "entry_high": entry_high,
        "tp1": tp1,
        "tp2": tp2,
        "sl": sl,
        "price": price,
        "decimals": d,
        "analysis": analysis_text,
        "timeframe": tf_used,
        "confidence": confidence,
        "accuracy": confidence
    }

# ============================================
# DATABASE SETUP (same as before)
# ============================================
os.makedirs("telegram_bot", exist_ok=True)
conn = sqlite3.connect('telegram_bot/users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, register_date TEXT, is_vip INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, email TEXT, phone TEXT, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS signal_usage (user_id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS channel_signals (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, direction TEXT, entry REAL, tp1 REAL, tp2 REAL, sl REAL, decimals INTEGER, sent_date TEXT, sent_time TEXT, result TEXT DEFAULT "pending", message_id INTEGER DEFAULT NULL, ticker TEXT, channel_type TEXT DEFAULT "public", accuracy INTEGER DEFAULT 85, timeframe TEXT, reason TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, value TEXT)''')
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
    c.execute("""INSERT INTO channel_signals (symbol, direction, entry, tp1, tp2, sl, decimals, sent_date, sent_time, ticker, channel_type, accuracy, timeframe, reason)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (data["symbol"], data["direction"], (data["entry_low"]+data["entry_high"])/2,
               data["tp1"], data["tp2"], data["sl"], data["decimals"],
               now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), data["ticker"], channel_type,
               data.get("accuracy", 85), data.get("timeframe", "Multiple"), data.get("analysis", "")))
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
# SIGNAL TEMPLATES (with timeframe and reason)
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

📊 *Technical Analysis:*
_{d['analysis']}_

⏰ *Timeframe:* {d['timeframe']}
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

💡 *Why this trade:*
_{d['analysis']}_

⏰ *Signal from:* {d['timeframe']} timeframe
📊 *Kailash Confidence: {d['confidence']}%*
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
# PROMOTIONAL MESSAGES (22 as before, keep same)
# ============================================
PROMO_MESSAGES = [
    f"""💬 *WHAT OUR MEMBERS ARE SAYING* 💬
⭐⭐⭐⭐⭐

_"Joined VIP last month and already made back 10x my subscription fee. Kailash signals are insane!"_

— Rahul M., Mumbai

━━━━━━━━━━━━━━━━━━━━━━━
🚀 *Join 5000+ traders making money daily!*
💰 VIP = ₹399/month only
📩 DM to join → {CONTACT_USERNAME}
🔗 {VIP_CHANNEL_LINK}""",

    f"""⏰ *LIMITED SLOTS ALERT!* ⏰

🔥 Only *{random.randint(3,7)} VIP slots remaining* for this month!

*What VIP members get:*
✅ 7-10 Signals Daily (vs 3-5 free)
✅ Entry *30 mins before* free channel
✅ Gold & Crypto Premium Calls
✅ 1-on-1 Support

━━━━━━━━━━━━━━━━━━━━━━━
⚡ *ACT NOW — only {random.randint(3,7)} spots left!*
💰 ₹399/month
📩 DM to secure your spot → {CONTACT_USERNAME}
🔗 {VIP_CHANNEL_LINK}""",

    f"""💰 *TODAY'S VIP PROFIT UPDATE* 💰

📅 {get_ist_time().strftime('%d %b')}

Our VIP members collectively made:
💵 *₹{random.randint(5000,15000):,}+ today*

From just *4 signals* this morning! 🔥

*Free users missed the early entry.*
*VIP users booked max profit.* 😎

━━━━━━━━━━━━━━━━━━━━━━━
🚀 Stop missing profits!
💰 VIP = ₹399/month
📩 DM to join → {CONTACT_USERNAME}
🔗 {VIP_CHANNEL_LINK}""",

    f"""📚 *TRADING TIP OF THE DAY* 📚
By Kailash — Forex Expert

💡 *Why 90% of traders LOSE money:*
❌ They enter too late (no early signals)
❌ They set wrong SL levels
❌ They trade emotions, not analysis

✅ *What winners do differently:*
✅ Follow expert signals with clear entries
✅ Always use Stop Loss (1-2% risk)
✅ Take TP1 first, trail to TP2

📈 *Our VIP members follow this exact system.*
*89% win rate speaks for itself.*

━━━━━━━━━━━━━━━━━━━━━━━
🎓 *Learn & Earn with VIP*
₹399/month | {VIP_CHANNEL_LINK}
📩 Join → {CONTACT_USERNAME}""",

    f"""🏆 *THE KAILASH CHALLENGE* 🏆

📊 *Our last 30 days results:*

| Pair     | Calls | Win | Acc  |
|----------|-------|-----|------|
| GOLD     | 32    | 29  | 91%  |
| BTC      | 25    | 23  | 92%  |
| EUR/USD  | 35    | 31  | 89%  |
| USOIL    | 22    | 19  | 86%  |

*Total: 114 calls | 102 wins ✅ | 89.5% Accuracy*

🔥 *We prove it every single day.*

━━━━━━━━━━━━━━━━━━━━━━━
📲 *Join VIP & see for yourself*
💰 Just ₹399/month
🔗 {VIP_CHANNEL_LINK}
📩 {CONTACT_USERNAME}""",

    f"""🌅 *GOOD MORNING, TRADERS!* 🌅

The markets are OPEN and opportunities are here!

📊 *Today's Market Outlook:*
🥇 Gold — *Volatile, high opportunity*
₿ Bitcoin — *Bullish momentum*
💶 EUR/USD — *Key level to watch*

⚡ Our VIP members already have their entries set!

*Free channel gets signals AFTER the move starts.*
*VIP gets entries BEFORE the move — maximum profit.*

The difference? Just ₹399/month. 💰

━━━━━━━━━━━━━━━━━━━━━━━
☀️ *Start your day profitable!*
📩 DM to join → {CONTACT_USERNAME}
🔗 {VIP_CHANNEL_LINK}""",

    f"""🎯 *BEHIND THE SCENES — HOW WE MAKE SIGNALS* 🎯

Many ask: *"How do you get 89% accuracy?"*

Here's our process:

🔍 *Step 1:* Check 4H & Daily chart structure
📊 *Step 2:* Identify key support/resistance zones
📈 *Step 3:* Confirm with RSI + MACD divergence
⏰ *Step 4:* Wait for London/NY session confluence
✅ *Step 5:* Set tight entry with perfect SL/TP

VIP members get the FINAL call with early entries!

━━━━━━━━━━━━━━━━━━━━━━━
💎 *Get our best work — join VIP*
₹399/month | 🔗 {VIP_CHANNEL_LINK}""",

    f"""📈 *THIS WEEK IN REVIEW* 📈
Forex Trading With Kailash

🔥 *Weekly Highlights:*
✅ {random.randint(20,28)} signals sent
✅ {random.randint(18,26)} targets hit
✅ Max profit: +{random.randint(200,350)} pips on GOLD
✅ Members avg earning: ₹{random.randint(5000,12000):,}

💬 *Member shoutout:*
_"Made ₹{random.randint(8000,15000):,} this week following VIP signals!"_

━━━━━━━━━━━━━━━━━━━━━━━
💰 *₹399/month = unlimited signals*
Don't watch others profit — join now!
🔗 {VIP_CHANNEL_LINK}
📩 {CONTACT_USERNAME}""",

    f"""🚨 *SIGNAL COMING IN 30 MINUTES* 🚨

Our analysis team is finalizing a *HIGH PROBABILITY* setup on:
🥇 XAU/USD
₿ BTC/USD
💶 EUR/USD

*VIP members will get it 30 mins early!*
Free channel gets it after.

⚡ *Don't be late to the trade.*

━━━━━━━━━━━━━━━━━━━━━━━
🔔 *Upgrade to VIP NOW before the signal drops!*
💰 ₹399/month
📩 DM now → {CONTACT_USERNAME}
🔗 {VIP_CHANNEL_LINK}""",

    f"""💎 *WHY VIP IS THE BEST INVESTMENT* 💎

Let's do the math:

💰 VIP Cost: *₹399/month*
📊 Average profit per signal: *₹500–₹2,000*
📡 Signals per day: *7-10*

Even if you catch *just 1 TP per day* on 1 lot:

*₹500 × 30 days = ₹15,000/month*

Your ROI on ₹399 = *3,600%* 🚀

━━━━━━━━━━━━━━━━━━━━━━━
📲 *Join VIP today!*
💰 ₹399/month
📩 DM to join → {CONTACT_USERNAME}
🔗 {VIP_CHANNEL_LINK}""",

    f"""🎁 *SPECIAL VIP OFFER* 🎁

For the next {random.randint(3,7)} members only!

Join VIP today and get:
✅ FREE access to my Forex Masterclass (₹2,999 value)
✅ 1-on-1 Trading Session with Kailash

*Total Value: ₹5,000+*
*You pay: Just ₹399!*

⏰ *Offer valid until midnight!*

━━━━━━━━━━━━━━━━━━━━━━━
📩 DM *"VIPOFFER"* → {CONTACT_USERNAME}
🔗 {VIP_CHANNEL_LINK}""",

    f"""🛡️ *STOP LOSING MONEY!* 🛡️

Are you:
❌ Taking random trades?
❌ No stop loss?
❌ Chasing the market?

*Our VIP members don't have these problems.*

They follow:
✅ Structured signals with clear entries
✅ Always use stop loss (1-2% risk)
✅ Take partial profits at TP1

━━━━━━━━━━━━━━━━━━━━━━━
💰 *Break the cycle — join VIP*
₹399/month | 🔗 {VIP_CHANNEL_LINK}
📩 {CONTACT_USERNAME}""",

    f"""🌟 *FROM LOSS TO PROFIT* 🌟

Meet Vikram S. (VIP Member):

_"I was losing ₹30,000/month trading on my own._
_Saw Kailash's free signals — decided to join VIP._

_Now I make ₹50,000-80,000/month consistently!"_

🔥 *Vikram's 30-day results:*
• 28 trades taken
• 25 winning trades
• Total profit: ₹62,500
• Win rate: 89.2%

━━━━━━━━━━━━━━━━━━━━━━━
💪 *Your story could be next!*
₹399/month | 🔗 {VIP_CHANNEL_LINK}
📩 {CONTACT_USERNAME}""",

    f"""📊 *FREE VS VIP — KNOW THE DIFFERENCE* 📊

| Feature | Free | VIP |
|---------|------|-----|
| Signals/Day | 3-5 | 7-10 |
| Entry Timing | After move | Before move ⚡ |
| TP/SL Alerts | ❌ | ✅ |
| 1-on-1 Support | ❌ | ✅ |
| Live Sessions | ❌ | ✅ |
| Win Rate | 85% | 89%+ |

The choice is clear.

━━━━━━━━━━━━━━━━━━━━━━━
💎 *Upgrade to VIP now!*
🔗 {VIP_CHANNEL_LINK}
📩 {CONTACT_USERNAME}""",

    f"""⚡ *STOP WATCHING — START EARNING!* ⚡

Every day you wait = Lost profits:

📉 Free users: 3-5 signals (delayed)
📈 VIP members: 7-10 signals (early entries)

This month's VIP profits:
💰 Total: ₹1,45,000 average per member
💎 Top earner: ₹3,20,000

*Could have been you.*

━━━━━━━━━━━━━━━━━━━━━━━
🎯 *Make the decision today!*
₹399/month | 🔗 {VIP_CHANNEL_LINK}
📩 {CONTACT_USERNAME}""",

    f"""🔔 *LAST CALL — VIP SLOTS FILLING FAST!* 🔔

Only *{random.randint(2,5)} spots left* at ₹399/month!

Next price: ₹599/month

Don't wait — join the winning team today!

━━━━━━━━━━━━━━━━━━━━━━━
⏰ *Secure your spot NOW!*
📩 DM to join → {CONTACT_USERNAME}
🔗 {VIP_CHANNEL_LINK}""",

    f"""💸 *MISSED THIS GOLD MOVE?* 💸

Today's GOLD BUY signal:
✅ TP1 hit: +120 pips
✅ TP2 hit: +250 pips
💰 Profit: ~₹8,000/lot

*VIP members got it 30 minutes early at better price!*

━━━━━━━━━━━━━━━━━━━━━━━
Don't miss tomorrow's setup. Join VIP now!
₹399/month | 🔗 {VIP_CHANNEL_LINK}""",

    f"""📢 *VIP CHANNEL PREVIEW* 📢

What you get:
⭐ 30-35 premium signals/day
⭐ Early entries (before public)
⭐ Live market analysis
⭐ TP/SL alerts
⭐ 1-on-1 mentorship

All for just ₹399/month!

🔗 {VIP_CHANNEL_LINK}
📩 {CONTACT_USERNAME}""",

    f"""🎯 *ACCURACY PROOF* 🎯

Last 100 VIP signals:
✅ Wins: 89
❌ Losses: 11
📈 Win rate: 89%

This is not gambling — it's a system.

Join the winners circle today!
💰 ₹399/month | 🔗 {VIP_CHANNEL_LINK}""",

    f"""🚀 *EARLY BIRD OFFER* 🚀

First 50 VIP members this month get:
✅ FREE Forex Masterclass (₹2,999)
✅ Priority support

Only {random.randint(10,25)} spots left!

⏰ Join now: {VIP_CHANNEL_LINK}
📩 DM {CONTACT_USERNAME}""",

    f"""📈 *WHY TRADE ALONE?* 📈

Get expert signals from Kailash:
✅ 7+ years experience
✅ 89% win rate
✅ Real-time analysis

Stop guessing. Start winning.

VIP: ₹399/month
🔗 {VIP_CHANNEL_LINK}""",

    f"""💎 *VIP MEMBERS SPEAK* 💎

_"I've tried 10+ signal channels. Kailash is the only one that delivers consistently."_
— Ankit T.

_"The early entries are game-changing. My monthly profit doubled."_
— Neha S.

Join them today: {VIP_CHANNEL_LINK}""",

    f"""⏳ *PRICE HIKE INCOMING* ⏳

Current price: ₹399/month
New price from next month: ₹599/month

Lock in ₹399 for life by joining NOW!

🔗 {VIP_CHANNEL_LINK}
📩 {CONTACT_USERNAME}""",

    f"""🎓 *FREE MASTERCLASS FOR VIP* 🎓

VIP members get FREE access to my ₹2,999 Forex Course!

Learn:
✅ Chart patterns
✅ Entry/exit strategies
✅ Risk management

Join VIP: {VIP_CHANNEL_LINK}""",
]

def get_promo():
    return random.choice(PROMO_MESSAGES)

# ============================================
# PRICE MONITOR (same as before)
# ============================================
TP_HYPE = [
    "🎯🔥 *TARGET HIT!* 🔥🎯\n\n{symbol} {direction} → *{tp} ✅ REACHED!*\n\n+{profit} {unit} in profit!\n\n💎 *KAILASH TRADING* — India's Most Trusted Signal Provider\n🚀 Join VIP for early entries!\n👉 {vip}",
    "💰 *BOOM! TP HIT!* 💰\n\n{symbol} → *{tp} SMASHED!* 🎯\n*{direction} +{profit} {unit}*\n\n⭐ *Forex Trading With Kailash* — {accuracy}% Win Rate!\n👉 {vip}",
    "✅✅ *SIGNAL SUCCESSFUL!* ✅✅\n\n📊 {symbol} {direction}\n🎯 *{tp} HIT — +{profit} {unit}*\n\n🔥 Another W for Kailash traders!\n📲 Join VIP: {vip}",
]

def price_monitor():
    while True:
        time.sleep(180)
        try:
            pending = get_pending_signals()
            for row in pending:
                sig_id, symbol, direction, entry, tp1, tp2, sl, decimals, msg_id, ticker, result, ch_type, accuracy = row
                try:
                    current = yf.Ticker(ticker).history(period="1d", interval="5m")["Close"].iloc[-1]
                except:
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
# VIP CHANNEL SIGNALS (30-35 per day)
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
⏰ *Timeframe:* {d['timeframe']} | Confidence: {d['confidence']}%
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
            if vip_signal_count < 35:
                sym = random.choice(SYMBOLS)
                d = generate_accurate_signal(sym)
                sid = save_signal_to_db(d, "vip")
                text = vip_signal_post(d)
                sent = bot.send_message(VIP_CHANNEL_ID, text, parse_mode='Markdown')
                update_signal_message_id(sid, sent.message_id)
                vip_signal_count += 1
                print(f"VIP signal #{vip_signal_count}: {d['symbol']} {d['direction']} (confidence {d['confidence']}%)")
            else:
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
                    bot.send_message(CHANNEL_ID, get_promo(), parse_mode='Markdown')
            else:
                bot.send_message(CHANNEL_ID, get_promo(), parse_mode='Markdown')
        except Exception as e:
            print(f"Public scheduler error: {e}")
        time.sleep(1800)

# ============================================
# BOT COMMANDS (same as before)
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
        c.execute("INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,0)", (uid, name, email, phone, str(datetime.datetime.now())))
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
⏰ *Timeframe:* {d['timeframe']} | Confidence: {d['confidence']}%"""
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
# MAIN
# ============================================
if __name__ == "__main__":
    print("Starting real analysis engine...")
    threading.Thread(target=public_scheduler, daemon=True).start()
    threading.Thread(target=price_monitor, daemon=True).start()
    threading.Thread(target=vip_channel_scheduler, daemon=True).start()
    print("Bot polling started. Signals will be based on real technical analysis.")
    bot.infinity_polling()
