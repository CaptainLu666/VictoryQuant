"""
均线策略
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
from ..base.base_strategy import BaseStrategy
from ..base.signal import Signal, SignalType


class MAStrategy(BaseStrategy):
    def __init__(self, fast_period: int = 5, slow_period: int = 20, 
                 stop_loss: float = 0.08, take_profit: float = 0.15):
        params = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'stop_loss': stop_loss,
            'take_profit': take_profit
        }
        super().__init__("MA_Strategy", params)
    
    def _validate_params(self):
        if self.params['fast_period'] >= self.params['slow_period']:
            raise ValueError("快线周期必须小于慢线周期")
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        signals = []
        
        if data.empty:
            return signals
        
        fast_period = self.params['fast_period']
        slow_period = self.params['slow_period']
        
        data = data.copy()
        data['MA_Fast'] = data['close'].rolling(window=fast_period).mean()
        data['MA_Slow'] = data['close'].rolling(window=slow_period).mean()
        
        data['Golden_Cross'] = (
            (data['MA_Fast'] > data['MA_Slow']) & 
            (data['MA_Fast'].shift(1) <= data['MA_Slow'].shift(1))
        ).astype(int)
        
        data['Death_Cross'] = (
            (data['MA_Fast'] < data['MA_Slow']) & 
            (data['MA_Fast'].shift(1) >= data['MA_Slow'].shift(1))
        ).astype(int)
        
        for idx, row in data.iterrows():
            if pd.isna(row['MA_Fast']) or pd.isna(row['MA_Slow']):
                continue
            
            timestamp = idx if isinstance(idx, datetime) else datetime.now()
            
            if row['Golden_Cross'] == 1:
                signal = Signal(
                    symbol='',
                    signal_type=SignalType.BUY,
                    price=row['close'],
                    timestamp=timestamp,
                    strength=1.0,
                    metadata={
                        'MA_Fast': row['MA_Fast'],
                        'MA_Slow': row['MA_Slow'],
                        'reason': 'golden_cross'
                    }
                )
                signals.append(signal)
                self.record_signal(signal)
            
            elif row['Death_Cross'] == 1:
                signal = Signal(
                    symbol='',
                    signal_type=SignalType.SELL,
                    price=row['close'],
                    timestamp=timestamp,
                    strength=1.0,
                    metadata={
                        'MA_Fast': row['MA_Fast'],
                        'MA_Slow': row['MA_Slow'],
                        'reason': 'death_cross'
                    }
                )
                signals.append(signal)
                self.record_signal(signal)
        
        return signals
    
    def generate_signal_for_symbol(self, symbol: str, data: pd.DataFrame) -> List[Signal]:
        signals = self.generate_signals(data)
        
        for signal in signals:
            signal.symbol = symbol
        
        return signals
