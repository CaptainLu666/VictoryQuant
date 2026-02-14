"""
RSI策略
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
from ..base.base_strategy import BaseStrategy
from ..base.signal import Signal, SignalType


class RSIStrategy(BaseStrategy):
    def __init__(self, period: int = 14, oversold: float = 30, 
                 overbought: float = 70, stop_loss: float = 0.08):
        params = {
            'period': period,
            'oversold': oversold,
            'overbought': overbought,
            'stop_loss': stop_loss
        }
        super().__init__("RSI_Strategy", params)
    
    def _validate_params(self):
        if self.params['oversold'] >= self.params['overbought']:
            raise ValueError("超卖阈值必须小于超买阈值")
    
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        signals = []
        
        if data.empty:
            return signals
        
        period = self.params['period']
        oversold = self.params['oversold']
        overbought = self.params['overbought']
        
        data = data.copy()
        
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        data['Oversold_Signal'] = (
            (data['RSI'] < oversold) & 
            (data['RSI'].shift(1) >= oversold)
        ).astype(int)
        
        data['Overbought_Signal'] = (
            (data['RSI'] > overbought) & 
            (data['RSI'].shift(1) <= overbought)
        ).astype(int)
        
        data['Rising_From_Oversold'] = (
            (data['RSI'] > oversold) & 
            (data['RSI'].shift(1) <= oversold)
        ).astype(int)
        
        data['Falling_From_Overbought'] = (
            (data['RSI'] < overbought) & 
            (data['RSI'].shift(1) >= overbought)
        ).astype(int)
        
        for idx, row in data.iterrows():
            if pd.isna(row['RSI']):
                continue
            
            timestamp = idx if isinstance(idx, datetime) else datetime.now()
            
            if row['Rising_From_Oversold'] == 1:
                signal = Signal(
                    symbol='',
                    signal_type=SignalType.BUY,
                    price=row['close'],
                    timestamp=timestamp,
                    strength=(oversold - row['RSI'].shift(1)) / oversold if not pd.isna(row['RSI'].shift(1)) else 0.5,
                    metadata={
                        'RSI': row['RSI'],
                        'reason': 'rising_from_oversold'
                    }
                )
                signals.append(signal)
                self.record_signal(signal)
            
            elif row['Falling_From_Overbought'] == 1:
                signal = Signal(
                    symbol='',
                    signal_type=SignalType.SELL,
                    price=row['close'],
                    timestamp=timestamp,
                    strength=(row['RSI'].shift(1) - overbought) / (100 - overbought) if not pd.isna(row['RSI'].shift(1)) else 0.5,
                    metadata={
                        'RSI': row['RSI'],
                        'reason': 'falling_from_overbought'
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
