"""
交易信号定义
"""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


class SignalType(Enum):
    BUY = 1
    SELL = 2
    HOLD = 0
    CLOSE_LONG = 3
    CLOSE_SHORT = 4


@dataclass
class Signal:
    symbol: str
    signal_type: SignalType
    price: float
    timestamp: datetime
    strength: float = 1.0
    quantity: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'signal_type': self.signal_type.name,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'strength': self.strength,
            'quantity': self.quantity,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Signal':
        return cls(
            symbol=data['symbol'],
            signal_type=SignalType[data['signal_type']],
            price=data['price'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            strength=data.get('strength', 1.0),
            quantity=data.get('quantity'),
            metadata=data.get('metadata', {})
        )
    
    def is_buy(self) -> bool:
        return self.signal_type == SignalType.BUY
    
    def is_sell(self) -> bool:
        return self.signal_type == SignalType.SELL
    
    def is_hold(self) -> bool:
        return self.signal_type == SignalType.HOLD
    
    def is_close_position(self) -> bool:
        return self.signal_type in [SignalType.CLOSE_LONG, SignalType.CLOSE_SHORT]
    
    def __str__(self) -> str:
        return f"Signal({self.symbol}, {self.signal_type.name}, price={self.price}, strength={self.strength})"
