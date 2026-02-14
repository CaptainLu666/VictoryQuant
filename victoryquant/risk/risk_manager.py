"""
风险管理器
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class RiskMetrics:
    max_position_ratio: float
    max_single_stock_ratio: float
    max_daily_loss_ratio: float
    max_drawdown_ratio: float
    current_position_ratio: float
    current_daily_pnl_ratio: float
    current_drawdown_ratio: float
    risk_level: str


class RiskManager:
    def __init__(self, max_position_ratio: float = 0.8,
                 max_single_stock_ratio: float = 0.2,
                 max_daily_loss_ratio: float = 0.05,
                 max_drawdown_ratio: float = 0.15,
                 stop_loss_ratio: float = 0.08,
                 take_profit_ratio: float = 0.15):
        self.max_position_ratio = max_position_ratio
        self.max_single_stock_ratio = max_single_stock_ratio
        self.max_daily_loss_ratio = max_daily_loss_ratio
        self.max_drawdown_ratio = max_drawdown_ratio
        self.stop_loss_ratio = stop_loss_ratio
        self.take_profit_ratio = take_profit_ratio
        
        self.initial_capital = 0
        self.peak_value = 0
        self.daily_start_value = 0
        self.daily_pnl = 0
    
    def initialize(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.peak_value = initial_capital
        self.daily_start_value = initial_capital
        self.daily_pnl = 0
    
    def update_daily_start(self, current_value: float):
        self.daily_start_value = current_value
        self.daily_pnl = 0
    
    def update_value(self, current_value: float):
        if current_value > self.peak_value:
            self.peak_value = current_value
    
    def calculate_position_ratio(self, position_value: float, total_value: float) -> float:
        if total_value == 0:
            return 0
        return position_value / total_value
    
    def calculate_single_stock_ratio(self, stock_value: float, total_value: float) -> float:
        if total_value == 0:
            return 0
        return stock_value / total_value
    
    def calculate_daily_pnl_ratio(self, current_value: float) -> float:
        if self.daily_start_value == 0:
            return 0
        return (current_value - self.daily_start_value) / self.daily_start_value
    
    def calculate_drawdown_ratio(self, current_value: float) -> float:
        if self.peak_value == 0:
            return 0
        return (self.peak_value - current_value) / self.peak_value
    
    def check_position_limit(self, position_value: float, total_value: float) -> bool:
        ratio = self.calculate_position_ratio(position_value, total_value)
        return ratio <= self.max_position_ratio
    
    def check_single_stock_limit(self, stock_value: float, total_value: float) -> bool:
        ratio = self.calculate_single_stock_ratio(stock_value, total_value)
        return ratio <= self.max_single_stock_ratio
    
    def check_daily_loss_limit(self, current_value: float) -> bool:
        ratio = self.calculate_daily_pnl_ratio(current_value)
        return ratio >= -self.max_daily_loss_ratio
    
    def check_drawdown_limit(self, current_value: float) -> bool:
        ratio = self.calculate_drawdown_ratio(current_value)
        return ratio <= self.max_drawdown_ratio
    
    def check_stop_loss(self, avg_cost: float, current_price: float) -> bool:
        if avg_cost == 0:
            return False
        loss_ratio = (current_price - avg_cost) / avg_cost
        return loss_ratio <= -self.stop_loss_ratio
    
    def check_take_profit(self, avg_cost: float, current_price: float) -> bool:
        if avg_cost == 0:
            return False
        profit_ratio = (current_price - avg_cost) / avg_cost
        return profit_ratio >= self.take_profit_ratio
    
    def get_risk_metrics(self, position_value: float, total_value: float,
                        positions: Dict) -> RiskMetrics:
        current_position_ratio = self.calculate_position_ratio(position_value, total_value)
        current_daily_pnl_ratio = self.calculate_daily_pnl_ratio(total_value)
        current_drawdown_ratio = self.calculate_drawdown_ratio(total_value)
        
        risk_score = 0
        if current_position_ratio > self.max_position_ratio:
            risk_score += 2
        elif current_position_ratio > self.max_position_ratio * 0.8:
            risk_score += 1
        
        if current_daily_pnl_ratio < -self.max_daily_loss_ratio:
            risk_score += 3
        elif current_daily_pnl_ratio < -self.max_daily_loss_ratio * 0.5:
            risk_score += 1
        
        if current_drawdown_ratio > self.max_drawdown_ratio:
            risk_score += 3
        elif current_drawdown_ratio > self.max_drawdown_ratio * 0.5:
            risk_score += 1
        
        for symbol, pos in positions.items():
            stock_value = pos.get('quantity', 0) * pos.get('current_price', 0)
            stock_ratio = self.calculate_single_stock_ratio(stock_value, total_value)
            if stock_ratio > self.max_single_stock_ratio:
                risk_score += 1
        
        if risk_score >= 5:
            risk_level = "HIGH"
        elif risk_score >= 3:
            risk_level = "MEDIUM"
        elif risk_score >= 1:
            risk_level = "LOW"
        else:
            risk_level = "SAFE"
        
        return RiskMetrics(
            max_position_ratio=self.max_position_ratio,
            max_single_stock_ratio=self.max_single_stock_ratio,
            max_daily_loss_ratio=self.max_daily_loss_ratio,
            max_drawdown_ratio=self.max_drawdown_ratio,
            current_position_ratio=current_position_ratio,
            current_daily_pnl_ratio=current_daily_pnl_ratio,
            current_drawdown_ratio=current_drawdown_ratio,
            risk_level=risk_level
        )
    
    def should_reduce_position(self, current_value: float, position_value: float) -> bool:
        if not self.check_daily_loss_limit(current_value):
            return True
        if not self.check_drawdown_limit(current_value):
            return True
        if not self.check_position_limit(position_value, current_value):
            return True
        return False
    
    def calculate_max_position_size(self, total_value: float, price: float) -> int:
        max_value = total_value * self.max_single_stock_ratio
        max_quantity = int(max_value / price)
        min_unit = 100
        return (max_quantity // min_unit) * min_unit
    
    def get_risk_report(self, total_value: float, position_value: float,
                       positions: Dict) -> Dict:
        metrics = self.get_risk_metrics(position_value, total_value, positions)
        
        warnings = []
        if metrics.current_position_ratio > self.max_position_ratio:
            warnings.append(f"仓位比例 {metrics.current_position_ratio:.2%} 超过限制 {self.max_position_ratio:.2%}")
        
        if metrics.current_daily_pnl_ratio < -self.max_daily_loss_ratio:
            warnings.append(f"当日亏损 {metrics.current_daily_pnl_ratio:.2%} 超过限制 {self.max_daily_loss_ratio:.2%}")
        
        if metrics.current_drawdown_ratio > self.max_drawdown_ratio:
            warnings.append(f"最大回撤 {metrics.current_drawdown_ratio:.2%} 超过限制 {self.max_drawdown_ratio:.2%}")
        
        return {
            'risk_level': metrics.risk_level,
            'position_ratio': metrics.current_position_ratio,
            'daily_pnl_ratio': metrics.current_daily_pnl_ratio,
            'drawdown_ratio': metrics.current_drawdown_ratio,
            'warnings': warnings,
            'should_reduce': self.should_reduce_position(total_value, position_value)
        }
