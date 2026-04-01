# signals.py
import random
from datetime import datetime
from market_data import MarketData

class SignalGenerator:
    def __init__(self):
        self.market = MarketData()
        self.last_signals = {}
    
    def analyze_pair(self, symbol, pair_name):
        """Analyze a trading pair and generate signal"""
        
        # Get live data
        live_price = self.market.get_live_price(symbol)
        if not live_price:
            return None
        
        historical = self.market.get_historical_data(symbol, period="1d", interval="5m")
        if historical is None or len(historical) < 50:
            return None
        
        close_prices = historical['Close']
        
        # Calculate indicators
        rsi = self.market.calculate_rsi(close_prices)
        macd, signal, hist = self.market.calculate_macd(close_prices)
        ma20 = self.market.calculate_ma(close_prices, 20)
        ma50 = self.market.calculate_ma(close_prices, 50)
        support, resistance = self.market.calculate_support_resistance(close_prices)
        
        # Decision logic
        action = None
        confidence = 0
        reasons = []
        
        # RSI based decision
        if rsi < 30:
            action = "BUY ✅"
            confidence += 35
            reasons.append(f"RSI oversold at {rsi:.1f} (below 30)")
        elif rsi > 70:
            action = "SELL 🔻"
            confidence += 35
            reasons.append(f"RSI overbought at {rsi:.1f} (above 70)")
        
        # MACD based decision
        if hist > 0 and macd > signal:
            if action == "BUY ✅":
                confidence += 30
                reasons.append("MACD bullish crossover")
            elif action is None:
                action = "BUY ✅"
                confidence += 30
                reasons.append("MACD bullish crossover")
        elif hist < 0 and macd < signal:
            if action == "SELL 🔻":
                confidence += 30
                reasons.append("MACD bearish crossover")
            elif action is None:
                action = "SELL 🔻"
                confidence += 30
                reasons.append("MACD bearish crossover")
        
        # Moving Average based decision
        if ma20 and ma50:
            if ma20 > ma50:
                if action == "BUY ✅":
                    confidence += 20
                    reasons.append("Golden cross (MA20 above MA50)")
            else:
                if action == "SELL 🔻":
                    confidence += 20
                    reasons.append("Death cross (MA20 below MA50)")
        
        # Price position
        if live_price and support and resistance:
            price_position = (live_price - support) / (resistance - support) * 100
            if price_position < 30 and action == "BUY ✅":
                confidence += 15
                reasons.append(f"Near support level at {support:.2f}")
            elif price_position > 70 and action == "SELL 🔻":
                confidence += 15
                reasons.append(f"Near resistance level at {resistance:.2f}")
        
        # If no clear signal, skip
        if action is None or confidence < 50:
            return None
        
        # Calculate entry, TP, SL
        spread = live_price * 0.001  # 0.1% spread
        
        if "BUY" in action:
            entry = live_price
            tp1 = entry + (entry * 0.005)  # 0.5% profit
            tp2 = entry + (entry * 0.01)   # 1% profit
            sl = entry - (entry * 0.003)   # 0.3% stop loss
        else:
            entry = live_price
            tp1 = entry - (entry * 0.005)
            tp2 = entry - (entry * 0.01)
            sl = entry + (entry * 0.003)
        
        # Calculate expected profit %
        profit_pct = abs((tp1 - entry) / entry * 100)
        
        # Confidence level text
        if confidence >= 80:
            conf_text = "🔥 HIGH 🔥"
            fomo_text = "🚨 92% of our VIP traders are taking this trade! Don't miss out! 🚨"
        elif confidence >= 65:
            conf_text = "📈 MEDIUM-HIGH 📈"
            fomo_text = "📊 78% of VIP traders are entering this position 📊"
        else:
            conf_text = "📊 MEDIUM 📊"
            fomo_text = "⚡ VIP members are watching this closely ⚡"
        
        return {
            'pair': pair_name,
            'symbol': symbol,
            'action': action,
            'entry': entry,
            'tp1': tp1,
            'tp2': tp2,
            'sl': sl,
            'profit_pct': profit_pct,
            'confidence': confidence,
            'conf_text': conf_text,
            'reasons': reasons,
            'fomo_text': fomo_text,
            'rsi': rsi,
            'time': datetime.now()
        }
    
    def get_best_signal(self):
        """Get the best signal from all pairs"""
        best_signal = None
        best_confidence = 0
        
        from config import TRADING_PAIRS, PAIR_NAMES
        
        for symbol in TRADING_PAIRS:
            pair_name = PAIR_NAMES.get(symbol, symbol)
            signal = self.analyze_pair(symbol, pair_name)
            
            if signal and signal['confidence'] > best_confidence:
                best_confidence = signal['confidence']
                best_signal = signal
        
        return best_signal
    
    def format_signal_message(self, signal, is_vip=False):
        """Format signal message for Telegram"""
        
        reasons_text = "\n".join([f"▫️ {r}" for r in signal['reasons'][:3]])
        
        if is_vip:
            prefix = "👑 *VIP EXCLUSIVE SIGNAL* 👑\n\n"
        else:
            prefix = "📊 *FREE SIGNAL* 📊\n\n"
        
        message = f"""
{prefix}🔥 *{signal['pair']}* 🔥

🎯 *Action:* {signal['action']}
💰 *Entry:* {signal['entry']:.4f}
✅ *TP1:* {signal['tp1']:.4f} (+{signal['profit_pct']:.1f}%)
✅ *TP2:* {signal['tp2']:.4f} (+{signal['profit_pct']*2:.1f}%)
❌ *SL:* {signal['sl']:.4f}

📊 *Confidence:* {signal['conf_text']} ({signal['confidence']}%)
💹 *Expected Profit:* +{signal['profit_pct']:.1f}% to +{signal['profit_pct']*2:.1f}%

🔍 *Technical Reasons:*
{reasons_text}

{signal['fomo_text']}

⏰ Time: {signal['time'].strftime('%H:%M:%S')} IST

*Risk: 2% per trade | RR: 1:2*
"""
        
        if not is_vip:
            message += f"""
---
🌟 *Want Early Access?*
Join VIP for signals BEFORE public:
👉 {VIP_LINK}

💰 *VIP Price:* {VIP_PRICE}
🎯 *25-30 Premium Signals/Day*
"""
        
        return message
