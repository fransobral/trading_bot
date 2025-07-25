from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class OrderSide(Enum):
    BUY = 'buy'
    SELL = 'sell'

class OrderType(Enum):
    MARKET = 'market'
    LIMIT = 'limit'

@dataclass
class Order:
    id: str
    symbol: str
    type: OrderType
    side: OrderSide
    amount: float
    price: float
    timestamp: datetime
