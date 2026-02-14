"""
回测引擎
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.base.base_strategy import BaseStrategy
from strategy.base.signal import Signal, SignalType
from performance_analyzer import PerformanceAnalyzer


class BacktestEngine:
    def __init__(self, initial_capital: float = 1000000.0, 
                 commission_rate: float = 0.0003,
                 stamp_duty_rate: float = 0.001,
                 slippage: float = 0.001):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.stamp_duty_rate = stamp_duty_rate
        self.slippage = slippage
        
        self.cash = initial_capital
        self.positions = {}
        self.trades = []
        self.daily_values = []
        self.performance_analyzer = PerformanceAnalyzer()
    
    def reset(self):
        self.cash = self.initial_capital
        self.positions = {}
        self.trades = []
        self.daily_values = []
    
    def run_backtest(self, strategy: BaseStrategy, data: pd.DataFrame, 
                     symbol: str = None) -> Dict:
        self.reset()
        
        if data.empty:
            return {'error': '数据为空'}
        
        signals = strategy.generate_signals(data)
        
        if symbol:
            for signal in signals:
                signal.symbol = symbol
        
        for idx, row in data.iterrows():
            current_date = idx if isinstance(idx, datetime) else pd.to_datetime(idx)
            current_price = row['close']
            
            self._process_signals(signals, current_date, current_price)
            
            self._update_daily_value(current_date, current_price)
        
        return self._generate_result(strategy.name)
    
    def run_backtest_multiple(self, strategy: BaseStrategy, 
                             data_dict: Dict[str, pd.DataFrame]) -> Dict:
        self.reset()
        
        all_signals = []
        
        for symbol, data in data_dict.items():
            signals = strategy.generate_signals(data)
            for signal in signals:
                signal.symbol = symbol
            all_signals.extend(signals)
        
        all_signals.sort(key=lambda x: x.timestamp)
        
        common_dates = None
        for symbol, data in data_dict.items():
            if common_dates is None:
                common_dates = set(data.index)
            else:
                common_dates = common_dates.intersection(set(data.index))
        
        common_dates = sorted(list(common_dates))
        
        for date in common_dates:
            current_signals = [s for s in all_signals if s.timestamp == date]
            
            for symbol, data in data_dict.items():
                if date in data.index:
                    current_price = data.loc[date, 'close']
                    self._process_signals(current_signals, date, current_price)
            
            total_value = self.cash
            for sym, pos in self.positions.items():
                if sym in data_dict and date in data_dict[sym].index:
                    price = data_dict[sym].loc[date, 'close']
                    total_value += pos['quantity'] * price
            
            self.daily_values.append({
                'date': date,
                'total_value': total_value,
                'cash': self.cash,
                'position_value': total_value - self.cash
            })
        
        return self._generate_result(strategy.name)
    
    def _process_signals(self, signals: List[Signal], current_date: datetime, 
                        current_price: float):
        for signal in signals:
            if signal.timestamp.date() != current_date.date():
                continue
            
            if signal.signal_type == SignalType.BUY:
                self._execute_buy(signal, current_price)
            elif signal.signal_type == SignalType.SELL:
                self._execute_sell(signal, current_price)
    
    def _execute_buy(self, signal: Signal, price: float):
        actual_price = price * (1 + self.slippage)
        
        max_quantity = int(self.cash / actual_price)
        min_unit = 100
        quantity = (max_quantity // min_unit) * min_unit
        
        if quantity < min_unit:
            return
        
        if signal.quantity and signal.quantity > 0:
            quantity = min(quantity, signal.quantity)
            quantity = (quantity // min_unit) * min_unit
        
        amount = quantity * actual_price
        commission = max(amount * self.commission_rate, 5)
        
        total_cost = amount + commission
        
        if total_cost > self.cash:
            return
        
        self.cash -= total_cost
        
        symbol = signal.symbol
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
        
        self.trades.append({
            'date': signal.timestamp,
            'symbol': symbol,
            'direction': 'BUY',
            'price': actual_price,
            'quantity': quantity,
            'amount': amount,
            'commission': commission,
            'cash_after': self.cash
        })
    
    def _execute_sell(self, signal: Signal, price: float):
        symbol = signal.symbol
        
        if symbol not in self.positions or self.positions[symbol]['quantity'] <= 0:
            return
        
        pos = self.positions[symbol]
        quantity = pos['quantity']
        
        if signal.quantity and signal.quantity > 0:
            quantity = min(quantity, signal.quantity)
            min_unit = 100
            quantity = (quantity // min_unit) * min_unit
        
        if quantity <= 0:
            return
        
        actual_price = price * (1 - self.slippage)
        amount = quantity * actual_price
        commission = max(amount * self.commission_rate, 5)
        stamp_duty = amount * self.stamp_duty_rate
        
        total_revenue = amount - commission - stamp_duty
        
        self.cash += total_revenue
        
        cost = quantity * pos['avg_cost']
        profit = amount - cost
        
        pos['quantity'] -= quantity
        if pos['quantity'] <= 0:
            pos['quantity'] = 0
            pos['total_cost'] = 0
            pos['avg_cost'] = 0
        else:
            pos['total_cost'] = pos['quantity'] * pos['avg_cost']
        
        self.trades.append({
            'date': signal.timestamp,
            'symbol': symbol,
            'direction': 'SELL',
            'price': actual_price,
            'quantity': quantity,
            'amount': amount,
            'commission': commission + stamp_duty,
            'profit': profit,
            'cash_after': self.cash
        })
    
    def _update_daily_value(self, date: datetime, current_price: float):
        position_value = 0
        for symbol, pos in self.positions.items():
            position_value += pos['quantity'] * current_price
        
        total_value = self.cash + position_value
        
        self.daily_values.append({
            'date': date,
            'total_value': total_value,
            'cash': self.cash,
            'position_value': position_value
        })
    
    def _generate_result(self, strategy_name: str) -> Dict:
        if not self.daily_values:
            return {'error': '没有交易记录'}
        
        df_values = pd.DataFrame(self.daily_values)
        df_values['date'] = pd.to_datetime(df_values['date'])
        df_values.set_index('date', inplace=True)
        
        performance = self.performance_analyzer.analyze(
            df_values, 
            self.initial_capital
        )
        
        return {
            'strategy_name': strategy_name,
            'initial_capital': self.initial_capital,
            'final_value': df_values['total_value'].iloc[-1],
            'trades': self.trades,
            'daily_values': self.daily_values,
            'performance': performance
        }
    
    def get_current_positions(self) -> Dict:
        return {k: v for k, v in self.positions.items() if v['quantity'] > 0}
    
    def get_trade_count(self) -> int:
        return len(self.trades)
    
    def get_profitable_trades(self) -> List[Dict]:
        return [t for t in self.trades if t.get('profit', 0) > 0]
    
    def get_losing_trades(self) -> List[Dict]:
        return [t for t in self.trades if t.get('profit', 0) < 0]
