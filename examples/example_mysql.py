"""
MySQL数据库使用示例
演示如何使用MySQL数据库存储和管理量化交易数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from victoryquant.data.storage import DatabaseManager
from victoryquant.config import Config


def example_database_connection():
    print("\n" + "="*50)
    print("MySQL数据库连接示例")
    print("="*50)
    
    config = Config("victoryquant/config/database_config.json")
    
    db_params = config.get_database_params()
    print(f"\n数据库连接参数:")
    print(f"  主机: {db_params['host']}")
    print(f"  端口: {db_params['port']}")
    print(f"  用户: {db_params['user']}")
    print(f"  数据库: {db_params['database']}")
    
    db = DatabaseManager(**db_params)
    print("\n数据库连接成功！")
    
    return db


def example_save_stock_data(db: DatabaseManager):
    print("\n" + "="*50)
    print("保存股票数据示例")
    print("="*50)
    
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
    np.random.seed(42)
    
    close_prices = 10 + np.cumsum(np.random.randn(len(dates)) * 0.02)
    high_prices = close_prices * (1 + np.abs(np.random.randn(len(dates)) * 0.01))
    low_prices = close_prices * (1 - np.abs(np.random.randn(len(dates)) * 0.01))
    open_prices = close_prices + np.random.randn(len(dates)) * 0.1
    volumes = np.random.randint(1000000, 5000000, len(dates))
    amounts = volumes * close_prices
    
    data = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes,
        'amount': amounts,
        'change_ratio': np.random.randn(len(dates)) * 2,
        'turnover': np.random.rand(len(dates)) * 5
    }, index=dates)
    
    symbol = "TEST001"
    
    print(f"\n保存股票 {symbol} 的日K线数据...")
    print(f"数据行数: {len(data)}")
    
    db.save_daily_data(data, symbol)
    print("数据保存成功！")


def example_query_stock_data(db: DatabaseManager):
    print("\n" + "="*50)
    print("查询股票数据示例")
    print("="*50)
    
    symbol = "TEST001"
    
    print(f"\n查询股票 {symbol} 的数据...")
    data = db.get_daily_data(symbol, start_date='2023-06-01', end_date='2023-06-30')
    
    if not data.empty:
        print(f"查询到 {len(data)} 条数据")
        print("\n数据预览:")
        print(data.head())
    else:
        print("未查询到数据")


def example_save_stock_info(db: DatabaseManager):
    print("\n" + "="*50)
    print("保存股票信息示例")
    print("="*50)
    
    stock_info = {
        'symbol': 'TEST001',
        'name': '测试股票',
        'industry': '计算机',
        'market': '主板',
        'list_date': '2020-01-01'
    }
    
    print(f"\n保存股票信息: {stock_info}")
    db.save_stock_info(stock_info)
    print("股票信息保存成功！")
    
    print("\n查询股票信息...")
    info = db.get_stock_info('TEST001')
    print(f"查询结果: {info}")


def example_save_trading_record(db: DatabaseManager):
    print("\n" + "="*50)
    print("保存交易记录示例")
    print("="*50)
    
    record = {
        'strategy_id': 'MA_Strategy',
        'symbol': 'TEST001',
        'trade_date': '2023-06-15',
        'trade_time': '09:35:00',
        'direction': 'BUY',
        'price': 10.5,
        'quantity': 1000,
        'amount': 10500,
        'commission': 5.25,
        'profit': 0
    }
    
    print(f"\n保存交易记录: {record}")
    db.save_trading_record(record)
    print("交易记录保存成功！")
    
    print("\n查询交易记录...")
    records = db.get_trading_records(strategy_id='MA_Strategy')
    if not records.empty:
        print(f"查询到 {len(records)} 条交易记录")
        print(records)


def example_save_strategy_performance(db: DatabaseManager):
    print("\n" + "="*50)
    print("保存策略绩效示例")
    print("="*50)
    
    performance = {
        'strategy_id': 'MA_Strategy',
        'date': '2023-06-15',
        'total_value': 1000000,
        'cash': 500000,
        'position_value': 500000,
        'daily_return': 0.015,
        'cumulative_return': 0.08,
        'max_drawdown': -0.05,
        'sharpe_ratio': 1.5
    }
    
    print(f"\n保存策略绩效: {performance}")
    db.save_strategy_performance(performance)
    print("策略绩效保存成功！")
    
    print("\n查询策略绩效...")
    perf_data = db.get_strategy_performance('MA_Strategy')
    if not perf_data.empty:
        print(f"查询到 {len(perf_data)} 条绩效记录")
        print(perf_data)


def example_save_signal(db: DatabaseManager):
    print("\n" + "="*50)
    print("保存交易信号示例")
    print("="*50)
    
    signal = {
        'strategy_id': 'MA_Strategy',
        'symbol': 'TEST001',
        'signal_date': '2023-06-15',
        'signal_type': 'BUY',
        'signal_strength': 0.8,
        'price': 10.5,
        'metadata': {
            'reason': 'golden_cross',
            'ma_fast': 10.2,
            'ma_slow': 10.0
        }
    }
    
    print(f"\n保存交易信号: {signal}")
    db.save_signal(signal)
    print("交易信号保存成功！")
    
    print("\n查询交易信号...")
    signals = db.get_signals(strategy_id='MA_Strategy')
    if not signals.empty:
        print(f"查询到 {len(signals)} 条信号记录")
        print(signals)


def example_custom_query(db: DatabaseManager):
    print("\n" + "="*50)
    print("自定义查询示例")
    print("="*50)
    
    query = "SELECT symbol, COUNT(*) as count FROM stock_daily GROUP BY symbol"
    print(f"\n执行查询: {query}")
    
    result = db.execute_query(query)
    print("\n查询结果:")
    print(result)


def main():
    print("="*50)
    print("VictoryQuant MySQL数据库使用示例")
    print("="*50)
    
    try:
        db = example_database_connection()
        
        example_save_stock_data(db)
        example_query_stock_data(db)
        example_save_stock_info(db)
        example_save_trading_record(db)
        example_save_strategy_performance(db)
        example_save_signal(db)
        example_custom_query(db)
        
        db.close_pool()
        
        print("\n" + "="*50)
        print("示例运行完成")
        print("="*50)
        
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n请确保:")
        print("1. MySQL服务已启动")
        print("2. 数据库 'victoryquant' 已创建")
        print("3. 配置文件中的连接参数正确")
        print("4. 已安装所需依赖: pip install pymysql DBUtils")


if __name__ == "__main__":
    main()
