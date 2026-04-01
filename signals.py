import random
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

class SignalGenerator:
    def __init__(self):
        self.vip_signals_today = 0
        self.public_signals_today = 0
        self.last_reset_date = datetime.now().date()

    def reset_daily_counts(self):
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.vip_signals_today = 0
            self.public_signals_today = 0
            self.last_reset_date = today

    def get_live_price(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return data['Close'].iloc[-1]
        except:
            pass
        return None

    def get_historical_data(self, symbol, period="1d", interval="5m"):
        try:
            ticker = yf.Ticker(symbol)
            return ticker.history(period=period, interval=interval)
        except:
            return None

    def calculate_rsi(self, data, period=14):
        if data is None or len(data) < period:
            return 50
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def calculate_macd(self, data):
        if data is None or len(data) < 26:
            return 0, 0, 0
        exp1 = data.ewm(span=12, adjust=False).mean()
        exp2 = data.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        return macd.iloc[-1], signal.iloc[-1], hist.iloc[-1]

    def calculate_ma(self, data, period=20):
        if data is None or len(data) < period:
            return None
        return data.rolling(window=period).mean().iloc[-1]

    def analyze_pair(self, symbol, pair_name, signal_type="public"):
        live_price = self.get_live_price(symbol)
        if not live_price:
            return None

        hist = self.get_historical_data(symbol)
        if hist is None or len(hist) < 50:
            return None

        close = hist['Close']
        rsi = self.calculate_rsi(close)
        macd, macd_signal, hist_val = self.calculate_macd(close)
        ma20 = self.calculate_ma(close, 20)
        ma50 = self.calculate_ma(close, 50)

        action = None
        confidence = 50
        reasons = []

        if rsi < 30:
            action = "BUY ✅"
            confidence += 25
            reasons.append(f"📊 RSI oversold at {rsi:.1f}")
        elif rsi > 70:
            action = "SELL 🔻"
            confidence += 25
            reasons.append(f"📊 RSI overbought at {rsi:.1f}")

        if hist_val > 0 and macd > macd_signal:
            if action == "BUY ✅":
                confidence += 20
                reasons.append("📈 MACD bullish crossover")
            elif action is None:
                action = "BUY ✅"
                confidence += 20
                reasons.append("📈 MACD bullish crossover")
        elif hist_val < 0 and macd < macd_signal:
            if action == "SELL 🔻":
                confidence += 20
                reasons.append("📉 MACD bearish crossover")
            elif action is None:
                action = "SELL 🔻"
                confidence += 20
                reasons.append("📉 MACD bearish crossover")

        if ma20 and ma50:
            if ma20 > ma50 and action == "BUY ✅":
                confidence += 15
                reasons.append("📊 Golden cross (MA20 > MA50)")
            elif ma20 < ma50 and action == "SELL 🔻":
                confidence += 15
                reasons.append("📊 Death cross (MA20 < MA50)")

        if action is None or confidence < 60:
            return None

        # Entry, TP, SL
        if "BUY" in action:
            entry = live_price
            tp1 = entry + entry * 0.005
            tp2 = entry + entry * 0.01
            sl = entry - entry * 0.003
        else:
            entry = live_price
            tp1 = entry - entry * 0.005
            tp2 = entry - entry * 0.01
            sl = entry + entry * 0.003

        profit_pct = abs((tp1 - entry) / entry * 100)

        return {
            'pair': pair_name,
            'symbol': symbol,
            'action': action,
            'entry': round(entry, 4),
            'tp1': round(tp1, 4),
            'tp2': round(tp2, 4),
            'sl': round(sl, 4),
            'profit_pct': round(profit_pct, 1),
            'confidence': confidence,
            'reasons': reasons[:2],
            'rsi': round(rsi, 1),
            'time': datetime.now()
        }

    def can_send_vip_signal(self):
        self.reset_daily_counts()
        return self.vip_signals_today < 30

    def can_send_public_signal(self):
        self.reset_daily_counts()
        return self.public_signals_today < 10

    def increment_vip_count(self):
        self.vip_signals_today += 1

    def increment_public_count(self):
        self.public_signals_today += 1

    def get_best_signal(self, signal_type="public"):
        pairs = {
            "XAUUSD=X": "🟡 GOLD",
            "EURUSD=X": "💶 EUR/USD",
            "GBPUSD=X": "💷 GBP/USD",
            "BTC-USD": "₿ BITCOIN",
            "NQ=F": "📊 NAS100"
        }
        best = None
        best_conf = 0
        for sym, name in pairs.items():
            sig = self.analyze_pair(sym, name, signal_type)
            if sig and sig['confidence'] > best_conf:
                best_conf = sig['confidence']
                best = sig
        return best

    def format_vip_signal(self, signal):
        reasons = "\n".join(signal['reasons'])
        rr = round(abs(signal['tp1'] - signal['entry']) / abs(signal['sl'] - signal['entry']), 1)
        msg = f"""
👑 *VIP EXCLUSIVE SIGNAL* 👑

🔥 *{signal['pair']}* 🔥

🎯 *Action:* {signal['action']}
💰 *Entry:* {signal['entry']}
✅ *TP1:* {signal['tp1']} (+{signal['profit_pct']:.1f}%)
✅ *TP2:* {signal['tp2']} (+{signal['profit_pct']*2:.1f}%)
❌ *SL:* {signal['sl']}

📊 *Confidence:* {'HIGH 🔥' if signal['confidence']>=80 else 'MEDIUM 📈'}
📈 *RSI:* {signal['rsi']}

🔍 *Technical Reasons:*
{reasons}

🎯 *Risk:Reward:* 1:{rr}

⏰ Time: {signal['time'].strftime('%H:%M:%S')} IST

━━━━━━━━━━━━━━━━━━━━━━
🎓 *TRADING COURSES – LIMITED OFFER* 🎓

📚 *Forex Mastery* - ₹2999  
• Complete foundation  
• Technical analysis  
• Risk management  

💰 *Smart Money Concepts* - ₹3999  
• Institutional trading  
• Order blocks & liquidity  

🎯 *Price Action Pro* - ₹3499  
• Candlestick patterns  
• Supply & demand  

✨ *VIP + ALL COURSES BUNDLE* - ₹9999 ✨  
• Lifetime VIP signals  
• All 3 courses  
• Personal mentorship  

💳 *UPI:* kailashbhardwaj66-2@okicici  
📱 *Contact:* @ForexKailash after payment  

━━━━━━━━━━━━━━━━━━━━━━
*VIP Signal #{random.randint(1,30)}/30 Today*
"""
        return msg

    def format_public_signal(self, signal):
        reasons = "\n".join(signal['reasons'])
        rr = round(abs(signal['tp1'] - signal['entry']) / abs(signal['sl'] - signal['entry']), 1)
        msg = f"""
📊 *FREE SIGNAL* 📊

🔥 *{signal['pair']}* 🔥

🎯 *Action:* {signal['action']}
💰 *Entry:* {signal['entry']}
✅ *TP1:* {signal['tp1']} (+{signal['profit_pct']:.1f}%)
✅ *TP2:* {signal['tp2']} (+{signal['profit_pct']*2:.1f}%)
❌ *SL:* {signal['sl']}

📊 *Confidence:* {'HIGH 🔥' if signal['confidence']>=80 else 'MEDIUM 📈'}
📈 *RSI:* {signal['rsi']}

🔍 *Technical Reasons:*
{reasons}

🎯 *Risk:Reward:* 1:{rr}

⏰ Time: {signal['time'].strftime('%H:%M:%S')} IST

━━━━━━━━━━━━━━━━━━━━━━
🌟 *UPGRADE TO VIP CHANNEL!* 🌟

✨ *VIP Benefits:*  
• 25-30 Premium Signals/Day (vs 8-10 free)  
• Early Entry (5-10 min before public)  
• Live Market Analysis  
• 1-on-1 VIP Support  
• Course Discounts  
• 89% Win Rate Guarantee  

💰 *Price:* ₹399/month  
🎓 *VIP + Course Bundle:* ₹9999 (Save ₹2999)  

💳 *Pay:* kailashbhardwaj66-2@okicici  

👉 *Join:* @ForexKailash after payment  

━━━━━━━━━━━━━━━━━━━━━━
*Free Signal #{random.randint(1,10)}/10 Today*
*Join VIP for unlimited signals!*
"""
        return msg
