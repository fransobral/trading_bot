import unittest
import pandas as pd
import yaml

from trading_bot.app.services.strategy_service import StrategyService

class TestStrategyService(unittest.TestCase):
    def setUp(self):
        with open('trading_bot/config.yml', 'r') as f:
            self.config = yaml.safe_load(f)
        self.strategy_service = StrategyService(self.config)
        self.data = pd.DataFrame({
            'open': [100, 102, 101, 103, 105],
            'high': [103, 104, 102, 105, 106],
            'low': [99, 101, 100, 102, 104],
            'close': [102, 103, 101, 104, 105],
            'volume': [1000, 1200, 1100, 1300, 1400]
        })

    def test_ema_cross_rsi_macd(self):
        buy_signal, sell_signal = self.strategy_service.ema_cross_rsi_macd(self.data)
        self.assertIsInstance(buy_signal, pd.Series)
        self.assertIsInstance(sell_signal, pd.Series)

if __name__ == '__main__':
    unittest.main()
