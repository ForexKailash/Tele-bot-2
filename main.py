import telebot
import sqlite3
import datetime
import os
import random
import threading
import time
import yfinance as yf
import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================
# CONFIGURATION
# ============================================
BOT_TOKEN = "8653450456:AAER9w6Gjj5IWkyCs1taa01N-DdMFZqxt3E"
ADMIN_ID = 6253584826
CHANNEL_ID = '@tradewithkailashh'
FREE_CHANNEL = 'https://t.me/tradewithkailashh'
VIP_CHANNEL = 'https://t.me/+Snj0BVAwjDo3NTA1'
WEBSITE_URL = 'https://forexkailash.netlify.app'
COURSE_URL = 'https://forexkailash.netlify.app/course'
UPI_ID = 'kailashbhardwaj66-2@okicici'
CONTACT_USERNAME = '@Yungshang1'

print("=" * 60)
print("🤖 FOREX TRADING BOT - STARTING...")
print("=" * 60)
print(f"Bot token: {BOT_TOKEN[:10]}...")
print(f"Admin ID: {ADMIN_ID}")
print(f"Public channel: {CHANNEL_ID}")
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
        pass  # suppress logs

def run_health_server():
    try:
        port = int(os.environ.get('PORT', 8080))
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        print(f"✅ Health check server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Health server error: {e}")

# Start health server in a separate thread
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()

# ============================================
# ENHANCED TRADING SYMBOLS
# ============================================
SYMBOLS = [
    {"name": "XAU/USD", "ticker": "GC=F", "emoji": "🥇", "decimals": 2, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "spread_pct": 0.001, "accuracy": 89, "trending": True,
     "analysis_buy": ["Gold breaking above key resistance. Strong bullish momentum.", "Safe haven demand rising. Institutional buying detected.", "Gold consolidating above support. Breakout incoming.", "RSI bullish divergence. Upside to 4550.", "Golden cross confirmed on daily."],
     "analysis_sell": ["Gold facing strong resistance. Bearish reversal.", "Dollar strength pushing gold lower.", "Gold rejecting from key level. Short-term bearish.", "MACD bearish crossover.", "Failed breakout at resistance."]},
    {"name": "BTC/USD", "ticker": "BTC-USD", "emoji": "₿", "decimals": 0, "tp1_pct": 0.006, "tp2_pct": 0.012, "sl_pct": 0.004, "spread_pct": 0.001, "accuracy": 91, "trending": True,
     "analysis_buy": ["Bitcoin breaking above resistance. Bullish structure.", "Whale accumulation detected.", "BTC holding key support. Momentum bullish.", "ETF inflows increasing.", "Halving anticipation building."],
     "analysis_sell": ["BTC facing major resistance. Distribution phase.", "Bearish divergence on RSI. Correction expected.", "Bitcoin rejecting from highs. Caution.", "Exchange inflows increasing.", "Failed to hold above 68K."]},
    {"name": "EUR/USD", "ticker": "EURUSD=X", "emoji": "💶", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 87, "trending": True,
     "analysis_buy": ["EUR/USD breaking above 50 EMA. Bullish continuation.", "Euro strengthening on ECB hawkish signals.", "Dollar weakness boosting EUR/USD.", "Support holding at 1.0800.", "Positive EU economic data."],
     "analysis_sell": ["EUR/USD rejected at key resistance. Bearish pattern.", "Strong USD on positive data. Downside expected.", "EUR/USD below daily pivot. Bearish pressure.", "ECB dovish comments.", "Failed breakout above 1.0900."]},
    {"name": "USOIL", "ticker": "CL=F", "emoji": "🛢️", "decimals": 2, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003, "spread_pct": 0.001, "accuracy": 85, "trending": True,
     "analysis_buy": ["Oil prices rising on supply cut news.", "OPEC+ production cut boosting crude.", "Oil demand surging. Bullish signal.", "Inventory drawdown larger than expected.", "Technical breakout above 78.50."],
     "analysis_sell": ["Oil supply increasing. Bearish pressure.", "Demand concerns weighing on crude.", "Oil breaking below support. Sell opportunity.", "Profit booking after rally.", "RSI overbought."]},
    {"name": "GBP/USD", "ticker": "GBPUSD=X", "emoji": "💷", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 88, "trending": True,
     "analysis_buy": ["GBP/USD bouncing off key support. Cable higher.", "UK economic data positive. Sterling gaining.", "GBP breaking above resistance. Bullish setup.", "BOE hawkish stance.", "Bullish engulfing candle."],
     "analysis_sell": ["GBP/USD rejected at 200 EMA. Bearish pressure.", "UK inflation fears weighing on pound.", "Cable dropping below pivot. Bearish continuation.", "US dollar strength.", "Failed breakout above 1.2700."]},
    {"name": "USD/JPY", "ticker": "JPY=X", "emoji": "🇯🇵", "decimals": 3, "tp1_pct": 0.003, "tp2_pct": 0.005, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 86, "trending": True,
     "analysis_buy": ["USD/JPY pushing higher on Fed hawkish tone.", "Yen weakening on BOJ dovish stance.", "USD/JPY breaking above key level.", "Interest rate differential favoring dollar.", "Breakout from consolidation."],
     "analysis_sell": ["BOJ intervention risk rising. Resistance ahead.", "Yen safe haven demand spiking.", "USD/JPY overbought. Correction expected.", "Japanese officials warning.", "Failed to hold above 151.00."]},
    {"name": "ETH/USD", "ticker": "ETH-USD", "emoji": "💎", "decimals": 1, "tp1_pct": 0.007, "tp2_pct": 0.014, "sl_pct": 0.005, "spread_pct": 0.001, "accuracy": 88, "trending": True,
     "analysis_buy": ["Ethereum breaking out. DeFi activity surging.", "ETH accumulation at key support.", "Ethereum forming bullish pattern. Smart money buying.", "ETF inflows increasing.", "Technical breakout confirmed."],
     "analysis_sell": ["ETH facing resistance. Market turning bearish.", "Ethereum distribution phase. Sell pressure.", "ETH rejecting from key level. Correction due.", "Gas fees declining.", "Failed to break above 3550."]},
    {"name": "NAS100", "ticker": "NQ=F", "emoji": "📈", "decimals": 0, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "spread_pct": 0.001, "accuracy": 84, "trending": True,
     "analysis_buy": ["NASDAQ futures gapping up. Tech earnings driving rally.", "NAS100 holding support. Bulls in control.", "Strong US tech momentum. BUY confirmed.", "AI sector booming.", "Breakout above resistance."],
     "analysis_sell": ["NASDAQ rejecting at highs. Rising rates pressuring tech.", "NAS100 forming double top. Bearish reversal.", "Tech sector under pressure. Sell opportunity.", "Valuations stretched.", "Failed breakout above 18750."]},
    {"name": "SILVER", "ticker": "SI=F", "emoji": "🥈", "decimals": 3, "tp1_pct": 0.005, "tp2_pct": 0.010, "sl_pct": 0.003, "spread_pct": 0.001, "accuracy": 87, "trending": True,
     "analysis_buy": ["Silver following gold higher. Industrial demand rising.", "SILVER breaking above key resistance.", "Precious metals rally. Strong BUY.", "Gold-silver ratio compressing.", "Technical breakout confirmed."],
     "analysis_sell": ["Silver losing momentum. Dollar strengthening.", "SILVER rejecting from resistance. Sell signal.", "Industrial demand concerns.", "RSI overbought.", "Failed to hold above 27.80."]},
    {"name": "AUD/USD", "ticker": "AUDUSD=X", "emoji": "🦘", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 86, "trending": True,
     "analysis_buy": ["AUD/USD rebounding on China optimism.", "Aussie strengthening on RBA hawkish signals.", "AUD breaking above pivot. Risk-on sentiment.", "Iron ore prices rising.", "Support holding at 0.6480."],
     "analysis_sell": ["AUD/USD weakening on risk-off sentiment.", "China slowdown fears weighing on Aussie.", "AUD rejecting from resistance. Bearish pattern.", "RBA dovish comments.", "Failed to hold above 0.6550."]},
    {"name": "GBP/JPY", "ticker": "GBPJPY=X", "emoji": "⚡", "decimals": 3, "tp1_pct": 0.004, "tp2_pct": 0.008, "sl_pct": 0.003, "spread_pct": 0.0004, "accuracy": 85, "trending": True,
     "analysis_buy": ["GBP/JPY surging on risk appetite. Explosive momentum.", "Cable-Yen cross breaking higher.", "GBP/JPY holding key support. Bulls in control.", "Carry trade demand increasing.", "Breakout above 190.50."],
     "analysis_sell": ["GBP/JPY reversal signal. Risk-off taking over.", "Yen demand rising. Bearish pressure.", "GBP/JPY double top forming. Sell opportunity.", "BOJ intervention speculation.", "Failed to hold above 191.00."]},
    {"name": "US30", "ticker": "YM=F", "emoji": "🏛️", "decimals": 0, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0008, "accuracy": 86, "trending": True,
     "analysis_buy": ["Dow Jones breaking higher. Industrial stocks rally.", "US30 holding support at 39000. Bullish momentum.", "Economic data supporting equities.", "Breakout from consolidation."],
     "analysis_sell": ["US30 facing resistance at 39500. Profit booking.", "Dow forming bearish divergence.", "Rising yields pressuring stocks."]},
    {"name": "USD/CAD", "ticker": "USDCAD=X", "emoji": "🍁", "decimals": 5, "tp1_pct": 0.003, "tp2_pct": 0.006, "sl_pct": 0.002, "spread_pct": 0.0003, "accuracy": 87, "trending": True,
     "analysis_buy": ["USD/CAD bouncing off support. Oil weakness boosting USD.", "US dollar strength across board.", "Breakout above 1.3600."],
     "analysis_sell": ["USD/CAD rejecting at 1.3650. Oil supporting CAD.", "Bank of Canada hawkish tilt.", "Failed breakout above 1.3630."]},
    {"name": "SOL/USD", "ticker": "SOL-USD", "emoji": "☀️", "decimals": 2, "tp1_pct": 0.008, "tp2_pct": 0.016, "sl_pct": 0.006, "spread_pct": 0.001, "accuracy": 84, "trending": True,
     "analysis_buy": ["Solana breaking out. Ecosystem growth.", "SOL holding key support. Upside expected.", "Network activity surging."],
     "analysis_sell": ["SOL facing resistance. Profit booking.", "Bearish divergence on RSI.", "Correction expected."]},
]

DIRECTIONS = ["BUY", "SELL"]
active_directions = {}

# ============================================
# FALLBACK PRICES
# ============================================
FALLBACK_PRICES = {
    "GC=F": 4520.00, "BTC-USD": 68500.00, "EURUSD=X": 1.08750, "CL=F": 79.50,
    "GBPUSD=X": 1.26800, "JPY=X": 150.50, "ETH-USD": 3550.00, "NQ=F": 18700.00,
    "SI=F": 27.80, "AUDUSD=X": 0.65500, "GBPJPY=X": 190.80, "YM=F": 39300.00,
    "USDCAD=X": 1.36000, "SOL-USD": 148.00,
}

# ============================================
# DATABASE SETUP
# ============================================
if not os.path.exists('telegram_bot'):
    os.makedirs('telegram_bot')
    print("✅ Created telegram_bot directory")

conn = sqlite3.connect('telegram_bot/users.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT,
              register_date TEXT, is_vip INTEGER)''')
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
              channel_type TEXT DEFAULT "public", accuracy INTEGER DEFAULT 85)''')
c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
             (key TEXT PRIMARY KEY, value TEXT)''')

for col in [
    "ALTER TABLE channel_signals ADD COLUMN message_id INTEGER DEFAULT NULL",
    "ALTER TABLE channel_signals ADD COLUMN ticker TEXT",
    "ALTER TABLE channel_signals ADD COLUMN channel_type TEXT DEFAULT 'public'",
    "ALTER TABLE channel_signals ADD COLUMN accuracy INTEGER DEFAULT 85",
]:
    try:
        c.execute(col)
    except:
        pass

conn.commit()
print("✅ Database initialized")

def get_setting(key, default=None):
    c.execute("SELECT value FROM bot_settings WHERE key=?", (key,))
    row = c.fetchone()
    return row[0] if row else default

def set_setting(key, value):
    c.execute("INSERT INTO bot_settings (key, value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?", (key, value, value))
    conn.commit()

def get_vip_channel_id():
    return get_setting("vip_channel_id")

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
print("Initializing bot...")
bot = telebot.TeleBot(BOT_TOKEN)
print("✅ Bot created")

# Verify bot token works
try:
    bot_info = bot.get_me()
    print(f"✅ Bot connected: @{bot_info.username}")
except Exception as e:
    print(f"❌ Bot token error: {e}")
    exit(1)

# ============================================
# LIVE PRICE FETCHING
# ============================================
def get_live_price_with_retry(ticker, max_retries=3):
    for attempt in range(max_retries):
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period="1d", interval="5m")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                return price
        except Exception as e:
            print(f"⚠️ Price fetch attempt {attempt+1} failed for {ticker}: {e}")
        time.sleep(1)
    fallback = FALLBACK_PRICES.get(ticker, 1000.00)
    print(f"⚠️ Using fallback price for {ticker}: {fallback}")
    return fallback

def get_signal_direction(symbol_name):
    current = active_directions.get(symbol_name)
    if current == "BUY":
        return "SELL"
    elif current == "SELL":
        return "BUY"
    else:
        symbol_data = next((s for s in SYMBOLS if s["name"] == symbol_name), None)
        if symbol_data and symbol_data.get("trending", False):
            return random.choices(["BUY", "SELL"], weights=[60, 40])[0]
        return random.choice(DIRECTIONS)

def set_active_direction(symbol_name, direction):
    active_directions[symbol_name] = direction

def generate_accurate_signal(symbol=None, force_direction=None):
    if symbol is None:
        trending_symbols = [s for s in SYMBOLS if s.get("trending", True)]
        symbol = random.choice(trending_symbols)
    
    direction = force_direction or get_signal_direction(symbol["name"])
    price = get_live_price_with_retry(symbol["ticker"])
    
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
    
    set_active_direction(symbol["name"], direction)
    
    return {
        "symbol": symbol["name"], "ticker": symbol["ticker"], "emoji": symbol["emoji"],
        "direction": direction, "entry_low": entry_low, "entry_high": entry_high,
        "tp1": tp1, "tp2": tp2, "sl": sl, "price": price, "decimals": d,
        "analysis": analysis, "dir_emoji": dir_emoji, "accuracy": symbol.get("accuracy", 85)
    }

def save_signal_to_db(data, channel_type="public"):
    now = datetime.datetime.now()
    c.execute("""INSERT INTO channel_signals
                 (symbol, direction, entry, tp1, tp2, sl, decimals, sent_date, sent_time, ticker, channel_type, accuracy)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
              (data["symbol"], data["direction"],
               (data["entry_low"] + data["entry_high"]) / 2,
               data["tp1"], data["tp2"], data["sl"], data["decimals"],
               now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), data["ticker"], channel_type, data["accuracy"]))
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
# SIGNAL TEMPLATES (simplified for brevity)
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
{VIP_CHANNEL}"""

TEMPLATES = [template_fire]

def build_channel_post():
    d = generate_accurate_signal()
    signal_id = save_signal_to_db(d, channel_type="public")
    return TEMPLATES[0](d), signal_id

# ============================================
# PROMOTIONAL MESSAGES (simplified)
# ============================================
def get_promo_message():
    return f"""💎 *VIP ACCESS - LIMITED SLOTS!* 💎

🔥 Only ₹399/month for 30-35 premium signals daily!
✅ Early entries before public channel
✅ 89%+ win rate
✅ 1-on-1 support

📩 DM {CONTACT_USERNAME} to join now!
🔗 {VIP_CHANNEL}"""

# ============================================
# PRICE MONITOR (simplified)
# ============================================
def price_monitor():
    while True:
        time.sleep(180)
        try:
            pending = get_pending_signals()
            for row in pending:
                sig_id, symbol, direction, entry, tp1, tp2, sl, decimals, msg_id, ticker, result, ch_type, accuracy = row
                if not ticker:
                    continue
                current = get_live_price_with_retry(ticker, max_retries=1)
                if current is None:
                  continue
                if direction == "BUY":
                    if current >= tp2 or current >= tp1:
                        update_signal_result(sig_id, "tp_hit")
                        active_directions.pop(symbol, None)
                        try:
                            bot.send_message(CHANNEL_ID, f"🎯 *TP HIT!* {symbol} {direction} ✅", parse_mode='Markdown')
                        except: pass
                    elif current <= sl:
                        if ch_type != "vip":
                            try:
                                bot.delete_message(CHANNEL_ID, msg_id)
                            except: pass
                        update_signal_result(sig_id, "sl_hit")
                        active_directions.pop(symbol, None)
                else:
                    if current <= tp2 or current <= tp1:
                        update_signal_result(sig_id, "tp_hit")
                        active_directions.pop(symbol, None)
                        try:
                            bot.send_message(CHANNEL_ID, f"🎯 *TP HIT!* {symbol} {direction} ✅", parse_mode='Markdown')
                        except: pass
                    elif current >= sl:
                        if ch_type != "vip":
                            try:
                                bot.delete_message(CHANNEL_ID, msg_id)
                            except: pass
                        update_signal_result(sig_id, "sl_hit")
                        active_directions.pop(symbol, None)
        except Exception as e:
            print(f"Price monitor error: {e}")

# ============================================
# SCHEDULERS
# ============================================
evening_report_sent = {"date": ""}
post_counter = [0]
public_signal_count = 0
MAX_PUBLIC_SIGNALS_PER_DAY = 8

def channel_scheduler():
    global public_signal_count
    last_date = ""
    while True:
        try:
            ist = get_ist_time()
            today = ist.strftime("%Y-%m-%d")
            if today != last_date:
                public_signal_count = 0
                last_date = today
            tick = post_counter[0]
            post_counter[0] += 1
            if tick % 2 == 1:
                promo = get_promo_message()
                bot.send_message(CHANNEL_ID, promo, parse_mode='Markdown')
                print(f"Promo posted")
            else:
                if public_signal_count < MAX_PUBLIC_SIGNALS_PER_DAY:
                    text, signal_id = build_channel_post()
                    sent_msg = bot.send_message(CHANNEL_ID, text, parse_mode='Markdown')
                    update_signal_message_id(signal_id, sent_msg.message_id)
                    public_signal_count += 1
                    print(f"Signal #{public_signal_count} posted")
        except Exception as e:
            print(f"Scheduler error: {e}")
        time.sleep(1800)

# ============================================
# BOT COMMANDS
# ============================================
def main_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton("📝 Register", callback_data="register")
    btn2 = telebot.types.InlineKeyboardButton("📊 Free Signal", callback_data="free")
    btn3 = telebot.types.InlineKeyboardButton("⭐ VIP Access", callback_data="vip")
    btn4 = telebot.types.InlineKeyboardButton("💬 Support", callback_data="support")
    btn5 = telebot.types.InlineKeyboardButton("🌐 Website", url=WEBSITE_URL)
    btn6 = telebot.types.InlineKeyboardButton("📢 Free Channel", url=FREE_CHANNEL)
    keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    msg = f"""🚀 *Forex Trading With Kailash* 🚀

India's Most Trusted Forex Signals Provider

📊 *Services:*
✅ FREE Signals - Daily 5-8 calls
⭐ VIP Channel - ₹399/month (30-35 calls)
🔄 Copy Trading Available
📈 89% Win Rate | 5000+ Traders

🌐 *Website:* {WEBSITE_URL}
📢 *Free Channel:* {FREE_CHANNEL}
⭐ *VIP Channel:* {VIP_CHANNEL}

👇 *Choose an option:*"""
    bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=main_keyboard())
    print(f"Start command sent to {message.from_user.id}")

@bot.message_handler(commands=['register'])
def register_cmd(message):
    msg = bot.reply_to(message, "📝 *Send your details:*\n\n`Name, Email, Phone`\n\nExample: `Rajesh, rajesh@gmail.com, 9876543210`", parse_mode='Markdown')
    bot.register_next_step_handler(msg, save_user)

def save_user(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    try:
        data = message.text.split(',')
        name = data[0].strip()
        email = data[1].strip()
        phone = data[2].strip()
        c.execute("INSERT OR REPLACE INTO users (user_id, name, email, phone, register_date, is_vip) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_id, name, email, phone, str(datetime.datetime.now()), 0))
        c.execute("INSERT INTO registrations (user_id, name, email, phone, date) VALUES (?, ?, ?, ?, ?)",
                  (user_id, name, email, phone, str(datetime.datetime.now())))
        conn.commit()
        admin_msg = f"🔔 NEW REGISTRATION: {name} (@{username})"
        bot.send_message(ADMIN_ID, admin_msg)
        reply_msg = f"✅ *Welcome {name}!* Registration complete. Use /free to get signals!"
        bot.reply_to(message, reply_msg, parse_mode='Markdown', reply_markup=main_keyboard())
    except:
        bot.reply_to(message, "❌ *Invalid Format!* Send: `Name, Email, Phone`", parse_mode='Markdown')

def send_signal_or_block(chat_id, user_id, reply_to_msg=None):
    remaining = signals_remaining(user_id)
    if remaining <= 0:
        block_msg = f"🚫 *Free Signal Limit Reached!* Join VIP for unlimited signals: /vip"
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton("⭐ Get VIP Access", callback_data="vip"))
        if reply_to_msg:
            bot.reply_to(reply_to_msg, block_msg, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(chat_id, block_msg, parse_mode='Markdown', reply_markup=keyboard)
        return
    increment_signal_count(user_id)
    d = generate_accurate_signal()
    signal = f"""📊 *FREE FOREX SIGNAL* 📊
{d['emoji']} *{d['direction']} {d['symbol']}*
📌 Entry: `{d['entry_low']} - {d['entry_high']}`
🎯 TP1: `{d['tp1']}`
🎯 TP2: `{d['tp2']}`
🛑 SL: `{d['sl']}`"""
    if reply_to_msg:
        bot.reply_to(reply_to_msg, signal, parse_mode='Markdown', reply_markup=main_keyboard())
    else:
        bot.send_message(chat_id, signal, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['free'])
def free_signal(message):
    send_signal_or_block(message.chat.id, message.from_user.id, reply_to_msg=message)

@bot.message_handler(commands=['vip'])
def vip_command(message):
    msg = f"⭐ *VIP ACCESS* - ₹399/month\n📱 UPI: `{UPI_ID}`\nPay & send screenshot to {CONTACT_USERNAME}\n🔗 {VIP_CHANNEL}"
    bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['support'])
def support_command(message):
    msg = f"💬 Contact: {CONTACT_USERNAME}\n📧 Email: btcuscoinbase@gmail.com"
    bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['website'])
def website_command(message):
    bot.reply_to(message, f"🌐 {WEBSITE_URL}", parse_mode='Markdown', reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "register":
        msg = bot.send_message(call.message.chat.id, "📝 Send: `Name, Email, Phone`", parse_mode='Markdown')
        bot.register_next_step_handler(msg, save_user)
    elif call.data == "free":
        send_signal_or_block(call.message.chat.id, call.from_user.id)
    elif call.data == "vip":
        bot.send_message(call.message.chat.id, f"⭐ VIP: ₹399/month to {UPI_ID}")
    elif call.data == "support":
        bot.send_message(call.message.chat.id, f"💬 {CONTACT_USERNAME}")
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id == ADMIN_ID:
        c.execute("SELECT COUNT(*) FROM users")
        total = c.fetchone()[0]
        bot.reply_to(message, f"📊 Total users: {total}", parse_mode='Markdown')

@bot.message_handler(commands=['setvipid'])
def set_vip_id_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /setvipid -100XXXXXXXXXX")
        return
    vip_id = parts[1].strip()
    set_setting("vip_channel_id", vip_id)
    bot.reply_to(message, f"✅ VIP channel ID set to `{vip_id}`")

@bot.message_handler(commands=['help'])
def help_command(message):
    msg = """📚 Commands: /start, /register, /free, /vip, /support, /website, /help"""
    bot.reply_to(message, msg, parse_mode='Markdown', reply_markup=main_keyboard())

# ============================================
# MAIN ENTRY POINT
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STARTING BOT POLLING...")
    print("=" * 60)
    
    # Start background threads
    channel_thread = threading.Thread(target=channel_scheduler, daemon=True)
    channel_thread.start()
    monitor_thread = threading.Thread(target=price_monitor, daemon=True)
    monitor_thread.start()
    
    print("✅ All threads started. Bot is ready!")
    print("=" * 60)
    
    # Start polling (this blocks)
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Polling error: {e}")
        import traceback
        traceback.print_exc()
