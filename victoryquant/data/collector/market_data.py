"""
行情数据采集模块
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time


class MarketDataCollector:
    def __init__(self, data_source: str = "akshare"):
        self.data_source = data_source
        self._cache = {}
    
    def get_realtime_quote(self, symbol: str) -> Dict:
        try:
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == symbol]
            if stock_data.empty:
                return {}
            
            return {
                'symbol': symbol,
                'name': stock_data['名称'].values[0],
                'open': float(stock_data['今开'].values[0]),
                'high': float(stock_data['最高'].values[0]),
                'low': float(stock_data['最低'].values[0]),
                'close': float(stock_data['最新价'].values[0]),
                'volume': float(stock_data['成交量'].values[0]),
                'amount': float(stock_data['成交额'].values[0]),
                'change_ratio': float(stock_data['涨跌幅'].values[0]),
                'change_amount': float(stock_data['涨跌额'].values[0]),
                'turnover_rate': float(stock_data['换手率'].values[0]) if '换手率' in stock_data.columns else 0,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"获取实时行情失败: {e}")
            return {}
    
    def get_history_kline(self, symbol: str, start_date: str, end_date: str, 
                          period: str = "daily", adjust: str = "qfq") -> pd.DataFrame:
        try:
            import akshare as ak
            
            cache_key = f"{symbol}_{start_date}_{end_date}_{period}_{adjust}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            if period == "daily":
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                        start_date=start_date, end_date=end_date, 
                                        adjust=adjust)
            elif period == "weekly":
                df = ak.stock_zh_a_hist(symbol=symbol, period="weekly", 
                                        start_date=start_date, end_date=end_date, 
                                        adjust=adjust)
            elif period == "monthly":
                df = ak.stock_zh_a_hist(symbol=symbol, period="monthly", 
                                        start_date=start_date, end_date=end_date, 
                                        adjust=adjust)
            else:
                df = pd.DataFrame()
            
            if not df.empty:
                df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 
                              'amplitude', 'change_ratio', 'change_amount', 'turnover']
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                self._cache[cache_key] = df
            
            return df
        except Exception as e:
            print(f"获取历史K线数据失败: {e}")
            return pd.DataFrame()
    
    def get_minute_kline(self, symbol: str, period: str = "1") -> pd.DataFrame:
        try:
            import akshare as ak
            
            if period == "1":
                df = ak.stock_zh_a_minute(symbol=symbol, period="1", adjust="qfq")
            elif period == "5":
                df = ak.stock_zh_a_minute(symbol=symbol, period="5", adjust="qfq")
            elif period == "15":
                df = ak.stock_zh_a_minute(symbol=symbol, period="15", adjust="qfq")
            elif period == "30":
                df = ak.stock_zh_a_minute(symbol=symbol, period="30", adjust="qfq")
            elif period == "60":
                df = ak.stock_zh_a_minute(symbol=symbol, period="60", adjust="qfq")
            else:
                df = pd.DataFrame()
            
            if not df.empty:
                df.columns = ['datetime', 'open', 'close', 'high', 'low', 'volume', 'amount']
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)
            
            return df
        except Exception as e:
            print(f"获取分钟K线数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_list(self) -> pd.DataFrame:
        try:
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            return df[['代码', '名称', '最新价', '涨跌幅', '总市值', '流通市值']]
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_index_data(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        try:
            import akshare as ak
            df = ak.stock_zh_index_daily(symbol=f"sh{index_code}")
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            return df
        except Exception as e:
            print(f"获取指数数据失败: {e}")
            return pd.DataFrame()
    
    def get_trading_dates(self, start_date: str, end_date: str) -> List[str]:
        try:
            import akshare as ak
            df = ak.tool_trade_date_hist_sina()
            dates = df[(df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)]
            return dates['trade_date'].tolist()
        except Exception as e:
            print(f"获取交易日历失败: {e}")
            return []
    
    def is_trading_time(self, dt: datetime = None) -> bool:
        if dt is None:
            dt = datetime.now()
        
        if dt.weekday() >= 5:
            return False
        
        time_val = dt.time()
        morning_start = datetime.strptime("09:30", "%H:%M").time()
        morning_end = datetime.strptime("11:30", "%H:%M").time()
        afternoon_start = datetime.strptime("13:00", "%H:%M").time()
        afternoon_end = datetime.strptime("15:00", "%H:%M").time()
        
        return (morning_start <= time_val <= morning_end) or \
               (afternoon_start <= time_val <= afternoon_end)
    
    def clear_cache(self):
        self._cache.clear()
