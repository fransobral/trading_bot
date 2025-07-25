import ccxt
import pandas as pd
from datetime import datetime

class ExchangeAdapter:
    def __init__(self, config):
        self.config = config
        self.exchange = getattr(ccxt, config['exchange']['name'])({
            'apiKey': config['exchange']['api_key'],
            'secret': config['exchange']['api_secret'],
        })

    def fetch_klines(self, symbol, timeframe, since):
        since_timestamp = int(since.timestamp() * 1000)
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since_timestamp)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df

    def create_order(self, symbol, order_type, side, amount, price=None):
        return self.exchange.create_order(symbol, order_type, side, amount, price)
