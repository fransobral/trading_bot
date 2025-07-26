import pandas as pd
import ta
import pandas_ta as pta

class StrategyService:
    def __init__(self, config):
        self.config = config

    def ema_cross(self, data: pd.DataFrame):
        """
        Estrategia simple de cruce de EMA 20 y 50
        - Señal de compra: EMA 20 cruza por encima de EMA 50
        - Señal de venta: EMA 20 cruza por debajo de EMA 50
        """
        ema_short = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_cross']['ema_short'])
        ema_long = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_cross']['ema_long'])

        # Señal de compra: EMA corta cruza por encima de EMA larga
        buy_signal = (ema_short > ema_long) & (ema_short.shift(1) <= ema_long.shift(1))

        # Señal de venta: EMA corta cruza por debajo de EMA larga
        sell_signal = (ema_short < ema_long) & (ema_short.shift(1) >= ema_long.shift(1))

        return buy_signal, sell_signal

    def ema_cross_rsi_macd(self, data: pd.DataFrame):
        """Estrategia original (ahora desactivada)"""
        # EMA Cross
        ema_short = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_cross_rsi_macd']['ema_short'])
        ema_long = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_cross_rsi_macd']['ema_long'])

        # RSI
        rsi = ta.momentum.rsi(data['close'], window=self.config['strategies']['ema_cross_rsi_macd']['rsi_period'])

        # MACD usando ta
        macd_line = ta.trend.macd(data['close'], 
                                 window_fast=self.config['strategies']['ema_cross_rsi_macd']['macd_fast'],
                                 window_slow=self.config['strategies']['ema_cross_rsi_macd']['macd_slow'])
        macd_signal = ta.trend.macd_signal(data['close'], 
                                          window_fast=self.config['strategies']['ema_cross_rsi_macd']['macd_fast'],
                                          window_slow=self.config['strategies']['ema_cross_rsi_macd']['macd_slow'],
                                          window_sign=self.config['strategies']['ema_cross_rsi_macd']['macd_signal'])

        # Buy signal
        buy_signal = ((ema_short > ema_long) & (ema_short.shift(1) <= ema_long.shift(1)) &
                      (rsi < self.config['strategies']['ema_cross_rsi_macd']['rsi_overbought'] - self.config['strategies']['ema_cross_rsi_macd']['rsi_sensitivity']) &
                      (macd_line > macd_signal))

        # Sell signal
        sell_signal = ((ema_short < ema_long) & (ema_short.shift(1) >= ema_long.shift(1)) &
                       (rsi > self.config['strategies']['ema_cross_rsi_macd']['rsi_oversold'] + self.config['strategies']['ema_cross_rsi_macd']['rsi_sensitivity']) &
                       (macd_line < macd_signal))

        return buy_signal, sell_signal

    def ema_rebound(self, data: pd.DataFrame):
        """Estrategia de rebote en EMA (desactivada)"""
        ema = ta.trend.ema_indicator(data['close'], window=self.config['strategies']['ema_rebound']['ema_period'])

        # Buy signal
        buy_signal = (data['low'] <= ema) & (data['close'] > ema)

        # Sell signal
        sell_signal = (data['high'] >= ema) & (data['close'] < ema)

        return buy_signal, sell_signal

    def bollinger_bands_breakout(self, data: pd.DataFrame):
        """Estrategia de ruptura de Bandas de Bollinger (desactivada)"""
        # Bollinger Bands usando ta
        bollinger = ta.volatility.BollingerBands(data['close'], window=20, window_dev=2)
        upper = bollinger.bollinger_hband()
        middle = bollinger.bollinger_mavg()
        lower = bollinger.bollinger_lband()

        # Buy signal
        buy_signal = (data['close'] > upper) & (data['volume'] > data['volume'].shift(1))

        # Sell signal
        sell_signal = (data['close'] < lower) & (data['volume'] > data['volume'].shift(1))

        return buy_signal, sell_signal
