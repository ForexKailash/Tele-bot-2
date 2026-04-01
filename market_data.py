# market_data.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketData:
    def __init__(self):
        self.cache = {}
    
    def get_live_price(self, symbol):
        """Get current live price"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol, period="1d", interval="5m"):
        """Get historical data for analysis"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            return data
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None
    
    def calculate_rsi(self, data, period=14):
        """Calculate RSI indicator"""
        if data is None or len(data) < period:
            return 50
        
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def calculate_macd(self, data):
        """Calculate MACD"""
        if data is None or len(data) < 26:
            return 0, 0, 0
        
        exp1 = data.ewm(span=12, adjust=False).mean()
        exp2 = data.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return macd.iloc[-1], signal.iloc[-1], histogram.iloc[-1]
    
    def calculate_ma(self, data, period=20):
        """Calculate Moving Average"""
        if data is None or len(data) < period:
            return None
        return data.rolling(window=period).mean().iloc[-1]
    
    def calculate_support_resistance(self, data, window=20):
        """Calculate support and resistance levels"""
        if data is None or len(data) < window:
            return None, None
        
        recent_data = data.tail(window)
        support = recent_data.min()
        resistance = recent_data.max()
        
        return support, resistance
