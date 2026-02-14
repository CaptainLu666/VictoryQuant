"""
MACD策略
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
from ..base.base_strategy import BaseStrategy
from ..base.signal import Signal, SignalType


class MACDStrategy(BaseStrategy):
    def __init__(self, fast_period: int = 12, slow_period: int = 26, 
                 signal_period: int = 9, stop_loss: float = 0.08):
        params = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period,
            'stop_loss': stop_loss
        }
        super().__init__("MACD_Strategy", params)
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        signals = []
        
        if data.empty:
            return signals
        
        fast_period = self.params['fast_period']
        slow_period = self.params['slow_period']
        signal_period = self.params['signal_period']
        
        data = data.copy()
        
        ema_fast = data['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = data['close'].ewm(span=slow_period, adjust=False).mean()
        
        data['MACD'] = ema_fast - ema_slow
        data['MACD_Signal'] = data['MACD'].ewm(span=signal_period, adjust=False).mean()
        data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
        
        data['Golden_Cross'] = (
            (data['MACD'] > data['MACD_Signal']) & 
            (data['MACD'].shift(1) <= data['MACD_Signal'].shift(1))
        ).astype(int)
        
        data['Death_Cross'] = (
            (data['MACD'] < data['MACD_Signal']) & 
            (data['MACD'].shift(1) >= data['MACD_Signal'].shift(1))
        ).astype(int)
        
        for idx, row in data.iterrows():
            if pd.isna(row['MACD']) or pd.isna(row['MACD_Signal']):
                continue
            
            timestamp = idx if isinstance(idx, datetime) else datetime.now()
            
            if row['Golden_Cross'] == 1:
                signal = Signal(
                    symbol='',
                    signal_type=SignalType.BUY,
                    price=row['close'],
                    timestamp=timestamp,
                    strength=abs(row['MACD_Hist']),
                    metadata={
                        'MACD': row['MACD'],
                        'MACD_Signal': row['MACD_Signal'],
                        'MACD_Hist': row['MACD_Hist'],
                        'reason': 'macd_golden_cross'
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
                    strength=abs(row['MACD_Hist']),
                    metadata={
                        'MACD': row['MACD'],
                        'MACD_Signal': row['MACD_Signal'],
                        'MACD_Hist': row['MACD_Hist'],
                        'reason': 'macd_death_cross'
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
