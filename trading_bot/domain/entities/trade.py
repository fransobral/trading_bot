from dataclasses import dataclass
from datetime import datetime
from trading_bot.domain.entities.order import OrderSide

@dataclass
class Trade:
    id: str
    symbol: str
    side: OrderSide
    amount: float
    price: float
    timestamp: datetime
    pnl: float = 0.0
