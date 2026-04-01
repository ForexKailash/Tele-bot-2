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

# Constants
BOT_TOKEN = 'YOUR_BOT_TOKEN'
ADMIN_ID = 'YOUR_ADMIN_ID'
CHANNEL_ID = 'YOUR_CHANNEL_ID'
SYMBOLS = {
    'XAU/USD': {'ticker': 'GC=F', 'emoji': '🥇'},
    'BTC/USD': {'ticker': 'TickerBTC-USD', 'emoji': '₿'},
    'EUR/USD': {'ticker': 'EURUSD=X', 'emoji': '💶'},
    'USOIL': {'ticker': 'CL=F', 'emoji': '🛢️'},
    'GBP/USD': {'ticker': 'GBPUSD=X', 'emoji': '💷'},
    'USD/JPY': {'ticker': 'JPY=X', 'emoji': '🇯🇵'},
    'ETH/USD': {'ticker': 'ETH-USD', 'emoji': '💎'},
    'NAS100': {'ticker': 'NQ=F', 'emoji': '📈'},
    'SILVER': {'ticker': 'SI=F', 'emoji': '🥈'},
    'AUD/USD': {'ticker': 'AUDUSD=X', 'emoji': '🦘'},
    'GBP/JPY': {'ticker': 'GBPJPY=X', 'emoji': '⚡'},
    'US30': {'ticker': 'YM=F', 'emoji': '🏛️'},
    'USD/CAD': {'ticker': 'USDCAD=X', 'emoji': '🍁'},
    'SOL/USD': {'ticker': 'SOL-USD', 'emoji': '☀️'}
}  

# Decimals
TP1_pct = 0.1  # Example value
TP2_pct = 0.2  # Example value
SL_pct = 0.05  # Example value
spread_pct = 0.01  # Example value
accuracy = 0.8  # Example value
trending = True  # Example boolean value
analysis_buy = True  # Example boolean value
analysis_sell = False  # Example boolean value

# Directions
DIRECTIONS = {'BUY': 1, 'SELL': -1}
FALLBACK_PRICES = {
    'XAU/USD': 1800,
    'BTC/USD': 60000,
    'EUR/USD': 1.2,
    'USOIL': 70,
    'GBP/USD': 1.35,
    'USD/JPY': 110,
    'ETH/USD': 2000,
    'NAS100': 14000,
    'SILVER': 25,
    'AUD/USD': 0.75,
    'GBP/JPY': 150,
    'US30': 32000,
    'USD/CAD': 1.25,
    'SOL/USD': 500
}

# Database setup
connection = sqlite3.connect('signals.db')
cursor = connection.cursor()

# Create tables for users, registrations, signal usage, channel signals, bot settings
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    user_name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS signal_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    signal_id INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS channel_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id INTEGER,
    message_id INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS bot_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_name TEXT,
    setting_value TEXT
)
''')

connection.commit()

# Functions
def get_signal_count():
    cursor.execute('SELECT COUNT(*) FROM signals')
    return cursor.fetchone()[0]

def increment_signal_count(signal_id):
    cursor.execute('UPDATE signals SET count = count + 1 WHERE id = ?', (signal_id,))
    connection.commit()

def signals_remaining(user_id):
    # Logic to calculate remaining signals
    return 5  # Example value

# Bot initialization
bot = telebot.TeleBot(BOT_TOKEN)

def get_live_price_with_retry(symbol, retries=3):
    while retries > 0:
        try:
            price = get_live_price(symbol)
            return price
        except Exception as e:
            retries -= 1
            time.sleep(1)
    return None  # Return None if all retries fail


def get_signal_direction(entry_price, tp1, tp2, sl):
    if entry_price < tp1:
        return 'BUY'
    elif entry_price > tp2:
        return 'SELL'
    return 'HOLD'


def generate_accurate_signal(cursor):
    # Buy/Sell entry calculations
    entry_price = 0 # Your logic here
    TP1 = entry_price * (1 + TP1_pct)
    TP2 = entry_price * (1 + TP2_pct)
    SL = entry_price * (1 - SL_pct)
    spread = entry_price * spread_pct
    accuracy_value = accuracy 
    return entry_price, TP1, TP2, SL, spread, accuracy_value


def save_signal_to_db(signal_data):
    cursor.execute('INSERT INTO signals (data) VALUES (?)', (signal_data,))
    connection.commit()


def update_signal_message_id(signal_id, message_id):
    cursor.execute('UPDATE signals SET message_id = ? WHERE id = ?', (message_id, signal_id))
    connection.commit()


def update_signal_result(signal_id, result):
    cursor.execute('UPDATE signals SET result = ? WHERE id = ?', (result, signal_id))
    connection.commit()


def get_pending_signals():
    cursor.execute('SELECT * FROM signals WHERE status = "pending"')
    return cursor.fetchall()

# Time-related functions
IST_OFFSET = 5.5  # IST is UTC+5:30

def get_ist_time():
    utc_time = datetime.datetime.utcnow()
    ist_time = utc_time + datetime.timedelta(hours=IST_OFFSET)
    return ist_time


# Signal templates
template_fire = "🔥 New Market Signal!"
template_premium = "💎 Premium Signal!"
template_urgent = "⚠️ Urgent Signal!"
template_analysis = "📊 Analysis Signal!"
template_clean = "✅ Clean Signal!"
template_winner = "🏆 Winning Signal!"


def build_channel_post(signal):
    # Logic to build the channel post
    return "Post content here"


TP_HIT_MESSAGES = [
    "🎉 TP HIT!",
    "💰 Take Profit Achieved!"
]

VIP_CELEBRATION = [
    "🥳 VIP Members Celebration!"
]

VIP_SL_WARNING_MESSAGES = [
    "⚠️ Attention: Stop Loss Warning!"
]


def calculate_profit_str(entry_price, exit_price):
    profit = (exit_price - entry_price) / entry_price * 100
    return f'Profit: {profit:.2f}%'


def get_live_price(symbol):
    # Logic to fetch live price from an API
    return 0  # Example value


# Price Monitor
def price_monitor():
    while True:
        pending_signals = get_pending_signals()
        for signal in pending_signals:
            current_price = get_live_price(signal['symbol'])
            if current_price >= signal['TP1']:
                update_signal_result(signal['id'], 'TP1 HIT')
            elif current_price <= signal['SL']:
                update_signal_result(signal['id'], 'SL HIT')
        time.sleep(10)  # Check every 10 seconds

# Start the price monitor in a new thread
monitor_thread = threading.Thread(target=price_monitor)
monitor_thread.start()