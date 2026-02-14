"""
日期工具
"""
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd


class DateUtils:
    @staticmethod
    def get_trading_dates(start_date: str, end_date: str) -> List[str]:
        try:
            import akshare as ak
            df = ak.tool_trade_date_hist_sina()
            dates = df[(df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)]
            return dates['trade_date'].tolist()
        except Exception:
            return DateUtils._generate_weekdays(start_date, end_date)
    
    @staticmethod
    def _generate_weekdays(start_date: str, end_date: str) -> List[str]:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        weekdays = []
        current = start
        while current <= end:
            if current.weekday() < 5:
                weekdays.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return weekdays
    
    @staticmethod
    def is_trading_day(date: str) -> bool:
        try:
            import akshare as ak
            df = ak.tool_trade_date_hist_sina()
            return date in df['trade_date'].values
        except Exception:
            dt = datetime.strptime(date, '%Y-%m-%d')
            return dt.weekday() < 5
    
    @staticmethod
    def is_trading_time(dt: datetime = None) -> bool:
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
    
    @staticmethod
    def get_next_trading_day(date: str) -> str:
        dt = datetime.strptime(date, '%Y-%m-%d')
        
        while True:
            dt += timedelta(days=1)
            if DateUtils.is_trading_day(dt.strftime('%Y-%m-%d')):
                return dt.strftime('%Y-%m-%d')
    
    @staticmethod
    def get_previous_trading_day(date: str) -> str:
        dt = datetime.strptime(date, '%Y-%m-%d')
        
        while True:
            dt -= timedelta(days=1)
            if DateUtils.is_trading_day(dt.strftime('%Y-%m-%d')):
                return dt.strftime('%Y-%m-%d')
    
    @staticmethod
    def get_trading_days_between(start_date: str, end_date: str) -> int:
        trading_dates = DateUtils.get_trading_dates(start_date, end_date)
        return len(trading_dates)
    
    @staticmethod
    def date_to_str(date: datetime, fmt: str = '%Y-%m-%d') -> str:
        return date.strftime(fmt)
    
    @staticmethod
    def str_to_date(date_str: str, fmt: str = '%Y-%m-%d') -> datetime:
        return datetime.strptime(date_str, fmt)
    
    @staticmethod
    def get_quarter(date: str) -> int:
        dt = datetime.strptime(date, '%Y-%m-%d')
        return (dt.month - 1) // 3 + 1
    
    @staticmethod
    def get_year(date: str) -> int:
        dt = datetime.strptime(date, '%Y-%m-%d')
        return dt.year
    
    @staticmethod
    def get_month(date: str) -> int:
        dt = datetime.strptime(date, '%Y-%m-%d')
        return dt.month
    
    @staticmethod
    def get_week_of_year(date: str) -> int:
        dt = datetime.strptime(date, '%Y-%m-%d')
        return dt.isocalendar()[1]
    
    @staticmethod
    def is_month_end(date: str) -> bool:
        dt = datetime.strptime(date, '%Y-%m-%d')
        next_day = dt + timedelta(days=1)
        return next_day.month != dt.month
    
    @staticmethod
    def is_quarter_end(date: str) -> bool:
        dt = datetime.strptime(date, '%Y-%m-%d')
        return dt.month in [3, 6, 9, 12] and DateUtils.is_month_end(date)
    
    @staticmethod
    def is_year_end(date: str) -> bool:
        dt = datetime.strptime(date, '%Y-%m-%d')
        return dt.month == 12 and DateUtils.is_month_end(date)
