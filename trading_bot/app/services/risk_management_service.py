import pandas as pd
from domain.entities.order import Order
from domain.entities.trade import Trade

class RiskManagementService:
    def __init__(self, config):
        self.config = config

    def calculate_position_size(self, capital):
        return capital * self.config['risk_management']['risk_per_trade']

    def get_take_profit(self, entry_price, atr_value=None):
        """Calcula take profit dinámico usando ATR o estático"""
        if self.config['risk_management']['use_dynamic_tp'] and atr_value is not None:
            # TP dinámico: ATR x 2
            atr_multiplier = self.config['strategies']['advanced_ema_strategy']['atr_multiplier']
            return entry_price + (atr_value * atr_multiplier)
        else:
            # TP estático
            return entry_price * (1 + self.config['risk_management']['static_take_profit_percentage'])

    def get_stop_loss(self, entry_price, atr_value=None):
        """Calcula stop loss dinámico usando ATR o estático"""
        if self.config['risk_management']['use_dynamic_sl'] and atr_value is not None:
            # SL dinámico: ATR x 1 (más conservador)
            return entry_price - atr_value
        else:
            # SL estático
            return entry_price * (1 - self.config['risk_management']['static_stop_loss_percentage'])

    def get_take_profit_short(self, entry_price, atr_value=None):
        """Calcula take profit para posiciones short"""
        if self.config['risk_management']['use_dynamic_tp'] and atr_value is not None:
            atr_multiplier = self.config['strategies']['advanced_ema_strategy']['atr_multiplier']
            return entry_price - (atr_value * atr_multiplier)
        else:
            return entry_price * (1 - self.config['risk_management']['static_take_profit_percentage'])

    def get_stop_loss_short(self, entry_price, atr_value=None):
        """Calcula stop loss para posiciones short"""
        if self.config['risk_management']['use_dynamic_sl'] and atr_value is not None:
            return entry_price + atr_value
        else:
            return entry_price * (1 + self.config['risk_management']['static_stop_loss_percentage'])
