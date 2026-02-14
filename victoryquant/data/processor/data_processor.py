"""
数据处理器
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime


class DataProcessor:
    def __init__(self):
        pass
    
    def normalize_data(self, data: pd.DataFrame, method: str = "minmax") -> pd.DataFrame:
        result = data.copy()
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        
        if method == "minmax":
            for col in numeric_cols:
                min_val = result[col].min()
                max_val = result[col].max()
                if max_val != min_val:
                    result[col] = (result[col] - min_val) / (max_val - min_val)
        elif method == "zscore":
            for col in numeric_cols:
                mean_val = result[col].mean()
                std_val = result[col].std()
                if std_val != 0:
                    result[col] = (result[col] - mean_val) / std_val
        
        return result
    
    def calculate_returns(self, data: pd.DataFrame, price_col: str = "close") -> pd.DataFrame:
        result = data.copy()
        result['daily_return'] = result[price_col].pct_change()
        result['log_return'] = np.log(result[price_col] / result[price_col].shift(1))
        result['cumulative_return'] = (1 + result['daily_return']).cumprod() - 1
        return result
    
    def calculate_volatility(self, data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        result = data.copy()
        result['volatility'] = result['daily_return'].rolling(window=window).std() * np.sqrt(252)
        return result
    
    def calculate_drawdown(self, data: pd.DataFrame, price_col: str = "close") -> pd.DataFrame:
        result = data.copy()
        cummax = result[price_col].cummax()
        result['drawdown'] = (result[price_col] - cummax) / cummax
        result['max_drawdown'] = result['drawdown'].cummin()
        return result
    
    def resample_data(self, data: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
        ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'amount': 'sum'
        }
        
        available_cols = [col for col in ohlc_dict.keys() if col in data.columns]
        ohlc_dict_filtered = {k: v for k, v in ohlc_dict.items() if k in available_cols}
        
        return data.resample(freq).agg(ohlc_dict_filtered)
    
    def calculate_price_change(self, data: pd.DataFrame, periods: List[int] = [1, 5, 10, 20]) -> pd.DataFrame:
        result = data.copy()
        for period in periods:
            result[f'change_{period}d'] = result['close'].pct_change(period) * 100
        return result
    
    def calculate_moving_average_ratio(self, data: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        result = data.copy()
        for period in periods:
            ma = result['close'].rolling(window=period).mean()
            result[f'price_ma{period}_ratio'] = result['close'] / ma
        return result
    
    def calculate_volume_ratio(self, data: pd.DataFrame, periods: List[int] = [5, 10, 20]) -> pd.DataFrame:
        result = data.copy()
        for period in periods:
            vol_ma = result['volume'].rolling(window=period).mean()
            result[f'volume_ma{period}_ratio'] = result['volume'] / vol_ma
        return result
    
    def calculate_turnover_rate(self, data: pd.DataFrame, shares_outstanding: float) -> pd.DataFrame:
        result = data.copy()
        result['turnover_rate'] = result['volume'] / shares_outstanding * 100
        return result
    
    def calculate_amplitude(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        result['amplitude'] = (result['high'] - result['low']) / result['close'].shift(1) * 100
        return result
    
    def calculate_price_position(self, data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        result = data.copy()
        rolling_max = result['high'].rolling(window=window).max()
        rolling_min = result['low'].rolling(window=window).min()
        result['price_position'] = (result['close'] - rolling_min) / (rolling_max - rolling_min)
        return result
    
    def calculate_strength(self, data: pd.DataFrame, window: int = 10) -> pd.DataFrame:
        result = data.copy()
        result['up_days'] = (result['close'] > result['close'].shift(1)).rolling(window=window).sum()
        result['strength'] = result['up_days'] / window
        return result
    
    def calculate_gap(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        result['gap'] = (result['open'] - result['close'].shift(1)) / result['close'].shift(1) * 100
        result['gap_up'] = (result['gap'] > 0).astype(int)
        result['gap_down'] = (result['gap'] < 0).astype(int)
        return result
    
    def calculate_limit_status(self, data: pd.DataFrame, limit_ratio: float = 0.1) -> pd.DataFrame:
        result = data.copy()
        result['limit_up'] = (result['change_ratio'] >= limit_ratio * 100 - 0.1).astype(int)
        result['limit_down'] = (result['change_ratio'] <= -limit_ratio * 100 + 0.1).astype(int)
        return result
    
    def merge_data(self, price_data: pd.DataFrame, fundamental_data: pd.DataFrame, 
                   how: str = "left") -> pd.DataFrame:
        return pd.merge(price_data, fundamental_data, left_index=True, right_index=True, how=how)
    
    def align_data(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        common_index = None
        for name, df in data_dict.items():
            if common_index is None:
                common_index = df.index
            else:
                common_index = common_index.intersection(df.index)
        
        aligned_data = {}
        for name, df in data_dict.items():
            aligned_data[name] = df.loc[common_index]
        
        return aligned_data
    
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        
        result = self.calculate_returns(result)
        result = self.calculate_volatility(result)
        result = self.calculate_drawdown(result)
        result = self.calculate_price_change(result)
        result = self.calculate_moving_average_ratio(result)
        result = self.calculate_volume_ratio(result)
        result = self.calculate_amplitude(result)
        result = self.calculate_price_position(result)
        result = self.calculate_strength(result)
        result = self.calculate_gap(result)
        
        return result
