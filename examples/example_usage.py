"""
VictoryQuant 使用示例
演示如何使用量化交易系统的各个模块
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from victoryquant.data.collector import MarketDataCollector, FundamentalDataCollector, TechnicalIndicatorCalculator
from victoryquant.data.processor import DataProcessor, DataCleaner
from victoryquant.data.storage import DatabaseManager, FileStorage
from victoryquant.strategy.examples import MAStrategy, MACDStrategy, RSIStrategy
from victoryquant.backtest import BacktestEngine, PerformanceAnalyzer
from victoryquant.trading.order import OrderManager, Order, OrderType, OrderDirection
from victoryquant.trading.broker import SimulatedBroker
from victoryquant.risk import RiskManager, PositionManager
from victoryquant.utils import setup_logger, DateUtils


def example_data_collection():
    print("\n" + "="*50)
    print("数据采集示例")
    print("="*50)
    
    collector = MarketDataCollector()
    
    print("\n1. 获取股票列表...")
    stock_list = collector.get_stock_list()
    print(f"获取到 {len(stock_list)} 只股票")
    
    if not stock_list.empty:
        print("\n前5只股票:")
        print(stock_list.head())
    
    print("\n2. 获取历史K线数据...")
    symbol = "000001"
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    try:
        kline_data = collector.get_history_kline(symbol, start_date, end_date)
        if not kline_data.empty:
            print(f"获取到 {len(kline_data)} 条K线数据")
            print("\n最近5天数据:")
            print(kline_data.tail())
    except Exception as e:
        print(f"获取K线数据失败: {e}")
    
    print("\n3. 计算技术指标...")
    if not kline_data.empty:
        indicator_calc = TechnicalIndicatorCalculator()
        
        kline_with_indicators = indicator_calc.calculate_ma(kline_data)
        kline_with_indicators = indicator_calc.calculate_macd(kline_with_indicators)
        kline_with_indicators = indicator_calc.calculate_kdj(kline_with_indicators)
        
        print("\n带技术指标的数据:")
        print(kline_with_indicators[['close', 'MA5', 'MA10', 'MA20', 'MACD', 'K', 'D']].tail())


def example_strategy():
    print("\n" + "="*50)
    print("策略示例")
    print("="*50)
    
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
    np.random.seed(42)
    
    close_prices = 10 + np.cumsum(np.random.randn(len(dates)) * 0.02)
    high_prices = close_prices * (1 + np.abs(np.random.randn(len(dates)) * 0.01))
    low_prices = close_prices * (1 - np.abs(np.random.randn(len(dates)) * 0.01))
    open_prices = close_prices + np.random.randn(len(dates)) * 0.1
    volumes = np.random.randint(1000000, 5000000, len(dates))
    
    data = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    print("\n模拟数据:")
    print(data.head())
    
    print("\n1. MA策略信号...")
    ma_strategy = MAStrategy(fast_period=5, slow_period=20)
    signals = ma_strategy.generate_signal_for_symbol('TEST', data)
    print(f"生成 {len(signals)} 个信号")
    for signal in signals[:5]:
        print(f"  {signal}")
    
    print("\n2. MACD策略信号...")
    macd_strategy = MACDStrategy()
    signals = macd_strategy.generate_signal_for_symbol('TEST', data)
    print(f"生成 {len(signals)} 个信号")
    
    print("\n3. RSI策略信号...")
    rsi_strategy = RSIStrategy()
    signals = rsi_strategy.generate_signal_for_symbol('TEST', data)
    print(f"生成 {len(signals)} 个信号")


def example_backtest():
    print("\n" + "="*50)
    print("回测示例")
    print("="*50)
    
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
    np.random.seed(42)
    
    close_prices = 10 + np.cumsum(np.random.randn(len(dates)) * 0.02)
    high_prices = close_prices * (1 + np.abs(np.random.randn(len(dates)) * 0.01))
    low_prices = close_prices * (1 - np.abs(np.random.randn(len(dates)) * 0.01))
    open_prices = close_prices + np.random.randn(len(dates)) * 0.1
    volumes = np.random.randint(1000000, 5000000, len(dates))
    
    data = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    strategy = MAStrategy(fast_period=5, slow_period=20)
    
    engine = BacktestEngine(
        initial_capital=1000000.0,
        commission_rate=0.0003,
        stamp_duty_rate=0.001,
        slippage=0.001
    )
    
    print("\n运行回测...")
    result = engine.run_backtest(strategy, data, symbol='TEST')
    
    if 'error' in result:
        print(f"回测失败: {result['error']}")
        return
    
    print("\n回测结果:")
    print(f"  初始资金: {result['initial_capital']:,.2f}")
    print(f"  最终价值: {result['final_value']:,.2f}")
    print(f"  总收益率: {result['performance']['total_return']*100:.2f}%")
    print(f"  年化收益率: {result['performance']['annualized_return']*100:.2f}%")
    print(f"  最大回撤: {result['performance']['max_drawdown']*100:.2f}%")
    print(f"  夏普比率: {result['performance']['sharpe_ratio']:.2f}")
    print(f"  交易次数: {len(result['trades'])}")
    
    if result['trades']:
        print("\n前5笔交易:")
        for trade in result['trades'][:5]:
            print(f"  {trade['date'].strftime('%Y-%m-%d')} {trade['direction']} "
                  f"{trade['quantity']}股 @ {trade['price']:.2f}")


def example_risk_management():
    print("\n" + "="*50)
    print("风险管理示例")
    print("="*50)
    
    risk_manager = RiskManager(
        max_position_ratio=0.8,
        max_single_stock_ratio=0.2,
        max_daily_loss_ratio=0.05,
        max_drawdown_ratio=0.15
    )
    
    risk_manager.initialize(1000000.0)
    
    print("\n1. 检查仓位限制...")
    position_value = 700000.0
    total_value = 1000000.0
    is_valid = risk_manager.check_position_limit(position_value, total_value)
    print(f"仓位比例: {position_value/total_value*100:.1f}%, 是否合规: {is_valid}")
    
    print("\n2. 检查单只股票限制...")
    stock_value = 150000.0
    is_valid = risk_manager.check_single_stock_limit(stock_value, total_value)
    print(f"单只股票比例: {stock_value/total_value*100:.1f}%, 是否合规: {is_valid}")
    
    print("\n3. 检查止损...")
    avg_cost = 10.0
    current_price = 9.0
    triggered = risk_manager.check_stop_loss(avg_cost, current_price)
    print(f"成本: {avg_cost}, 当前价格: {current_price}, 触发止损: {triggered}")
    
    print("\n4. 获取风险报告...")
    positions = {
        'TEST': {
            'quantity': 10000,
            'avg_cost': 10.0,
            'current_price': 10.5
        }
    }
    
    report = risk_manager.get_risk_report(total_value, position_value, positions)
    print(f"风险等级: {report['risk_level']}")
    print(f"仓位比例: {report['position_ratio']*100:.1f}%")
    print(f"警告信息: {report['warnings']}")
    
    print("\n5. 仓位管理...")
    position_manager = PositionManager(initial_capital=1000000.0)
    
    position_manager.update_position('TEST', 10000, 10.0, is_buy=True)
    print(f"买入后现金: {position_manager.cash:,.2f}")
    
    position_manager.update_current_prices({'TEST': 10.5})
    
    summary = position_manager.get_position_summary()
    print(f"\n持仓摘要:")
    print(f"  总价值: {summary['total_value']:,.2f}")
    print(f"  现金: {summary['cash']:,.2f}")
    print(f"  持仓市值: {summary['position_value']:,.2f}")
    print(f"  持仓数量: {summary['position_count']}")


def example_order_management():
    print("\n" + "="*50)
    print("订单管理示例")
    print("="*50)
    
    order_manager = OrderManager()
    
    print("\n1. 创建订单...")
    market_order = order_manager.create_market_order(
        symbol='TEST',
        direction=OrderDirection.BUY,
        quantity=1000,
        strategy_id='MA_Strategy'
    )
    print(f"创建市价单: {market_order}")
    
    limit_order = order_manager.create_limit_order(
        symbol='TEST',
        direction=OrderDirection.SELL,
        quantity=1000,
        price=10.5,
        strategy_id='MA_Strategy'
    )
    print(f"创建限价单: {limit_order}")
    
    print("\n2. 提交订单...")
    order_manager.submit_order(market_order.order_id)
    print(f"订单状态: {market_order.status.value}")
    
    print("\n3. 成交订单...")
    order_manager.fill_order(
        market_order.order_id,
        filled_quantity=1000,
        filled_price=10.2,
        commission=5.0
    )
    print(f"订单状态: {market_order.status.value}")
    print(f"成交数量: {market_order.filled_quantity}")
    print(f"成交价格: {market_order.filled_price}")
    
    print("\n4. 订单统计...")
    stats = order_manager.get_order_statistics()
    print(f"订单统计: {stats}")


def main():
    print("="*50)
    print("VictoryQuant 量化交易系统示例")
    print("="*50)
    
    logger = setup_logger("VictoryQuant", "logs/example.log")
    logger.info("开始运行示例...")
    
    try:
        example_data_collection()
    except Exception as e:
        print(f"数据采集示例失败: {e}")
    
    example_strategy()
    example_backtest()
    example_risk_management()
    example_order_management()
    
    print("\n" + "="*50)
    print("示例运行完成")
    print("="*50)


if __name__ == "__main__":
    main()
