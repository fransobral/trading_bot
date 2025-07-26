import pandas as pd
import ta
import pandas_ta as pta
from datetime import datetime

class StrategyService:
    def __init__(self, config):
        self.config = config

    def advanced_ema_strategy(self, data: pd.DataFrame):
        """
        Estrategia avanzada con EMA 50/200, RSI, MACD y filtros de volumen/horario (optimizada)
        """
        # === INDICADORES ===
        ema_fast = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['advanced_ema_strategy']['ema_fast'])
        ema_slow = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['advanced_ema_strategy']['ema_slow'])
        
        rsi = ta.momentum.rsi(data['close'], window=self.config['strategies']['advanced_ema_strategy']['rsi_period'])
        
        macd_line = ta.trend.macd(data['close'], 
                                  window_fast=self.config['strategies']['advanced_ema_strategy']['macd_fast'],
                                  window_slow=self.config['strategies']['advanced_ema_strategy']['macd_slow'])
        macd_signal = ta.trend.macd_signal(data['close'], 
                                           window_fast=self.config['strategies']['advanced_ema_strategy']['macd_fast'],
                                           window_slow=self.config['strategies']['advanced_ema_strategy']['macd_slow'],
                                           window_sign=self.config['strategies']['advanced_ema_strategy']['macd_signal'])

        atr = ta.volatility.average_true_range(data['high'], data['low'], data['close'], 
                                               window=self.config['strategies']['advanced_ema_strategy']['atr_period'])

        # === FILTROS ===
        volume_ma = data['volume'].rolling(window=self.config['strategies']['advanced_ema_strategy']['volume_lookback']).mean()
        volume_threshold = self.config['strategies']['advanced_ema_strategy']['volume_threshold']
        high_volume = data['volume'] > (volume_ma * volume_threshold)

        trading_allowed = self._is_trading_time_allowed(data.index)

        # === VENTANAS FLEXIBLES ===
        recent_window = 3
        rsi_oversold_exit = (rsi > self.config['strategies']['advanced_ema_strategy']['rsi_oversold']).rolling(recent_window).max() == 1
        rsi_overbought_exit = (rsi < self.config['strategies']['advanced_ema_strategy']['rsi_overbought']).rolling(recent_window).max() == 1

        macd_bullish = (macd_line > macd_signal).rolling(recent_window).max() == 1
        macd_bearish = (macd_line < macd_signal).rolling(recent_window).max() == 1

        # === CONDICIONES LONG ===
        ema_bullish_trend = ema_fast > ema_slow
        buy_signal = ema_bullish_trend & rsi_oversold_exit & macd_bullish & high_volume & trading_allowed

        # === CONDICIONES SHORT ===
        ema_bearish_trend = ema_fast < ema_slow
        sell_signal = ema_bearish_trend & rsi_overbought_exit & macd_bearish & high_volume & trading_allowed

        return buy_signal, sell_signal, atr

    def _is_trading_time_allowed(self, timestamps):
        """
        Devuelve serie booleana para horarios válidos según configuración.
        """
        config = self.config['strategies']['advanced_ema_strategy']
        if config.get('avoid_weekends', False):
            return pd.Series(timestamps).map(lambda ts: ts.weekday() < 5).values
        return pd.Series([True] * len(timestamps)).values

    def ema_cross(self, data: pd.DataFrame):
        ema_short = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_cross']['ema_short'])
        ema_long = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_cross']['ema_long'])

        buy_signal = (ema_short > ema_long) & (ema_short.shift(1) <= ema_long.shift(1))
        sell_signal = (ema_short < ema_long) & (ema_short.shift(1) >= ema_long.shift(1))

        return buy_signal, sell_signal

    def ema_cross_rsi_macd(self, data: pd.DataFrame):
        ema_short = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_cross_rsi_macd']['ema_short'])
        ema_long = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_cross_rsi_macd']['ema_long'])
        rsi = ta.momentum.rsi(data['close'], window=self.config['strategies']['ema_cross_rsi_macd']['rsi_period'])

        macd_line = ta.trend.macd(data['close'], 
                                  window_fast=self.config['strategies']['ema_cross_rsi_macd']['macd_fast'],
                                  window_slow=self.config['strategies']['ema_cross_rsi_macd']['macd_slow'])
        macd_signal = ta.trend.macd_signal(data['close'], 
                                           window_fast=self.config['strategies']['ema_cross_rsi_macd']['macd_fast'],
                                           window_slow=self.config['strategies']['ema_cross_rsi_macd']['macd_slow'],
                                           window_sign=self.config['strategies']['ema_cross_rsi_macd']['macd_signal'])

        buy_signal = ((ema_short > ema_long) & (ema_short.shift(1) <= ema_long.shift(1)) &
                      (rsi < self.config['strategies']['ema_cross_rsi_macd']['rsi_overbought'] - self.config['strategies']['ema_cross_rsi_macd']['rsi_sensitivity']) &
                      (macd_line > macd_signal))

        sell_signal = ((ema_short < ema_long) & (ema_short.shift(1) >= ema_long.shift(1)) &
                       (rsi > self.config['strategies']['ema_cross_rsi_macd']['rsi_oversold'] + self.config['strategies']['ema_cross_rsi_macd']['rsi_sensitivity']) &
                       (macd_line < macd_signal))

        return buy_signal, sell_signal

    def ema_rebound(self, data: pd.DataFrame):
        ema = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_rebound']['ema_period'])

        buy_signal = (data['low'] <= ema) & (data['close'] > ema)
        sell_signal = (data['high'] >= ema) & (data['close'] < ema)

        return buy_signal, sell_signal

    def bollinger_bands_breakout(self, data: pd.DataFrame):
        bollinger = ta.volatility.BollingerBands(data['close'], window=20, window_dev=2)
        upper = bollinger.bollinger_hband()
        lower = bollinger.bollinger_lband()

        buy_signal = (data['close'] > upper) & (data['volume'] > data['volume'].shift(1))
        sell_signal = (data['close'] < lower) & (data['volume'] > data['volume'].shift(1))

        return buy_signal, sell_signal
