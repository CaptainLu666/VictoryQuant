"""
订单管理器
"""
from typing import Dict, List, Optional
from datetime import datetime
from .order import Order, OrderStatus, OrderType, OrderDirection


class OrderManager:
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.pending_orders: List[str] = []
        self.active_orders: List[str] = []
        self.completed_orders: List[str] = []
    
    def create_order(self, symbol: str, direction: OrderDirection, quantity: int,
                    order_type: OrderType, price: float = None, 
                    stop_price: float = None, strategy_id: str = None) -> Order:
        order = Order(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            order_type=order_type,
            price=price,
            stop_price=stop_price,
            strategy_id=strategy_id
        )
        
        self.orders[order.order_id] = order
        self.pending_orders.append(order.order_id)
        
        return order
    
    def create_market_order(self, symbol: str, direction: OrderDirection, 
                           quantity: int, strategy_id: str = None) -> Order:
        return self.create_order(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            order_type=OrderType.MARKET,
            strategy_id=strategy_id
        )
    
    def create_limit_order(self, symbol: str, direction: OrderDirection, 
                          quantity: int, price: float, 
                          strategy_id: str = None) -> Order:
        return self.create_order(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            order_type=OrderType.LIMIT,
            price=price,
            strategy_id=strategy_id
        )
    
    def create_stop_order(self, symbol: str, direction: OrderDirection, 
                         quantity: int, stop_price: float, 
                         strategy_id: str = None) -> Order:
        return self.create_order(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            order_type=OrderType.STOP,
            stop_price=stop_price,
            strategy_id=strategy_id
        )
    
    def create_stop_limit_order(self, symbol: str, direction: OrderDirection, 
                                quantity: int, price: float, stop_price: float,
                                strategy_id: str = None) -> Order:
        return self.create_order(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            order_type=OrderType.STOP_LIMIT,
            price=price,
            stop_price=stop_price,
            strategy_id=strategy_id
        )
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)
    
    def get_all_orders(self) -> List[Order]:
        return list(self.orders.values())
    
    def get_pending_orders(self) -> List[Order]:
        return [self.orders[oid] for oid in self.pending_orders if oid in self.orders]
    
    def get_active_orders(self) -> List[Order]:
        return [self.orders[oid] for oid in self.active_orders if oid in self.orders]
    
    def get_completed_orders(self) -> List[Order]:
        return [self.orders[oid] for oid in self.completed_orders if oid in self.orders]
    
    def get_orders_by_symbol(self, symbol: str) -> List[Order]:
        return [order for order in self.orders.values() if order.symbol == symbol]
    
    def get_orders_by_strategy(self, strategy_id: str) -> List[Order]:
        return [order for order in self.orders.values() if order.strategy_id == strategy_id]
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        return [order for order in self.orders.values() if order.status == status]
    
    def submit_order(self, order_id: str) -> bool:
        order = self.get_order(order_id)
        if order and order.status == OrderStatus.PENDING:
            order.status = OrderStatus.SUBMITTED
            order.update_time = datetime.now()
            
            if order_id in self.pending_orders:
                self.pending_orders.remove(order_id)
            self.active_orders.append(order_id)
            
            return True
        return False
    
    def fill_order(self, order_id: str, filled_quantity: int, filled_price: float,
                   commission: float = 0) -> bool:
        order = self.get_order(order_id)
        if order and order.is_active():
            order.update_fill(filled_quantity, filled_price, commission)
            
            if order.is_completed():
                if order_id in self.active_orders:
                    self.active_orders.remove(order_id)
                self.completed_orders.append(order_id)
            
            return True
        return False
    
    def cancel_order(self, order_id: str, reason: str = "") -> bool:
        order = self.get_order(order_id)
        if order and order.is_active():
            order.cancel(reason)
            
            if order_id in self.pending_orders:
                self.pending_orders.remove(order_id)
            if order_id in self.active_orders:
                self.active_orders.remove(order_id)
            self.completed_orders.append(order_id)
            
            return True
        return False
    
    def reject_order(self, order_id: str, reason: str = "") -> bool:
        order = self.get_order(order_id)
        if order and order.status == OrderStatus.PENDING:
            order.reject(reason)
            
            if order_id in self.pending_orders:
                self.pending_orders.remove(order_id)
            self.completed_orders.append(order_id)
            
            return True
        return False
    
    def cancel_all_orders(self, symbol: str = None):
        orders_to_cancel = self.get_active_orders()
        
        if symbol:
            orders_to_cancel = [o for o in orders_to_cancel if o.symbol == symbol]
        
        for order in orders_to_cancel:
            self.cancel_order(order.order_id, "批量取消")
    
    def get_order_statistics(self) -> Dict:
        return {
            'total_orders': len(self.orders),
            'pending_orders': len(self.pending_orders),
            'active_orders': len(self.active_orders),
            'completed_orders': len(self.completed_orders),
            'filled_orders': len([o for o in self.orders.values() if o.status == OrderStatus.FILLED]),
            'cancelled_orders': len([o for o in self.orders.values() if o.status == OrderStatus.CANCELLED]),
            'rejected_orders': len([o for o in self.orders.values() if o.status == OrderStatus.REJECTED])
        }
    
    def clear_completed_orders(self):
        for order_id in self.completed_orders[:]:
            if order_id in self.orders:
                del self.orders[order_id]
        self.completed_orders.clear()
    
    def reset(self):
        self.orders.clear()
        self.pending_orders.clear()
        self.active_orders.clear()
        self.completed_orders.clear()
