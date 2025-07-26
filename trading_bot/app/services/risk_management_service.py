import pandas as pd
from domain.entities.order import Order  # En lugar de trading_bot.domain.entities.order
from domain.entities.trade import Trade  # En lugar de trading_bot.domain.entities.trade

class RiskManagementService:
    def __init__(self, config):
        self.config = config

    def calculate_position_size(self, capital):
        return capital * self.config['risk_management']['risk_per_trade']

    def get_take_profit(self, entry_price):
        return entry_price * (1 + self.config['risk_management']['take_profit_percentage'])

    def get_stop_loss(self, entry_price):
        return entry_price * (1 - self.config['risk_management']['stop_loss_percentage'])
