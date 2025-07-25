import pandas as pd
from trading_bot.app.services.strategy_service import StrategyService
from trading_bot.app.services.risk_management_service import RiskManagementService

class BacktestingService:
    def __init__(self, config, exchange_adapter, persistence_adapter):
        self.config = config
        self.exchange_adapter = exchange_adapter
        self.persistence_adapter = persistence_adapter
        self.strategy_service = StrategyService(config)
        self.risk_management_service = RiskManagementService(config)

    def run(self):
        data = self.exchange_adapter.fetch_klines(
            symbol=self.config['exchange']['default_symbol'],
            timeframe=self.config['exchange']['timeframe'],
            since=pd.to_datetime(self.config['backtest']['start_date'])
        )

        capital = self.config['backtest']['initial_capital']
        trades = []

        for i in range(1, len(data)):
            df = data.iloc[:i]
            buy_signal, sell_signal = self.strategy_service.ema_cross_rsi_macd(df)

            if buy_signal.iloc[-1]:
                position_size = self.risk_management_service.calculate_position_size(capital)
                entry_price = df['close'].iloc[-1]
                take_profit = self.risk_management_service.get_take_profit(entry_price)
                stop_loss = self.risk_management_service.get_stop_loss(entry_price)

                # Simulate trade
                capital -= position_size
                trades.append({
                    'timestamp': df.index[-1],
                    'symbol': self.config['exchange']['default_symbol'],
                    'side': 'buy',
                    'amount': position_size / entry_price,
                    'price': entry_price,
                    'pnl': 0
                })

            elif sell_signal.iloc[-1]:
                # In a real scenario, you would sell an existing position.
                # For simplicity, we'll just log the sell signal.
                pass

        self.persistence_adapter.save_trades(trades)
        self.calculate_metrics(trades, capital)

    def calculate_metrics(self, trades, final_capital):
        if not trades:
            return

        initial_capital = self.config['backtest']['initial_capital']
        df = pd.DataFrame(trades)

        roi = (final_capital - initial_capital) / initial_capital
        win_rate = len(df[df['pnl'] > 0]) / len(df) if len(df) > 0 else 0

        # Simplified drawdown calculation
        capital_over_time = [initial_capital] + list(initial_capital + df['pnl'].cumsum())
        peak = max(capital_over_time)
        drawdown = max([(peak - val) / peak for val in capital_over_time])

        metrics = {
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'roi': roi,
            'win_rate': win_rate,
            'drawdown': drawdown,
            'total_trades': len(trades)
        }

        self.persistence_adapter.save_metrics(metrics)
