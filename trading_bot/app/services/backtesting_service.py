import pandas as pd
from datetime import datetime, timedelta
from app.services.strategy_service import StrategyService
from app.services.risk_management_service import RiskManagementService
from domain.entities.trade import Trade
from domain.entities.order import Order

class BacktestingService:
    def __init__(self, config, exchange_adapter, persistence_adapter):
        self.config = config
        self.exchange_adapter = exchange_adapter
        self.persistence_adapter = persistence_adapter
        self.strategy_service = StrategyService(config)
        self.risk_management_service = RiskManagementService(config)
        self.open_positions = []  # Lista para mantener posiciones abiertas

    def run(self):
        data = self.exchange_adapter.fetch_klines(
            symbol=self.config['exchange']['default_symbol'],
            timeframe=self.config['exchange']['timeframe'],
            since=pd.to_datetime(self.config['backtest']['start_date'])
        )
        
        print(f"Loaded {len(data)} candles from {data.index[0]} to {data.index[-1]}")

        capital = self.config['backtest']['initial_capital']
        completed_trades = []

        for i in range(200, len(data)):  # Empezar desde 200 para tener suficientes datos para EMA 200
            current_row = data.iloc[i]
            df_until_now = data.iloc[:i+1]
            
            # Verificar primero si hay posiciones abiertas que deben cerrarse
            self._check_exit_conditions(current_row, completed_trades, capital)
            
            # Solo buscar nuevas entradas si es menor al numero permitido
            if len(self.open_positions) < self.config['backtest']['simultaniouseous_trades']:
                # Usar la nueva estrategia avanzada
                buy_signal, sell_signal, atr = self.strategy_service.advanced_ema_strategy(df_until_now)

                if buy_signal.iloc[-1]:
                    self._open_long_position(current_row, capital, atr.iloc[-1])
                elif sell_signal.iloc[-1]:
                    self._open_short_position(current_row, capital, atr.iloc[-1])

        # Cerrar cualquier posición que quede abierta al final del backtest
        self._close_remaining_positions(data.iloc[-1], completed_trades, capital)

        self.persistence_adapter.save_trades(completed_trades)
        self.calculate_metrics(completed_trades, capital)

    def _open_long_position(self, current_row, capital, atr_value=None):
        """Abre una posición larga con TP/SL dinámicos"""
        position_size = self.risk_management_service.calculate_position_size(capital)
        entry_price = current_row['close']
        take_profit = self.risk_management_service.get_take_profit(entry_price, atr_value)
        stop_loss = self.risk_management_service.get_stop_loss(entry_price, atr_value)
        
        position = {
            'id': len(self.open_positions) + 1,
            'type': 'long',
            'entry_timestamp': current_row.name,
            'entry_price': entry_price,
            'amount': position_size / entry_price,
            'position_size': position_size,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'symbol': self.config['exchange']['default_symbol'],
            'atr_value': atr_value
        }
        
        self.open_positions.append(position)
        tp_distance = ((take_profit - entry_price) / entry_price) * 100
        sl_distance = ((entry_price - stop_loss) / entry_price) * 100
        print(f"Opened LONG position at {entry_price:.2f}, TP: {take_profit:.2f} (+{tp_distance:.1f}%), SL: {stop_loss:.2f} (-{sl_distance:.1f}%), ATR: {atr_value:.2f}")

    def _open_short_position(self, current_row, capital, atr_value=None):
        """Abre una posición corta con TP/SL dinámicos"""
        position_size = self.risk_management_service.calculate_position_size(capital)
        entry_price = current_row['close']
        take_profit = self.risk_management_service.get_take_profit_short(entry_price, atr_value)
        stop_loss = self.risk_management_service.get_stop_loss_short(entry_price, atr_value)
        
        position = {
            'id': len(self.open_positions) + 1,
            'type': 'short',
            'entry_timestamp': current_row.name,
            'entry_price': entry_price,
            'amount': position_size / entry_price,
            'position_size': position_size,
            'take_profit': take_profit,
            'stop_loss': stop_loss,
            'symbol': self.config['exchange']['default_symbol'],
            'atr_value': atr_value
        }
        
        self.open_positions.append(position)
        tp_distance = ((entry_price - take_profit) / entry_price) * 100
        sl_distance = ((stop_loss - entry_price) / entry_price) * 100
        print(f"Opened SHORT position at {entry_price:.2f}, TP: {take_profit:.2f} (-{tp_distance:.1f}%), SL: {stop_loss:.2f} (+{sl_distance:.1f}%), ATR: {atr_value:.2f}")

    def _check_exit_conditions(self, current_row, completed_trades, capital):
        """Verifica si alguna posición abierta debe cerrarse"""
        positions_to_remove = []
        
        for position in self.open_positions:
            exit_reason = None
            exit_price = None
            
            if position['type'] == 'long':
                # Para posición larga: TP si precio >= take_profit, SL si precio <= stop_loss
                if current_row['high'] >= position['take_profit']:
                    exit_reason = 'take_profit'
                    exit_price = position['take_profit']
                elif current_row['low'] <= position['stop_loss']:
                    exit_reason = 'stop_loss'
                    exit_price = position['stop_loss']
                    
            elif position['type'] == 'short':
                # Para posición corta: TP si precio <= take_profit, SL si precio >= stop_loss
                if current_row['low'] <= position['take_profit']:
                    exit_reason = 'take_profit'
                    exit_price = position['take_profit']
                elif current_row['high'] >= position['stop_loss']:
                    exit_reason = 'stop_loss'
                    exit_price = position['stop_loss']
            
            if exit_reason:
                # Calcular PnL
                if position['type'] == 'long':
                    pnl = (exit_price - position['entry_price']) * position['amount']
                else:  # short
                    pnl = (position['entry_price'] - exit_price) * position['amount']
                
                # Crear el trade completado
                trade = {
                    'entry_timestamp': position['entry_timestamp'],
                    'exit_timestamp': current_row.name,
                    'symbol': position['symbol'],
                    'side': position['type'],
                    'amount': position['amount'],
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'exit_reason': exit_reason,
                    'pnl': pnl,
                    'pnl_percentage': (pnl / position['position_size']) * 100
                }
                
                completed_trades.append(trade)
                positions_to_remove.append(position)
                
                print(f"Closed {position['type'].upper()} position: "
                      f"Entry: {position['entry_price']:.4f}, "
                      f"Exit: {exit_price:.4f}, "
                      f"Reason: {exit_reason.upper()}, "
                      f"PnL: {pnl:.4f} ({trade['pnl_percentage']:.2f}%)")
        
        # Remover posiciones cerradas
        for position in positions_to_remove:
            self.open_positions.remove(position)

    def _close_remaining_positions(self, last_row, completed_trades, capital):
        """Cierra cualquier posición que quede abierta al final del backtest"""
        for position in self.open_positions:
            exit_price = last_row['close']
            
            if position['type'] == 'long':
                pnl = (exit_price - position['entry_price']) * position['amount']
            else:  # short
                pnl = (position['entry_price'] - exit_price) * position['amount']
            
            trade = {
                'entry_timestamp': position['entry_timestamp'],
                'exit_timestamp': last_row.name,
                'symbol': position['symbol'],
                'side': position['type'],
                'amount': position['amount'],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'exit_reason': 'end_of_backtest',
                'pnl': pnl,
                'pnl_percentage': (pnl / position['position_size']) * 100
            }
            
            completed_trades.append(trade)
            print(f"Closed {position['type'].upper()} position at end of backtest: "
                  f"PnL: {pnl:.4f} ({trade['pnl_percentage']:.2f}%)")
        
        self.open_positions.clear()

    def calculate_metrics(self, trades, final_capital):
        if not trades:
            print("No trades executed during backtest")
            return

        initial_capital = self.config['backtest']['initial_capital']
        df = pd.DataFrame(trades)

        # Métricas mejoradas
        total_pnl = df['pnl'].sum()
        final_capital_calculated = initial_capital + total_pnl
        roi = (final_capital_calculated - initial_capital) / initial_capital * 100
        
        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(df) * 100 if len(df) > 0 else 0
        
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else float('inf')

        # Calcular drawdown máximo
        capital_curve = [initial_capital]
        for pnl in df['pnl']:
            capital_curve.append(capital_curve[-1] + pnl)
        
        peak = capital_curve[0]
        max_drawdown = 0
        for capital in capital_curve:
            if capital > peak:
                peak = capital
            drawdown = (peak - capital) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Separar por tipo de cierre
        tp_trades = df[df['exit_reason'] == 'take_profit']
        sl_trades = df[df['exit_reason'] == 'stop_loss']
        
        metrics = {
            'initial_capital': initial_capital,
            'final_capital': final_capital_calculated,
            'total_pnl': total_pnl,
            'roi_percentage': roi,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate_percentage': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown_percentage': max_drawdown,
            'take_profit_hits': len(tp_trades),
            'stop_loss_hits': len(sl_trades),
            'tp_hit_rate': len(tp_trades) / len(df) * 100 if len(df) > 0 else 0,
            'sl_hit_rate': len(sl_trades) / len(df) * 100 if len(df) > 0 else 0
        }

        # Imprimir resumen
        print("\n=== BACKTEST RESULTS ===")
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate_percentage']:.2f}%")
        print(f"Take Profit Hits: {metrics['take_profit_hits']} ({metrics['tp_hit_rate']:.2f}%)")
        print(f"Stop Loss Hits: {metrics['stop_loss_hits']} ({metrics['sl_hit_rate']:.2f}%)")
        print(f"Total PnL: {metrics['total_pnl']:.4f}")
        print(f"ROI: {metrics['roi_percentage']:.2f}%")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"Max Drawdown: {metrics['max_drawdown_percentage']:.2f}%")

        self.persistence_adapter.save_metrics(metrics)
