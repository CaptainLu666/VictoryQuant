"""
数据清洗模块
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime


class DataCleaner:
    def __init__(self):
        pass
    
    def remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        return data[~data.index.duplicated(keep='first')]
    
    def handle_missing_values(self, data: pd.DataFrame, method: str = "ffill") -> pd.DataFrame:
        result = data.copy()
        
        if method == "ffill":
            result = result.fillna(method='ffill')
        elif method == "bfill":
            result = result.fillna(method='bfill')
        elif method == "interpolate":
            result = result.interpolate()
        elif method == "drop":
            result = result.dropna()
        elif method == "mean":
            result = result.fillna(result.mean())
        elif method == "median":
            result = result.fillna(result.median())
        elif method == "zero":
            result = result.fillna(0)
        
        return result
    
    def remove_outliers(self, data: pd.DataFrame, method: str = "iqr", 
                        threshold: float = 3.0) -> pd.DataFrame:
        result = data.copy()
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        
        if method == "iqr":
            for col in numeric_cols:
                Q1 = result[col].quantile(0.25)
                Q3 = result[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                result = result[(result[col] >= lower_bound) & (result[col] <= upper_bound)]
        elif method == "zscore":
            for col in numeric_cols:
                z_scores = np.abs((result[col] - result[col].mean()) / result[col].std())
                result = result[z_scores < threshold]
        
        return result
    
    def winsorize(self, data: pd.DataFrame, limits: tuple = (0.01, 0.01)) -> pd.DataFrame:
        result = data.copy()
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            lower_limit = result[col].quantile(limits[0])
            upper_limit = result[col].quantile(1 - limits[1])
            result[col] = result[col].clip(lower=lower_limit, upper=upper_limit)
        
        return result
    
    def validate_price_data(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        
        invalid_mask = (
            (result['high'] < result['low']) |
            (result['high'] < result['open']) |
            (result['high'] < result['close']) |
            (result['low'] > result['open']) |
            (result['low'] > result['close']) |
            (result['volume'] < 0)
        )
        
        result = result[~invalid_mask]
        
        return result
    
    def validate_timestamp(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        
        if not isinstance(result.index, pd.DatetimeIndex):
            try:
                result.index = pd.to_datetime(result.index)
            except:
                pass
        
        result = result.sort_index()
        
        return result
    
    def remove_non_trading_days(self, data: pd.DataFrame, trading_days: List[str]) -> pd.DataFrame:
        result = data.copy()
        
        if isinstance(result.index, pd.DatetimeIndex):
            result = result[result.index.normalize().isin(pd.to_datetime(trading_days))]
        
        return result
    
    def clean_stock_data(self, data: pd.DataFrame, trading_days: List[str] = None) -> pd.DataFrame:
        result = data.copy()
        
        result = self.remove_duplicates(result)
        result = self.validate_timestamp(result)
        result = self.validate_price_data(result)
        result = self.handle_missing_values(result, method="ffill")
        
        if trading_days:
            result = self.remove_non_trading_days(result, trading_days)
        
        return result
    
    def detect_anomalies(self, data: pd.DataFrame, window: int = 20, 
                        threshold: float = 3.0) -> pd.DataFrame:
        result = data.copy()
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            rolling_mean = result[col].rolling(window=window).mean()
            rolling_std = result[col].rolling(window=window).std()
            
            z_score = np.abs((result[col] - rolling_mean) / rolling_std)
            result[f'{col}_anomaly'] = (z_score > threshold).astype(int)
        
        return result
    
    def detect_price_jumps(self, data: pd.DataFrame, threshold: float = 0.1) -> pd.DataFrame:
        result = data.copy()
        
        returns = result['close'].pct_change()
        result['price_jump'] = (np.abs(returns) > threshold).astype(int)
        result['jump_direction'] = np.where(returns > threshold, 1, 
                                           np.where(returns < -threshold, -1, 0))
        
        return result
    
    def detect_volume_spikes(self, data: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
        result = data.copy()
        
        vol_mean = result['volume'].rolling(window=20).mean()
        vol_std = result['volume'].rolling(window=20).std()
        
        result['volume_spike'] = ((result['volume'] - vol_mean) / vol_std > threshold).astype(int)
        
        return result
    
    def fill_trading_gaps(self, data: pd.DataFrame, trading_days: List[str]) -> pd.DataFrame:
        result = data.copy()
        
        if not isinstance(result.index, pd.DatetimeIndex):
            return result
        
        all_dates = pd.DatetimeIndex(trading_days)
        missing_dates = all_dates.difference(result.index)
        
        if len(missing_dates) > 0:
            for date in missing_dates:
                prev_date = result.index[result.index < date]
                if len(prev_date) > 0:
                    prev_data = result.loc[prev_date[-1]].copy()
                    prev_data.name = date
                    prev_data['volume'] = 0
                    prev_data['amount'] = 0
                    result = pd.concat([result, prev_data.to_frame().T])
            
            result = result.sort_index()
        
        return result
    
    def clean_and_validate(self, data: pd.DataFrame, trading_days: List[str] = None,
                          outlier_method: str = "iqr") -> pd.DataFrame:
        result = data.copy()
        
        result = self.clean_stock_data(result, trading_days)
        result = self.remove_outliers(result, method=outlier_method)
        result = self.winsorize(result)
        
        return result
