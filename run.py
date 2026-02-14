"""
VictoryQuant 快速启动脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from victoryquant.data.collector import MarketDataCollector
from victoryquant.data.collector import TechnicalIndicatorCalculator
from victoryquant.strategy.examples import MAStrategy, MACDStrategy
from victoryquant.backtest import BacktestEngine
from victoryquant.utils import setup_logger

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def quick_test():
    print("="*60)
    print("VictoryQuant 快速测试")
    print("="*60)
    
    logger = setup_logger("VictoryQuant")
    logger.info("开始快速测试...")
    
    print("\n[1/4] 测试数据采集模块...")
    try:
        collector = MarketDataCollector()
        stock_list = collector.get_stock_list()
        print(f"  ✓ 获取到 {len(stock_list)} 只股票")
    except Exception as e:
        print(f"  ✗ 数据采集失败: {e}")
        print("  提示: 请确保已安装 akshare 库")
        return False
    
    print("\n[2/4] 测试技术指标计算...")
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
    
    indicator_calc = TechnicalIndicatorCalculator()
    data_with_indicators = indicator_calc.calculate_ma(data)
    data_with_indicators = indicator_calc.calculate_macd(data_with_indicators)
    print(f"  ✓ 计算了 {len(data_with_indicators.columns)} 个技术指标")
    
    print("\n[3/4] 测试策略模块...")
    strategy = MAStrategy(fast_period=5, slow_period=20)
    signals = strategy.generate_signal_for_symbol('TEST', data)
    print(f"  ✓ MA策略生成了 {len(signals)} 个信号")
    
    print("\n[4/4] 测试回测模块...")
    engine = BacktestEngine(initial_capital=1000000)
    result = engine.run_backtest(strategy, data, symbol='TEST')
    
    if 'error' not in result:
        print(f"  ✓ 回测完成")
        print(f"    - 初始资金: {result['initial_capital']:,.2f}")
        print(f"    - 最终价值: {result['final_value']:,.2f}")
        print(f"    - 总收益率: {result['performance']['total_return']*100:.2f}%")
        print(f"    - 最大回撤: {result['performance']['max_drawdown']*100:.2f}%")
        print(f"    - 交易次数: {len(result['trades'])}")
    else:
        print(f"  ✗ 回测失败: {result['error']}")
    
    print("\n" + "="*60)
    print("快速测试完成！")
    print("="*60)
    
    return True


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              VictoryQuant 量化交易系统                    ║
║                                                          ║
║  版本: 1.0.0                                             ║
║  Python: >=3.8, <3.12                                    ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    while True:
        print("\n请选择操作:")
        print("  1. 快速测试（测试所有模块）")
        print("  2. 数据采集示例")
        print("  3. 策略回测示例")
        print("  4. MySQL数据库示例")
        print("  5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == '1':
            quick_test()
        elif choice == '2':
            print("\n运行数据采集示例...")
            os.system("python examples/example_usage.py")
        elif choice == '3':
            print("\n运行策略回测示例...")
            os.system("python examples/example_usage.py")
        elif choice == '4':
            print("\n运行MySQL示例...")
            os.system("python examples/example_mysql.py")
        elif choice == '5':
            print("\n感谢使用 VictoryQuant！")
            break
        else:
            print("\n无效选项，请重新选择")


if __name__ == "__main__":
    main()
