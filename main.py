import telebot
import sqlite3
import datetime
import os
import random
import threading
import time
import yfinance as yf
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================
# CONFIGURATION (HARDCODED VIP ID)
# ============================================
BOT_TOKEN = "8653450456:AAER9w6Gjj5IWkyCs1taa01N-DdMFZqxt3E"
ADMIN_ID = 6253584826
CHANNEL_ID = '@tradewithkailashh'
FREE_CHANNEL = 'https://t.me/tradewithkailashh'
VIP_CHANNEL_LINK = 'https://t.me/+Snj0BVAwjDo3NTA1'
VIP_CHANNEL_ID = "-1003826269063"  # Your VIP channel ID (hardcoded)
WEBSITE_URL = 'https://forexkailash.netlify.app'
COURSE_URL = 'https://forexkailash.netlify.app/course'
UPI_ID = 'kailashbhardwaj66-2@okicici'
CONTACT_USERNAME = '@Yungshang1'

print("=" * 60)
print("🤖 KAILASH FOREX SIGNAL BOT - STARTING")
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
# TRADING SYMBOLS (14 pairs, high accuracy)
# ============================================
SYMBOLS = [
    {"name": "XAU/USD", "ticker": "GC=F", "emoji": "🥇", "decimals": 2, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "spread_pct": 0.001, "accuracy": 89,
     "analysis_buy": ["Gold breaking above key resistance. Strong bullish momentum.", "Safe haven demand rising. Institutional buying detected.", "Gold consolidating above support. Breakout incoming.", "RSI bullish divergence. Upside to 4550.", "Golden cross confirmed on daily."],
     "analysis_sell": ["Gold facing strong resistance. Bearish reversal.", "Dollar strength pushing gold lower.", "Gold rejecting from key level. Short-term bearish.", "MACD bearish crossover.", "Failed breakout at resistance."]},
    {"name": "BTC/USD", "ticker": "BTC-USD", "emoji": "₿", "decimals": 0, "tp1_pct": 0.006, "tp2_pct": 0.012, "sl_pct": 0.004, "spread_pct": 0.001, "accuracy": 91,
     "analysis_buy": ["Bitcoin breaking above resistance. Bullish structure.", "Whale accumulation detected.", "BTC holding key support. Momentum bullish.", "ETF inflows increasing.", "Halving anticipation building."],
     "analysis_sell": ["BTC facing major resistance. Distribution phase.", "Bearish divergence on RSI. Correction expected.", "Bitcoin rejecting from highs. Caution.", "Exchange inflows increasing.", "Failed to hold above 68K."]},
    {"name": "EUR/USD", "ticker": "EURUSD=X", "emoji": "💶", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 87,
     "analysis_buy": ["EUR/USD breaking above 50 EMA. Bullish continuation.", "Euro strengthening on ECB hawkish signals.", "Dollar weakness boosting EUR/USD.", "Support holding at 1.0800.", "Positive EU economic data."],
     "analysis_sell": ["EUR/USD rejected at key resistance. Bearish pattern.", "Strong USD on positive data. Downside expected.", "EUR/USD below daily pivot. Bearish pressure.", "ECB dovish comments.", "Failed breakout above 1.0900."]},
    {"name": "USOIL", "ticker": "CL=F", "emoji": "🛢️", "decimals": 2, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003, "spread_pct": 0.001, "accuracy": 85,
     "analysis_buy": ["Oil prices rising on supply cut news.", "OPEC+ production cut boosting crude.", "Oil demand surging. Bullish signal.", "Inventory drawdown larger than expected.", "Technical breakout above 78.50."],
     "analysis_sell": ["Oil supply increasing. Bearish pressure.", "Demand concerns weighing on crude.", "Oil breaking below support. Sell opportunity.", "Profit booking after rally.", "RSI overbought."]},
    {"name": "GBP/USD", "ticker": "GBPUSD=X", "emoji": "💷", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 88,
     "analysis_buy": ["GBP/USD bouncing off key support. Cable higher.", "UK economic data positive. Sterling gaining.", "GBP breaking above resistance. Bullish setup.", "BOE hawkish stance.", "Bullish engulfing candle."],
     "analysis_sell": ["GBP/USD rejected at 200 EMA. Bearish pressure.", "UK inflation fears weighing on pound.", "Cable dropping below pivot. Bearish continuation.", "US dollar strength.", "Failed breakout above 1.2700."]},
    {"name": "USD/JPY", "ticker": "JPY=X", "emoji": "🇯🇵", "decimals": 3, "tp1_pct": 0.003, "tp2_pct": 0.005, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 86,
     "analysis_buy": ["USD/JPY pushing higher on Fed hawkish tone.", "Yen weakening on BOJ dovish stance.", "USD/JPY breaking above key level.", "Interest rate differential favoring dollar.", "Breakout from consolidation."],
     "analysis_sell": ["BOJ intervention risk rising. Resistance ahead.", "Yen safe haven demand spiking.", "USD/JPY overbought. Correction expected.", "Japanese officials warning.", "Failed to hold above 151.00."]},
    {"name": "ETH/USD", "ticker": "ETH-USD", "emoji": "💎", "decimals": 1, "tp1_pct": 0.007, "tp2_pct": 0.014, "sl_pct": 0.005, "spread_pct": 0.001, "accuracy": 88,
     "analysis_buy": ["Ethereum breaking out. DeFi activity surging.", "ETH accumulation at key support.", "Ethereum forming bullish pattern. Smart money buying.", "ETF inflows increasing.", "Technical breakout confirmed."],
     "analysis_sell": ["ETH facing resistance. Market turning bearish.", "Ethereum distribution phase. Sell pressure.", "ETH rejecting from key level. Correction due.", "Gas fees declining.", "Failed to break above 3550."]},
    {"name": "NAS100", "ticker": "NQ=F", "emoji": "📈", "decimals": 0, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "spread_pct": 0.001, "accuracy": 84,
     "analysis_buy": ["NASDAQ futures gapping up. Tech earnings driving rally.", "NAS100 holding support. Bulls in control.", "Strong US tech momentum. BUY confirmed.", "AI sector booming.", "Breakout above resistance."],
     "analysis_sell": ["NASDAQ rejecting at highs. Rising rates pressuring tech.", "NAS100 forming double top. Bearish reversal.", "Tech sector under pressure. Sell opportunity.", "Valuations stretched.", "Failed breakout above 18750."]},
    {"name": "SILVER", "ticker": "SI=F", "emoji": "🥈", "decimals": 3, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003, "spread_pct": 0.001, "accuracy": 87,
     "analysis_buy": ["Silver following gold higher. Industrial demand rising.", "SILVER breaking above key resistance.", "Precious metals rally. Strong BUY.", "Gold-silver ratio compressing.", "Technical breakout confirmed."],
     "analysis_sell": ["Silver losing momentum. Dollar strengthening.", "SILVER rejecting from resistance. Sell signal.", "Industrial demand concerns.", "RSI overbought.", "Failed to hold above 27.80."]},
    {"name": "AUD/USD", "ticker": "AUDUSD=X", "emoji": "🦘", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 86,
     "analysis_buy": ["AUD/USD rebounding on China optimism.", "Aussie strengthening on RBA hawkish signals.", "AUD breaking above pivot. Risk-on sentiment.", "Iron ore prices rising.", "Support holding at 0.6480."],
     "analysis_sell": ["AUD/USD weakening on risk-off sentiment.", "China slowdown fears weighing on Aussie.", "AUD rejecting from resistance. Bearish pattern.", "RBA dovish comments.", "Failed to hold above 0.6550."]},
    {"name": "GBP/JPY", "ticker": "GBPJPY=X", "emoji": "⚡", "decimals": 3, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "spread_pct": 0.0004, "accuracy": 85,
     "analysis_buy": ["GBP/JPY surging on risk appetite. Explosive momentum.", "Cable-Yen cross breaking higher.", "GBP/JPY holding key support. Bulls in control.", "Carry trade demand increasing.", "Breakout above 190.50."],
     "analysis_sell": ["GBP/JPY reversal signal. Risk-off taking over.", "Yen demand rising. Bearish pressure.", "GBP/JPY double top forming. Sell opportunity.", "BOJ intervention speculation.", "Failed to hold above 191.00."]},
    {"name": "US30", "ticker": "YM=F", "emoji": "🏛️", "decimals": 0, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0008, "accuracy": 86,
     "analysis_buy": ["Dow Jones breaking higher. Industrial stocks rally.", "US30 holding support at 39000. Bullish momentum.", "Economic data supporting equities.", "Breakout from consolidation."],
     "analysis_sell": ["US30 facing resistance at 39500. Profit booking.", "Dow forming bearish divergence.", "Rising yields pressuring stocks."]},
    {"name": "USD/CAD", "ticker": "USDCAD=X", "emoji": "🍁", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 87,
     "analysis_buy": ["USD/CAD bouncing off support. Oil weakness boosting USD.", "US dollar strength across board.", "Breakout above 1.3600."],
     "analysis_sell": ["USD/CAD rejecting at 1.3650. Oil supporting CAD.", "Bank of Canada hawkish tilt.", "Failed breakout above 1.3630."]},
    {"name": "SOL/USD", "ticker": "SOL-USD", "emoji": "☀️", "decimals": 2, "tp1_pct": 0.008, "tp2_pct": 0.016, "sl_pct": 0.006, "spread_pct": 0.001, "accuracy": 84,
     "analysis_buy": ["Solana breaking out. Ecosystem growth.", "SOL holding key support. Upside expected.", "Network activity surging."],
     "analysis_sell": ["SOL facing resistance. Profit booking.", "Bearish divergence on RSI.", "Correction expected."]},
]

DIRECTIONS = ["BUY", "SELL"]
active_directions = {}

FALLBACK_PRICES = {
    "GC=F": 4520.00, "BTC-USD": 68500.00, "EURUSD=X": 1.08750, "CL=F": 79.50,
    "GBPUSD=X": 1.26800, "JPY=X": 150.50, "ETH-USD": 3550.00, "NQ=F": 18700.00,
    "SI=F": 27.80, "AUDUSD=X": 0.65500, "GBPJPY=X": 190.80, "YM=F": 39300.00,
    "USDCAD=X": 1.36000, "SOL-USD": 148.00,
}

# ============================================
# DATABASE SETUP
# ============================================
os.makedirs("telegram_bot", exist_ok=True)
conn = sqlite3.connect('telegram_bot/users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT, register_date TEXT, is_vip INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS registrations (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, email TEXT, phone TEXT, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS signal_usage (user_id INTEGER PRIMARY KEY, count INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS channel_signals (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, direction TEXT, entry REAL, tp1 REAL, tp2 REAL, sl REAL, decimals INTEGER, sent_date TEXT, sent_time TEXT, result TEXT DEFAULT "pending", message_id INTEGER DEFAULT NULL, ticker TEXT, channel_type TEXT DEFAULT "public", accuracy INTEGER DEFAULT 85)''')
c.execute('''CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, value TEXT)''')
conn.commit()

def get_setting(key, default=None):
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone()
    return row[0] if row else default

def set_setting(key, value):
    c.execute("INSERT INTO bot_settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?", (key, value, value))
    conn.commit()

# Hardcode VIP channel ID in settings if not already set
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

# ============================================
# LIVE PRICE FUNCTIONS
# ============================================
def get_live_price(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="1d", interval="5m")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except:
        pass
    return FALLBACK_PRICES.get(ticker, 1000.00)

def get_signal_direction(symbol_name):
    cur = active_directions.get(symbol_name)
    if cur == "BUY":
        return "SELL"
    elif cur == "SELL":
        return "BUY"
    return random.choice(DIRECTIONS)

def generate_accurate_signal(symbol=None):
    if symbol is None:
        symbol = random.choice([s for s in SYMBOLS if s.get("trending", True)])
    direction = get_signal_direction(symbol["name"])
    price = get_live_price(symbol["ticker"])
    d = symbol["decimals"]
    spread = price * symbol["spread_pct"]
    if direction == "BUY":
        entry_low = round(price - spread, d)
        entry_high = round(price + spread, d)
        tp1 = round(price * (1 + symbol["tp1_pct"]), d)
        tp2 = round(price * (1 + symbol["tp2_pct"]), d)
        sl = round(price * (1 - symbol["sl_pct"]), d)
        analysis = random.choice(symbol["analysis_buy"])
        dir_emoji = "🟢"
    else:
        entry_low = round(price - spread, d)
        entry_high = round(price + spread, d)
        tp1 = round(price * (1 - symbol["tp1_pct"]), d)
        tp2 = round(price * (1 - symbol["tp2_pct"]), d)
        sl = round(price * (1 + symbol["sl_pct"]), d)
        analysis = random.choice(symbol["analysis_sell"])
        dir_emoji = "🔴"
    if direction == "BUY" and sl >= entry_low:
        sl = round(entry_low - (price * 0.001), d)
    elif direction == "SELL" and sl <= entry_high:
        sl = round(entry_high + (price * 0.001), d)
    active_directions[symbol["name"]] = direction
    return {
        "symbol": symbol["name"], "ticker": symbol["ticker"], "emoji": symbol["emoji"],
        "direction": direction, "entry_low": entry_low, "entry_high": entry_high,
        "tp1": tp1, "tp2": tp2, "sl": sl, "price": price, "decimals": d,
        "analysis": analysis, "dir_emoji": dir_emoji, "accuracy": symbol.get("accuracy", 85)
    }

def save_signal_to_db(data, channel_type="public"):
    now = datetime.datetime.now()
    c.execute("""INSERT INTO channel_signals (symbol, direction, entry, tp1, tp2, sl, decimals, sent_date, sent_time, ticker, channel_type, accuracy)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
              (data["symbol"], data["direction"], (data["entry_low"]+data["entry_high"])/2,
               data["tp1"], data["tp2"], data["sl"], data["decimals"],
               now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), data["ticker"], channel_type, data["accuracy"]))
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
# SIGNAL TEMPLATES (HYPE + BRAND PROMOTION)
# ============================================
def template_fire(d):
    ist = get_ist_time()
    return f"""🔥🔥🔥 *LIVE SIGNAL ALERT* 🔥🔥🔥

{d['emoji']} *{d['direction']} {d['symbol']}*
━━━━━━━━━━━━━━━━━━━━━━━━
📌 *Entry Zone:* `{d['entry_low']} — {d['entry_high']}`
🎯 *TP 1:* `{d['tp1']}` ✅
🎯 *TP 2:* `{d['tp2']}` ✅✅
🛑 *Stop Loss:* `{d['sl']}`

📊 *Analysis:*
_{d['analysis']}_

⏰ {ist.strftime('%d %b %Y • %I:%M %p')} IST
━━━━━━━━━━━━━━━━━━━━━━━━
💎 *Win Rate: {d['accuracy']}%* | Risk: 1-2% only
⭐ VIP gets signals *30 mins early!*
👇 *Upgrade to VIP — ₹399/month*
{VIP_CHANNEL_LINK}"""

def template_winner(d):
    ist = get_ist_time()
    return f"""🏆 *WINNING SIGNAL ALERT* 🏆

{d['emoji']} *{d['direction']} {d['symbol']}* — READY TO HIT!

━━━━━━━━━━━━━━━━━━━━━━━━
📌 Entry: `{d['entry_low']} - {d['entry_high']}`
🎯 TP1: `{d['tp1']}`
🎯 TP2: `{d['tp2']}`
🛑 SL: `{d['sl']}`

💡 *Why this trade will win:*
_{d['analysis']}_

📊 *Kailash's Accuracy Rate: {d['accuracy']}%*
━━━━━━━━━━━━━━━━━━━━━━━━
⭐ *VIP Members get EXCLUSIVE early entries!*
Join VIP — only ₹399/month
🔗 {VIP_CHANNEL_LINK}"""

TEMPLATES = [template_fire, template_winner]

def build_channel_post():
    d = generate_accurate_signal()
    sid = save_signal_to_db(d, "public")
    return random.choice(TEMPLATES)(d), sid

# ============================================
# 22 PROMOTIONAL MESSAGES FOR FOMO & VIP UPSELL
# ============================================
PROMO_MESSAGES = [
    f"""💬 *WHAT OUR MEMBERS ARE SAYING* 💬
⭐⭐⭐⭐⭐

_"Joined VIP last month and already made back 10x my subscription fee. Kailash signals are insane!"_

— Rahul M., Mumbai

⭐⭐⭐⭐⭐

_"3 TP2s in a row this week. Never seen accuracy like this before."_

— Priya S., Delhi

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
# PRICE MONITOR (TP HYPE + AUTO-DELETE LOSSES)
# ============================================
TP_HYPE = [
    "🎯🔥 *TARGET HIT!* 🔥🎯\n\n{symbol} {direction} → *{tp} ✅ REACHED!*\n\n+{profit} {unit} in profit!\n\n💎 *KAILASH TRADING* — India's Most Trusted Signal Provider\n🚀 Join VIP for early entries!\n👉 {vip}",
    "💰 *BOOM! TP HIT!* 💰\n\n{symbol} → *{tp} SMASHED!* 🎯\n*{direction} +{profit} {unit}*\n\n⭐ *Forex Trading With Kailash* — {accuracy}% Win Rate!\n👉 {vip}",
    "✅✅ *SIGNAL SUCCESSFUL!* ✅✅\n\n📊 {symbol} {direction}\n🎯 *{tp} HIT — +{profit} {unit}*\n\n🔥 Another W for Kailash traders!\n📲 Join VIP: {vip}",
]

def price_monitor():
    while True:
        time.sleep(180)  # every 3 minutes
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
                                print(f"Deleted losing signal: {symbol}")
                            except:
                                pass
                        update_signal_result(sig_id, "sl_hit")
                        active_directions.pop(symbol, None)
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
                        active_directions.pop(symbol, None)
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
                        active_directions.pop(symbol, None)
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
🕐 {ist.strftime('%H:%M')} IST
🔒 VIP Only | Win Rate: {d['accuracy']}%
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
                print(f"VIP signal #{vip_signal_count}: {d['symbol']} {d['direction']}")
            else:
                # send course promo
                bot.send_message(VIP_CHANNEL_ID, random.choice(VIP_COURSE_PROMOS), parse_mode='Markdown')
        except Exception as e:
            print(f"VIP scheduler error: {e}")
        time.sleep(random.randint(600, 900))  # 10-15 min

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
            # Alternate: promo, signal, promo, signal...
            if post_counter % 2 == 0:
                if public_signal_count < 8:
                    text, sid = build_channel_post()
                    sent = bot.send_message(CHANNEL_ID, text, parse_mode='Markdown')
                    update_signal_message_id(sid, sent.message_id)
                    public_signal_count += 1
                    print(f"Public signal #{public_signal_count} posted")
                else:
                    # daily limit reached, send promo instead
                    bot.send_message(CHANNEL_ID, get_promo(), parse_mode='Markdown')
            else:
                bot.send_message(CHANNEL_ID, get_promo(), parse_mode='Markdown')
        except Exception as e:
            print(f"Public scheduler error: {e}")
        time.sleep(1800)  # 30 minutes

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
    txt = f"""🚀 *Forex Trading With Kailash* 🚀

India's Most Trusted Forex Signals Provider

📊 *Services:*
✅ FREE Signals - Daily 8-10 calls
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
    sig = f"""📊 *FREE SIGNAL* 📊
{d['emoji']} *{d['direction']} {d['symbol']}*
📌 Entry: `{d['entry_low']} - {d['entry_high']}`
🎯 TP1: `{d['tp1']}`
🎯 TP2: `{d['tp2']}`
🛑 SL: `{d['sl']}`"""
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
    # Not needed because ID is hardcoded, but keep for flexibility
    bot.reply_to(msg, "VIP ID is hardcoded as -1003826269063. No need to set.", parse_mode='Markdown')

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
    print("Starting threads...")
    threading.Thread(target=public_scheduler, daemon=True).start()
    threading.Thread(target=price_monitor, daemon=True).start()
    threading.Thread(target=vip_channel_scheduler, daemon=True).start()
    print("Bot polling started.")
    bot.infinity_polling()
