"""
系统配置模块
"""
from dataclasses import dataclass
from typing import Dict, List
import json
import os


@dataclass
class DatabaseConfig:
    type: str = "mysql"
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "victoryquant"
    charset: str = "utf8mb4"
    pool_size: int = 20
    pool_recycle: int = 3600


@dataclass
class TradingConfig:
    trading_start_time: str = "09:30"
    trading_end_time: str = "15:00"
    lunch_break_start: str = "11:30"
    lunch_break_end: str = "13:00"
    price_limit_ratio: float = 0.1
    st_price_limit_ratio: float = 0.05
    gem_price_limit_ratio: float = 0.2
    min_trade_unit: int = 100
    commission_rate: float = 0.0003
    stamp_duty_rate: float = 0.001
    transfer_fee_rate: float = 0.00002


@dataclass
class RiskConfig:
    max_position_ratio: float = 0.8
    max_single_stock_ratio: float = 0.2
    max_daily_loss_ratio: float = 0.05
    stop_loss_ratio: float = 0.08
    take_profit_ratio: float = 0.15


@dataclass
class DataConfig:
    data_source: str = "akshare"
    cache_enabled: bool = True
    cache_dir: str = "data/cache"
    update_interval: int = 300


@dataclass
class BacktestConfig:
    initial_capital: float = 1000000.0
    benchmark: str = "000300"
    risk_free_rate: float = 0.03


class Config:
    def __init__(self, config_file: str = None):
        self.database = DatabaseConfig()
        self.trading = TradingConfig()
        self.risk = RiskConfig()
        self.data = DataConfig()
        self.backtest = BacktestConfig()
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str):
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        if 'database' in config_data:
            for key, value in config_data['database'].items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
        
        if 'trading' in config_data:
            for key, value in config_data['trading'].items():
                if hasattr(self.trading, key):
                    setattr(self.trading, key, value)
        
        if 'risk' in config_data:
            for key, value in config_data['risk'].items():
                if hasattr(self.risk, key):
                    setattr(self.risk, key, value)
        
        if 'data' in config_data:
            for key, value in config_data['data'].items():
                if hasattr(self.data, key):
                    setattr(self.data, key, value)
        
        if 'backtest' in config_data:
            for key, value in config_data['backtest'].items():
                if hasattr(self.backtest, key):
                    setattr(self.backtest, key, value)
    
    def save_to_file(self, config_file: str):
        config_data = {
            'database': self.database.__dict__,
            'trading': self.trading.__dict__,
            'risk': self.risk.__dict__,
            'data': self.data.__dict__,
            'backtest': self.backtest.__dict__
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    
    def get_database_params(self) -> Dict:
        return {
            'host': self.database.host,
            'port': self.database.port,
            'user': self.database.user,
            'password': self.database.password,
            'database': self.database.database,
            'charset': self.database.charset
        }


default_config = Config()
