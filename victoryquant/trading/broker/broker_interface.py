"""
券商接口模块
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from order.order import Order, OrderStatus, OrderType, OrderDirection


class BrokerInterface(ABC):
    def __init__(self):
        self.connected = False
        self.account_info = {}
    
    @abstractmethod
    def connect(self, **kwargs) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        return self.connected
    
    @abstractmethod
    def submit_order(self, order: Order) -> bool:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> OrderStatus:
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict:
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict:
        pass
    
    @abstractmethod
    def get_today_trades(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def get_today_orders(self) -> List[Dict]:
        pass


class SimulatedBroker(BrokerInterface):
    def __init__(self, initial_capital: float = 1000000.0):
        super().__init__()
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.orders = {}
        self.trades = []
        self.commission_rate = 0.0003
        self.stamp_duty_rate = 0.001
        self.slippage = 0.001
    
    def connect(self, **kwargs) -> bool:
        self.connected = True
        return True
    
    def disconnect(self) -> bool:
        self.connected = False
        return True
    
    def is_connected(self) -> bool:
        return self.connected
    
    def submit_order(self, order: Order) -> bool:
        if not self.connected:
            return False
        
        self.orders[order.order_id] = order
        order.status = OrderStatus.SUBMITTED
        
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.is_active():
                order.cancel("用户取消")
                return True
        return False
    
    def get_order_status(self, order_id: str) -> OrderStatus:
        if order_id in self.orders:
            return self.orders[order_id].status
        return OrderStatus.REJECTED
    
    def get_positions(self) -> Dict:
        return {k: v for k, v in self.positions.items() if v['quantity'] > 0}
    
    def get_account_info(self) -> Dict:
        position_value = sum(
            pos['quantity'] * pos.get('current_price', pos['avg_cost'])
            for pos in self.positions.values()
        )
        
        return {
            'total_value': self.cash + position_value,
            'cash': self.cash,
            'position_value': position_value,
            'initial_capital': self.initial_capital
        }
    
    def get_balance(self) -> Dict:
        return {
            'cash': self.cash,
            'available': self.cash
        }
    
    def get_today_trades(self) -> List[Dict]:
        return self.trades
    
    def get_today_orders(self) -> List[Dict]:
        return [order.to_dict() for order in self.orders.values()]
    
    def execute_order(self, order: Order, current_price: float) -> bool:
        if not self.connected:
            return False
        
        if order.direction == OrderDirection.BUY:
            return self._execute_buy(order, current_price)
        else:
            return self._execute_sell(order, current_price)
    
    def _execute_buy(self, order: Order, current_price: float) -> bool:
        if order.order_type == OrderType.MARKET:
            execution_price = current_price * (1 + self.slippage)
        elif order.order_type == OrderType.LIMIT:
            if order.price < current_price:
                return False
            execution_price = order.price
        else:
            return False
        
        quantity = order.quantity
        amount = quantity * execution_price
        commission = max(amount * self.commission_rate, 5)
        total_cost = amount + commission
        
        if total_cost > self.cash:
            order.reject("资金不足")
            return False
        
        self.cash -= total_cost
        
        symbol = order.symbol
        if symbol not in self.positions:
            self.positions[symbol] = {
                'quantity': 0,
                'avg_cost': 0,
                'total_cost': 0
            }
        
        pos = self.positions[symbol]
        pos['total_cost'] += amount
        pos['quantity'] += quantity
        pos['avg_cost'] = pos['total_cost'] / pos['quantity']
        
        order.update_fill(quantity, execution_price, commission)
        
        self.trades.append({
            'order_id': order.order_id,
            'symbol': symbol,
            'direction': 'BUY',
            'price': execution_price,
            'quantity': quantity,
            'amount': amount,
            'commission': commission,
            'timestamp': datetime.now().isoformat()
        })
        
        return True
    
    def _execute_sell(self, order: Order, current_price: float) -> bool:
        symbol = order.symbol
        
        if symbol not in self.positions or self.positions[symbol]['quantity'] < order.quantity:
            order.reject("持仓不足")
            return False
        
        if order.order_type == OrderType.MARKET:
            execution_price = current_price * (1 - self.slippage)
        elif order.order_type == OrderType.LIMIT:
            if order.price > current_price:
                return False
            execution_price = order.price
        else:
            return False
        
        quantity = order.quantity
        amount = quantity * execution_price
        commission = max(amount * self.commission_rate, 5)
        stamp_duty = amount * self.stamp_duty_rate
        
        total_revenue = amount - commission - stamp_duty
        
        self.cash += total_revenue
        
        pos = self.positions[symbol]
        cost = quantity * pos['avg_cost']
        profit = amount - cost
        
        pos['quantity'] -= quantity
        if pos['quantity'] <= 0:
            pos['quantity'] = 0
            pos['total_cost'] = 0
            pos['avg_cost'] = 0
        else:
            pos['total_cost'] = pos['quantity'] * pos['avg_cost']
        
        order.update_fill(quantity, execution_price, commission + stamp_duty)
        
        self.trades.append({
            'order_id': order.order_id,
            'symbol': symbol,
            'direction': 'SELL',
            'price': execution_price,
            'quantity': quantity,
            'amount': amount,
            'commission': commission + stamp_duty,
            'profit': profit,
            'timestamp': datetime.now().isoformat()
        })
        
        return True
    
    def update_position_price(self, symbol: str, current_price: float):
        if symbol in self.positions:
            self.positions[symbol]['current_price'] = current_price
    
    def reset(self):
        self.cash = self.initial_capital
        self.positions = {}
        self.orders = {}
        self.trades = []
