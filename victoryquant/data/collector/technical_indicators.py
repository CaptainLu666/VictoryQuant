"""
技术指标计算模块
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class TechnicalIndicatorCalculator:
    def __init__(self):
        pass
    
    def calculate_ma(self, data: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        result = data.copy()
        for period in periods:
            result[f'MA{period}'] = result['close'].rolling(window=period).mean()
        return result
    
    def calculate_ema(self, data: pd.DataFrame, periods: List[int] = [12, 26]) -> pd.DataFrame:
        result = data.copy()
        for period in periods:
            result[f'EMA{period}'] = result['close'].ewm(span=period, adjust=False).mean()
        return result
    
    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, 
                       signal: int = 9) -> pd.DataFrame:
        result = data.copy()
        ema_fast = result['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = result['close'].ewm(span=slow, adjust=False).mean()
        
        result['MACD'] = ema_fast - ema_slow
        result['MACD_Signal'] = result['MACD'].ewm(span=signal, adjust=False).mean()
        result['MACD_Hist'] = result['MACD'] - result['MACD_Signal']
        
        return result
    
    def calculate_kdj(self, data: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        result = data.copy()
        
        low_n = result['low'].rolling(window=n).min()
        high_n = result['high'].rolling(window=n).max()
        
        rsv = (result['close'] - low_n) / (high_n - low_n) * 100
        rsv = rsv.fillna(50)
        
        result['K'] = rsv.ewm(alpha=1/m1, adjust=False).mean()
        result['D'] = result['K'].ewm(alpha=1/m2, adjust=False).mean()
        result['J'] = 3 * result['K'] - 2 * result['D']
        
        return result
    
    def calculate_rsi(self, data: pd.DataFrame, periods: List[int] = [6, 12, 24]) -> pd.DataFrame:
        result = data.copy()
        
        delta = result['close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        for period in periods:
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            rs = avg_gain / avg_loss
            result[f'RSI{period}'] = 100 - (100 / (1 + rs))
        
        return result
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, 
                                   std_dev: float = 2.0) -> pd.DataFrame:
        result = data.copy()
        
        result['BOLL_MID'] = result['close'].rolling(window=period).mean()
        result['BOLL_STD'] = result['close'].rolling(window=period).std()
        result['BOLL_UPPER'] = result['BOLL_MID'] + std_dev * result['BOLL_STD']
        result['BOLL_LOWER'] = result['BOLL_MID'] - std_dev * result['BOLL_STD']
        result['BOLL_WIDTH'] = (result['BOLL_UPPER'] - result['BOLL_LOWER']) / result['BOLL_MID']
        
        return result
    
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        result = data.copy()
        
        high_low = result['high'] - result['low']
        high_close = np.abs(result['high'] - result['close'].shift())
        low_close = np.abs(result['low'] - result['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        result['ATR'] = tr.rolling(window=period).mean()
        
        return result
    
    def calculate_obv(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        
        direction = np.where(result['close'] > result['close'].shift(), 1,
                            np.where(result['close'] < result['close'].shift(), -1, 0))
        result['OBV'] = (direction * result['volume']).cumsum()
        
        return result
    
    def calculate_cci(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        result = data.copy()
        
        tp = (result['high'] + result['low'] + result['close']) / 3
        ma_tp = tp.rolling(window=period).mean()
        md = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        result['CCI'] = (tp - ma_tp) / (0.015 * md)
        
        return result
    
    def calculate_williams_r(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        result = data.copy()
        
        high_n = result['high'].rolling(window=period).max()
        low_n = result['low'].rolling(window=period).min()
        
        result['WILLR'] = (high_n - result['close']) / (high_n - low_n) * -100
        
        return result
    
    def calculate_momentum(self, data: pd.DataFrame, period: int = 10) -> pd.DataFrame:
        result = data.copy()
        result['MOM'] = result['close'] - result['close'].shift(period)
        result['MOM_PCT'] = result['close'].pct_change(period) * 100
        
        return result
    
    def calculate_roc(self, data: pd.DataFrame, period: int = 12) -> pd.DataFrame:
        result = data.copy()
        result['ROC'] = ((result['close'] - result['close'].shift(period)) / 
                        result['close'].shift(period)) * 100
        
        return result
    
    def calculate_adx(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        result = data.copy()
        
        high_diff = result['high'].diff()
        low_diff = -result['low'].diff()
        
        plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
        minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)
        
        high_low = result['high'] - result['low']
        high_close = np.abs(result['high'] - result['close'].shift())
        low_close = np.abs(result['low'] - result['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean() / atr
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        result['ADX'] = dx.rolling(window=period).mean()
        result['PLUS_DI'] = plus_di
        result['MINUS_DI'] = minus_di
        
        return result
    
    def calculate_volume_ma(self, data: pd.DataFrame, periods: List[int] = [5, 10, 20]) -> pd.DataFrame:
        result = data.copy()
        for period in periods:
            result[f'VOL_MA{period}'] = result['volume'].rolling(window=period).mean()
        return result
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        
        result = self.calculate_ma(result)
        result = self.calculate_ema(result)
        result = self.calculate_macd(result)
        result = self.calculate_kdj(result)
        result = self.calculate_rsi(result)
        result = self.calculate_bollinger_bands(result)
        result = self.calculate_atr(result)
        result = self.calculate_obv(result)
        result = self.calculate_cci(result)
        result = self.calculate_williams_r(result)
        result = self.calculate_momentum(result)
        result = self.calculate_roc(result)
        result = self.calculate_adx(result)
        result = self.calculate_volume_ma(result)
        
        return result
    
    def detect_golden_cross(self, data: pd.DataFrame, fast_period: int = 5, 
                           slow_period: int = 10) -> pd.DataFrame:
        result = data.copy()
        fast_ma = result[f'MA{fast_period}']
        slow_ma = result[f'MA{slow_period}']
        
        result['GOLDEN_CROSS'] = ((fast_ma > slow_ma) & 
                                  (fast_ma.shift(1) <= slow_ma.shift(1))).astype(int)
        result['DEATH_CROSS'] = ((fast_ma < slow_ma) & 
                                 (fast_ma.shift(1) >= slow_ma.shift(1))).astype(int)
        
        return result
    
    def detect_macd_signal(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        
        result['MACD_GOLDEN_CROSS'] = ((result['MACD'] > result['MACD_Signal']) & 
                                       (result['MACD'].shift(1) <= result['MACD_Signal'].shift(1))).astype(int)
        result['MACD_DEATH_CROSS'] = ((result['MACD'] < result['MACD_Signal']) & 
                                      (result['MACD'].shift(1) >= result['MACD_Signal'].shift(1))).astype(int)
        
        return result
