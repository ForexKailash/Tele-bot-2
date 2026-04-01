import yfinance as yf

class MarketData:
    @staticmethod
    def get_live_price(symbol):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return data['Close'].iloc[-1]
        except:
            pass
        return None

    @staticmethod
    def get_historical_data(symbol, period="1d", interval="5m"):
        try:
            ticker = yf.Ticker(symbol)
            return ticker.history(period=period, interval=interval)
        except:
            return None
