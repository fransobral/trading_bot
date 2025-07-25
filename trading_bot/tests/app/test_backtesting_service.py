import unittest
import pandas as pd
import yaml
from unittest.mock import MagicMock

from trading_bot.app.services.backtesting_service import BacktestingService

class TestBacktestingService(unittest.TestCase):
    def setUp(self):
        with open('trading_bot/config.yml', 'r') as f:
            self.config = yaml.safe_load(f)

        self.exchange_adapter = MagicMock()
        self.persistence_adapter = MagicMock()

        self.backtesting_service = BacktestingService(
            self.config, self.exchange_adapter, self.persistence_adapter
        )

        self.data = pd.DataFrame({
            'open': [100, 102, 101, 103, 105],
            'high': [103, 104, 102, 105, 106],
            'low': [99, 101, 100, 102, 104],
            'close': [102, 103, 101, 104, 105],
            'volume': [1000, 1200, 1100, 1300, 1400]
        }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']))

    def test_run(self):
        self.exchange_adapter.fetch_klines.return_value = self.data
        self.backtesting_service.run()

        self.exchange_adapter.fetch_klines.assert_called_once()
        self.persistence_adapter.save_trades.assert_called_once()
        self.persistence_adapter.save_metrics.assert_called_once()

if __name__ == '__main__':
    unittest.main()
