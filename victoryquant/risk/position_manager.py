"""
仓位管理器
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Position:
    symbol: str
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    profit_loss: float
    profit_loss_ratio: float
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'avg_cost': self.avg_cost,
            'current_price': self.current_price,
            'market_value': self.market_value,
            'profit_loss': self.profit_loss,
            'profit_loss_ratio': self.profit_loss_ratio
        }


class PositionManager:
    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict] = {}
    
    def get_position(self, symbol: str) -> Optional[Position]:
        if symbol not in self.positions or self.positions[symbol]['quantity'] <= 0:
            return None
        
        pos = self.positions[symbol]
        return Position(
            symbol=symbol,
            quantity=pos['quantity'],
            avg_cost=pos['avg_cost'],
            current_price=pos.get('current_price', pos['avg_cost']),
            market_value=pos['quantity'] * pos.get('current_price', pos['avg_cost']),
            profit_loss=(pos.get('current_price', pos['avg_cost']) - pos['avg_cost']) * pos['quantity'],
            profit_loss_ratio=(pos.get('current_price', pos['avg_cost']) - pos['avg_cost']) / pos['avg_cost'] if pos['avg_cost'] > 0 else 0
        )
    
    def get_all_positions(self) -> List[Position]:
        positions = []
        for symbol in self.positions:
            pos = self.get_position(symbol)
            if pos:
                positions.append(pos)
        return positions
    
    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions and self.positions[symbol]['quantity'] > 0
    
    def get_position_quantity(self, symbol: str) -> int:
        if symbol in self.positions:
            return self.positions[symbol]['quantity']
        return 0
    
    def get_position_value(self, symbol: str) -> float:
        pos = self.get_position(symbol)
        return pos.market_value if pos else 0
    
    def get_total_position_value(self) -> float:
        total = 0
        for symbol in self.positions:
            pos = self.get_position(symbol)
            if pos:
                total += pos.market_value
        return total
    
    def get_total_value(self) -> float:
        return self.cash + self.get_total_position_value()
    
    def get_total_profit_loss(self) -> float:
        total = 0
        for symbol in self.positions:
            pos = self.get_position(symbol)
            if pos:
                total += pos.profit_loss
        return total
    
    def update_position(self, symbol: str, quantity: int, price: float, is_buy: bool):
        if symbol not in self.positions:
            self.positions[symbol] = {
                'quantity': 0,
                'avg_cost': 0,
                'total_cost': 0,
                'current_price': price
            }
        
        pos = self.positions[symbol]
        
        if is_buy:
            amount = quantity * price
            pos['total_cost'] += amount
            pos['quantity'] += quantity
            pos['avg_cost'] = pos['total_cost'] / pos['quantity'] if pos['quantity'] > 0 else 0
            self.cash -= amount
        else:
            if pos['quantity'] >= quantity:
                pos['quantity'] -= quantity
                revenue = quantity * price
                self.cash += revenue
                
                if pos['quantity'] <= 0:
                    pos['quantity'] = 0
                    pos['total_cost'] = 0
                    pos['avg_cost'] = 0
        
        pos['current_price'] = price
    
    def update_current_prices(self, prices: Dict[str, float]):
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol]['current_price'] = price
    
    def get_position_weights(self) -> Dict[str, float]:
        total_value = self.get_total_value()
        weights = {}
        
        for symbol in self.positions:
            pos = self.get_position(symbol)
            if pos and total_value > 0:
                weights[symbol] = pos.market_value / total_value
        
        return weights
    
    def get_position_summary(self) -> Dict:
        positions = self.get_all_positions()
        
        total_market_value = sum(p.market_value for p in positions)
        total_profit_loss = sum(p.profit_loss for p in positions)
        
        return {
            'total_value': self.get_total_value(),
            'cash': self.cash,
            'position_value': total_market_value,
            'position_count': len(positions),
            'total_profit_loss': total_profit_loss,
            'positions': [p.to_dict() for p in positions]
        }
    
    def calculate_position_concentration(self) -> Dict[str, float]:
        weights = self.get_position_weights()
        
        if not weights:
            return {'max_weight': 0, 'avg_weight': 0, 'herfindahl': 0}
        
        max_weight = max(weights.values())
        avg_weight = sum(weights.values()) / len(weights)
        herfindahl = sum(w ** 2 for w in weights.values())
        
        return {
            'max_weight': max_weight,
            'avg_weight': avg_weight,
            'herfindahl': herfindahl
        }
    
    def rebalance_positions(self, target_weights: Dict[str, float], 
                           prices: Dict[str, float]) -> Dict[str, int]:
        total_value = self.get_total_value()
        
        target_values = {
            symbol: total_value * weight 
            for symbol, weight in target_weights.items()
        }
        
        adjustments = {}
        
        for symbol, target_value in target_values.items():
            if symbol not in prices:
                continue
            
            price = prices[symbol]
            target_quantity = int(target_value / price)
            min_unit = 100
            target_quantity = (target_quantity // min_unit) * min_unit
            
            current_quantity = self.get_position_quantity(symbol)
            adjustment = target_quantity - current_quantity
            
            if adjustment != 0:
                adjustments[symbol] = adjustment
        
        for symbol in self.positions:
            if symbol not in target_weights:
                current_quantity = self.get_position_quantity(symbol)
                if current_quantity > 0:
                    adjustments[symbol] = -current_quantity
        
        return adjustments
    
    def clear_position(self, symbol: str, price: float) -> float:
        if symbol not in self.positions:
            return 0
        
        quantity = self.positions[symbol]['quantity']
        if quantity <= 0:
            return 0
        
        revenue = quantity * price
        self.cash += revenue
        
        self.positions[symbol] = {
            'quantity': 0,
            'avg_cost': 0,
            'total_cost': 0,
            'current_price': price
        }
        
        return revenue
    
    def clear_all_positions(self, prices: Dict[str, float]) -> float:
        total_revenue = 0
        
        for symbol in list(self.positions.keys()):
            if symbol in prices:
                revenue = self.clear_position(symbol, prices[symbol])
                total_revenue += revenue
        
        return total_revenue
    
    def reset(self):
        self.cash = self.initial_capital
        self.positions.clear()
