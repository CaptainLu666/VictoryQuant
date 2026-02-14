"""
基础策略类
"""
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from .signal import Signal, SignalType


class BaseStrategy(ABC):
    def __init__(self, name: str, params: Dict = None):
        self.name = name
        self.params = params or {}
        self.positions = {}
        self.signals_history = []
        self._validate_params()
    
    def _validate_params(self):
        pass
    
    def set_param(self, key: str, value: Any):
        self.params[key] = value
    
    def get_param(self, key: str, default: Any = None) -> Any:
        return self.params.get(key, default)
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        pass
    
    def update_positions(self, symbol: str, quantity: int, price: float):
        if symbol not in self.positions:
            self.positions[symbol] = {
                'quantity': 0,
                'avg_cost': 0,
                'total_cost': 0
            }
        
        pos = self.positions[symbol]
        
        if quantity > 0:
            pos['total_cost'] += quantity * price
            pos['quantity'] += quantity
            pos['avg_cost'] = pos['total_cost'] / pos['quantity'] if pos['quantity'] > 0 else 0
        else:
            sell_quantity = abs(quantity)
            if sell_quantity >= pos['quantity']:
                pos['quantity'] = 0
                pos['total_cost'] = 0
                pos['avg_cost'] = 0
            else:
                pos['quantity'] -= sell_quantity
                pos['total_cost'] = pos['quantity'] * pos['avg_cost']
    
    def get_position(self, symbol: str) -> Dict:
        return self.positions.get(symbol, {'quantity': 0, 'avg_cost': 0, 'total_cost': 0})
    
    def has_position(self, symbol: str) -> bool:
        return self.get_position(symbol)['quantity'] > 0
    
    def get_all_positions(self) -> Dict:
        return {k: v for k, v in self.positions.items() if v['quantity'] > 0}
    
    def clear_position(self, symbol: str):
        if symbol in self.positions:
            self.positions[symbol] = {'quantity': 0, 'avg_cost': 0, 'total_cost': 0}
    
    def clear_all_positions(self):
        self.positions = {}
    
    def record_signal(self, signal: Signal):
        self.signals_history.append(signal)
    
    def get_signals_history(self, symbol: str = None) -> List[Signal]:
        if symbol:
            return [s for s in self.signals_history if s.symbol == symbol]
        return self.signals_history
    
    def calculate_position_size(self, symbol: str, price: float, 
                                total_capital: float, risk_ratio: float = 0.02) -> int:
        risk_amount = total_capital * risk_ratio
        quantity = int(risk_amount / price)
        
        min_unit = 100
        quantity = (quantity // min_unit) * min_unit
        
        return max(quantity, min_unit)
    
    def apply_stop_loss(self, data: pd.DataFrame, stop_loss_ratio: float = 0.08) -> List[Signal]:
        signals = []
        
        for symbol, pos in self.positions.items():
            if pos['quantity'] > 0:
                if symbol in data.index:
                    current_price = data.loc[symbol, 'close'] if 'close' in data.columns else None
                    
                    if current_price:
                        loss_ratio = (current_price - pos['avg_cost']) / pos['avg_cost']
                        
                        if loss_ratio <= -stop_loss_ratio:
                            signal = Signal(
                                symbol=symbol,
                                signal_type=SignalType.SELL,
                                price=current_price,
                                timestamp=datetime.now(),
                                strength=1.0,
                                quantity=pos['quantity'],
                                metadata={'reason': 'stop_loss', 'loss_ratio': loss_ratio}
                            )
                            signals.append(signal)
        
        return signals
    
    def apply_take_profit(self, data: pd.DataFrame, take_profit_ratio: float = 0.15) -> List[Signal]:
        signals = []
        
        for symbol, pos in self.positions.items():
            if pos['quantity'] > 0:
                if symbol in data.index:
                    current_price = data.loc[symbol, 'close'] if 'close' in data.columns else None
                    
                    if current_price:
                        profit_ratio = (current_price - pos['avg_cost']) / pos['avg_cost']
                        
                        if profit_ratio >= take_profit_ratio:
                            signal = Signal(
                                symbol=symbol,
                                signal_type=SignalType.SELL,
                                price=current_price,
                                timestamp=datetime.now(),
                                strength=1.0,
                                quantity=pos['quantity'],
                                metadata={'reason': 'take_profit', 'profit_ratio': profit_ratio}
                            )
                            signals.append(signal)
        
        return signals
    
    def get_strategy_info(self) -> Dict:
        return {
            'name': self.name,
            'params': self.params,
            'positions': self.get_all_positions(),
            'signals_count': len(self.signals_history)
        }
    
    def reset(self):
        self.positions = {}
        self.signals_history = []
    
    def __str__(self) -> str:
        return f"Strategy({self.name}, params={self.params})"
    
    def __repr__(self) -> str:
        return self.__str__()
