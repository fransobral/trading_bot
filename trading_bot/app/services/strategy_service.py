import pandas as pd
import talib

class StrategyService:
    def __init__(self, config):
        self.config = config

    def ema_cross_rsi_macd(self, data: pd.DataFrame):
        # EMA Cross
        ema_short = talib.EMA(data['close'], timeperiod=self.config['strategies']['ema_cross_rsi_macd']['ema_short'])
        ema_long = talib.EMA(data['close'], timeperiod=self.config['strategies']['ema_cross_rsi_macd']['ema_long'])

        # RSI
        rsi = talib.RSI(data['close'], timeperiod=self.config['strategies']['ema_cross_rsi_macd']['rsi_period'])

        # MACD
        macd, macdsignal, _ = talib.MACD(data['close'],
                                         fastperiod=self.config['strategies']['ema_cross_rsi_macd']['macd_fast'],
                                         slowperiod=self.config['strategies']['ema_cross_rsi_macd']['macd_slow'],
                                         signalperiod=self.config['strategies']['ema_cross_rsi_macd']['macd_signal'])

        # Buy signal
        buy_signal = ((ema_short > ema_long) & (ema_short.shift(1) <= ema_long.shift(1)) &
                      (rsi < self.config['strategies']['ema_cross_rsi_macd']['rsi_overbought'] - self.config['strategies']['ema_cross_rsi_macd']['rsi_sensitivity']) &
                      (macd > macdsignal))

        # Sell signal
        sell_signal = ((ema_short < ema_long) & (ema_short.shift(1) >= ema_long.shift(1)) &
                       (rsi > self.config['strategies']['ema_cross_rsi_macd']['rsi_oversold'] + self.config['strategies']['ema_cross_rsi_macd']['rsi_sensitivity']) &
                       (macd < macdsignal))

        return buy_signal, sell_signal

    def ema_rebound(self, data: pd.DataFrame):
        ema = talib.EMA(data['close'], timeperiod=self.config['strategies']['ema_rebound']['ema_period'])

        # Buy signal
        buy_signal = (data['low'] <= ema) & (data['close'] > ema)

        # Sell signal
        sell_signal = (data['high'] >= ema) & (data['close'] < ema)

        return buy_signal, sell_signal

    def bollinger_bands_breakout(self, data: pd.DataFrame):
        upper, middle, lower = talib.BBANDS(data['close'],
                                            timeperiod=self.config['strategies']['bollinger_bands_breakout']['bb_period'],
                                            nbdevup=self.config['strategies']['bollinger_bands_breakout']['bb_std_dev'],
                                            nbdevdn=self.config['strategies']['bollinger_bands_breakout']['bb_std_dev'])

        # Buy signal
        buy_signal = (data['close'] > upper) & (data['volume'] > data['volume'].shift(1))

        # Sell signal
        sell_signal = (data['close'] < lower) & (data['volume'] > data['volume'].shift(1))

        return buy_signal, sell_signal
