"""
订单定义
"""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL_FILLED = "partial_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderDirection(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    symbol: str
    direction: OrderDirection
    quantity: int
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    filled_price: float = 0.0
    commission: float = 0.0
    order_id: Optional[str] = None
    strategy_id: Optional[str] = None
    create_time: datetime = None
    update_time: datetime = None
    message: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.create_time is None:
            self.create_time = datetime.now()
        if self.update_time is None:
            self.update_time = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        if self.order_id is None:
            self.order_id = self._generate_order_id()
    
    def _generate_order_id(self) -> str:
        return f"{self.symbol}_{self.direction.value}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def is_buy(self) -> bool:
        return self.direction == OrderDirection.BUY
    
    def is_sell(self) -> bool:
        return self.direction == OrderDirection.SELL
    
    def is_active(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL_FILLED]
    
    def is_completed(self) -> bool:
        return self.status == OrderStatus.FILLED
    
    def is_cancelled(self) -> bool:
        return self.status == OrderStatus.CANCELLED
    
    def is_rejected(self) -> bool:
        return self.status == OrderStatus.REJECTED
    
    def get_unfilled_quantity(self) -> int:
        return self.quantity - self.filled_quantity
    
    def get_filled_amount(self) -> float:
        return self.filled_quantity * self.filled_price
    
    def update_fill(self, filled_quantity: int, filled_price: float, commission: float = 0):
        self.filled_quantity += filled_quantity
        self.filled_price = (self.filled_price * (self.filled_quantity - filled_quantity) + 
                            filled_price * filled_quantity) / self.filled_quantity if self.filled_quantity > 0 else 0
        self.commission += commission
        self.update_time = datetime.now()
        
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        elif self.filled_quantity > 0:
            self.status = OrderStatus.PARTIAL_FILLED
    
    def cancel(self, reason: str = ""):
        if self.is_active():
            self.status = OrderStatus.CANCELLED
            self.message = reason
            self.update_time = datetime.now()
    
    def reject(self, reason: str = ""):
        self.status = OrderStatus.REJECTED
        self.message = reason
        self.update_time = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'direction': self.direction.value,
            'quantity': self.quantity,
            'order_type': self.order_type.value,
            'price': self.price,
            'stop_price': self.stop_price,
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'filled_price': self.filled_price,
            'commission': self.commission,
            'strategy_id': self.strategy_id,
            'create_time': self.create_time.isoformat(),
            'update_time': self.update_time.isoformat(),
            'message': self.message,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Order':
        return cls(
            symbol=data['symbol'],
            direction=OrderDirection(data['direction']),
            quantity=data['quantity'],
            order_type=OrderType(data['order_type']),
            price=data.get('price'),
            stop_price=data.get('stop_price'),
            status=OrderStatus(data['status']),
            filled_quantity=data.get('filled_quantity', 0),
            filled_price=data.get('filled_price', 0.0),
            commission=data.get('commission', 0.0),
            order_id=data.get('order_id'),
            strategy_id=data.get('strategy_id'),
            create_time=datetime.fromisoformat(data['create_time']),
            update_time=datetime.fromisoformat(data['update_time']),
            message=data.get('message', ''),
            metadata=data.get('metadata', {})
        )
    
    def __str__(self) -> str:
        return f"Order({self.order_id}, {self.symbol}, {self.direction.value}, {self.quantity}@{self.price}, {self.status.value})"
