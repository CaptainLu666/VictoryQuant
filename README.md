# VictoryQuant - A股量化交易系统

得胜量化 - 一个基于Python3的A股量化交易系统

## 项目简介

VictoryQuant是一个完整的A股量化交易系统，提供数据采集、策略研发、回测评估、交易执行和风险管理等功能。

## 环境要求

- **Python版本**: >=3.8, <3.12（推荐使用 Python 3.10）
- **操作系统**: Windows / macOS / Linux
- **数据库**: MySQL 5.7+ 或 MySQL 8.0+

## 核心功能

### 1. 数据采集模块
- **行情数据**: 实时行情、历史K线数据（日/周/月/分钟）
- **基本面数据**: 财务报表、财务指标、公司信息
- **技术指标**: MA、MACD、KDJ、RSI、BOLL等常用指标

### 2. 数据处理模块
- **数据清洗**: 缺失值处理、异常值检测、数据验证
- **数据转换**: 标准化、收益率计算、波动率计算
- **数据存储**: MySQL数据库、文件存储（CSV/Parquet/HDF5）

### 3. 策略模块
- **基础策略类**: 提供策略开发框架
- **示例策略**: MA策略、MACD策略、RSI策略
- **信号生成**: 支持买入、卖出、持仓信号

### 4. 回测模块
- **回测引擎**: 事件驱动回测、支持多股票回测
- **绩效分析**: 收益率、夏普比率、最大回撤等指标
- **风险指标**: Sortino比率、Calmar比率、VaR、CVaR

### 5. 交易执行模块
- **订单管理**: 创建、提交、成交、取消订单
- **券商接口**: 模拟交易接口、可扩展实盘接口
- **订单类型**: 市价单、限价单、止损单

### 6. 风险管理模块
- **风险控制**: 仓位限制、止损止盈、最大回撤控制
- **仓位管理**: 持仓跟踪、仓位调整、资金管理

## 项目结构

```
VictoryQuant/
├── victoryquant/              # 核心代码
│   ├── data/                  # 数据模块
│   │   ├── collector/         # 数据采集
│   │   ├── processor/         # 数据处理
│   │   └── storage/           # 数据存储
│   ├── strategy/              # 策略模块
│   │   ├── base/              # 基础策略类
│   │   └── examples/          # 示例策略
│   ├── backtest/              # 回测模块
│   ├── trading/               # 交易模块
│   │   ├── order/             # 订单管理
│   │   └── broker/            # 券商接口
│   ├── risk/                  # 风险管理
│   ├── utils/                 # 工具类
│   └── config/                # 配置文件
├── examples/                  # 使用示例
├── logs/                      # 日志文件
├── data/                      # 数据文件
└── requirements.txt           # 依赖包
```

## 安装说明

### 1. 环境准备

#### 1.1 检查Python版本
```bash
python --version
# 要求: Python >=3.8, <3.12 (推荐 Python 3.10)
```

#### 1.2 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或者安装项目（开发模式）
pip install -e .
```

### 3. 配置MySQL数据库

#### 3.1 安装MySQL
- Windows: 下载 [MySQL Installer](https://dev.mysql.com/downloads/installer/)
- macOS: `brew install mysql`
- Linux: `sudo apt install mysql-server`

#### 3.2 启动MySQL服务
```bash
# Windows:
net start mysql

# macOS:
brew services start mysql

# Linux:
sudo systemctl start mysql
```

#### 3.3 创建数据库
```sql
-- 登录MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE victoryquant DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'victoryquant'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON victoryquant.* TO 'victoryquant'@'localhost';
FLUSH PRIVILEGES;
```

#### 3.4 配置数据库连接
编辑 `victoryquant/config/database_config.json` 文件：
```json
{
    "database": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "your_password",
        "database": "victoryquant"
    }
}
```

### 4. 运行示例

#### 4.1 快速启动（推荐）
```bash
# 运行交互式启动脚本
python run.py
```

#### 4.2 运行基础示例
```bash
python examples/example_usage.py
```

#### 4.3 运行MySQL示例
```bash
python examples/example_mysql.py
```

### 5. 快速测试

```python
# 测试数据采集
from victoryquant.data.collector import MarketDataCollector

collector = MarketDataCollector()
stock_list = collector.get_stock_list()
print(f"获取到 {len(stock_list)} 只股票")
```

## 快速开始

### 1. 数据库连接

```python
from victoryquant.data.storage import DatabaseManager
from victoryquant.config import Config

# 加载配置
config = Config("victoryquant/config/database_config.json")

# 连接数据库
db = DatabaseManager(**config.get_database_params())
```

### 2. 数据采集

```python
from victoryquant.data.collector import MarketDataCollector

collector = MarketDataCollector()

# 获取历史K线数据
kline_data = collector.get_history_kline(
    symbol="000001",
    start_date="20230101",
    end_date="20231231"
)

# 获取实时行情
quote = collector.get_realtime_quote("000001")
```

### 3. 策略开发

```python
from victoryquant.strategy.base import BaseStrategy
from victoryquant.strategy.base.signal import Signal, SignalType

class MyStrategy(BaseStrategy):
    def generate_signals(self, data):
        signals = []
        # 策略逻辑
        return signals
```

### 4. 回测

```python
from victoryquant.backtest import BacktestEngine
from victoryquant.strategy.examples import MAStrategy

strategy = MAStrategy(fast_period=5, slow_period=20)
engine = BacktestEngine(initial_capital=1000000)

result = engine.run_backtest(strategy, data, symbol='000001')
```

### 5. 风险管理

```python
from victoryquant.risk import RiskManager

risk_manager = RiskManager(
    max_position_ratio=0.8,
    max_single_stock_ratio=0.2,
    stop_loss_ratio=0.08
)
```

## A股交易规则

- **交易时间**: 9:30-11:30, 13:00-15:00
- **涨跌幅限制**: 主板±10%，科创板/创业板±20%
- **交易制度**: T+1
- **交易单位**: 100股/手
- **费用**: 佣金（万分之三）、印花税（千分之一）、过户费

## 注意事项

1. 本系统仅供学习和研究使用
2. 实盘交易需要对接券商API
3. 投资有风险，入市需谨慎

## 许可证

MIT License
