"""
绩效分析器
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class PerformanceAnalyzer:
    def __init__(self, risk_free_rate: float = 0.03):
        self.risk_free_rate = risk_free_rate
    
    def analyze(self, daily_values: pd.DataFrame, initial_capital: float) -> Dict:
        if daily_values.empty:
            return {}
        
        df = daily_values.copy()
        
        if 'total_value' not in df.columns:
            return {}
        
        df['daily_return'] = df['total_value'].pct_change()
        df['cumulative_return'] = (df['total_value'] / initial_capital) - 1
        
        metrics = {
            'total_return': self._calculate_total_return(df, initial_capital),
            'annualized_return': self._calculate_annualized_return(df),
            'volatility': self._calculate_volatility(df),
            'sharpe_ratio': self._calculate_sharpe_ratio(df),
            'max_drawdown': self._calculate_max_drawdown(df),
            'win_rate': 0,
            'profit_factor': 0,
            'avg_profit': 0,
            'avg_loss': 0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
            'trading_days': len(df),
            'start_date': df.index[0].strftime('%Y-%m-%d') if len(df) > 0 else '',
            'end_date': df.index[-1].strftime('%Y-%m-%d') if len(df) > 0 else ''
        }
        
        return metrics
    
    def _calculate_total_return(self, df: pd.DataFrame, initial_capital: float) -> float:
        if df.empty:
            return 0.0
        
        final_value = df['total_value'].iloc[-1]
        return (final_value - initial_capital) / initial_capital
    
    def _calculate_annualized_return(self, df: pd.DataFrame) -> float:
        if df.empty or len(df) < 2:
            return 0.0
        
        total_return = df['cumulative_return'].iloc[-1]
        trading_days = len(df)
        years = trading_days / 252
        
        if years <= 0:
            return 0.0
        
        return (1 + total_return) ** (1 / years) - 1
    
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        if df.empty or 'daily_return' not in df.columns:
            return 0.0
        
        return df['daily_return'].std() * np.sqrt(252)
    
    def _calculate_sharpe_ratio(self, df: pd.DataFrame) -> float:
        if df.empty or 'daily_return' not in df.columns:
            return 0.0
        
        annualized_return = self._calculate_annualized_return(df)
        volatility = self._calculate_volatility(df)
        
        if volatility == 0:
            return 0.0
        
        return (annualized_return - self.risk_free_rate) / volatility
    
    def _calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0
        
        cummax = df['total_value'].cummax()
        drawdown = (df['total_value'] - cummax) / cummax
        
        return drawdown.min()
    
    def analyze_trades(self, trades: List[Dict]) -> Dict:
        if not trades:
            return {}
        
        sell_trades = [t for t in trades if t.get('direction') == 'SELL']
        
        if not sell_trades:
            return {}
        
        profits = [t.get('profit', 0) for t in sell_trades]
        
        winning_trades = [p for p in profits if p > 0]
        losing_trades = [p for p in profits if p < 0]
        
        total_profit = sum(winning_trades) if winning_trades else 0
        total_loss = abs(sum(losing_trades)) if losing_trades else 0
        
        win_rate = len(winning_trades) / len(profits) if profits else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        avg_profit = np.mean(winning_trades) if winning_trades else 0
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        
        return {
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'total_trades': len(sell_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'total_profit': total_profit,
            'total_loss': total_loss
        }
    
    def calculate_sortino_ratio(self, df: pd.DataFrame) -> float:
        if df.empty or 'daily_return' not in df.columns:
            return 0.0
        
        annualized_return = self._calculate_annualized_return(df)
        
        negative_returns = df['daily_return'][df['daily_return'] < 0]
        
        if negative_returns.empty:
            return float('inf')
        
        downside_std = negative_returns.std() * np.sqrt(252)
        
        if downside_std == 0:
            return 0.0
        
        return (annualized_return - self.risk_free_rate) / downside_std
    
    def calculate_calmar_ratio(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0
        
        annualized_return = self._calculate_annualized_return(df)
        max_drawdown = abs(self._calculate_max_drawdown(df))
        
        if max_drawdown == 0:
            return float('inf')
        
        return annualized_return / max_drawdown
    
    def calculate_var(self, df: pd.DataFrame, confidence: float = 0.95) -> float:
        if df.empty or 'daily_return' not in df.columns:
            return 0.0
        
        returns = df['daily_return'].dropna()
        
        if returns.empty:
            return 0.0
        
        return np.percentile(returns, (1 - confidence) * 100)
    
    def calculate_cvar(self, df: pd.DataFrame, confidence: float = 0.95) -> float:
        if df.empty or 'daily_return' not in df.columns:
            return 0.0
        
        returns = df['daily_return'].dropna()
        
        if returns.empty:
            return 0.0
        
        var = self.calculate_var(df, confidence)
        
        return returns[returns <= var].mean()
    
    def calculate_beta(self, df: pd.DataFrame, benchmark_returns: pd.Series) -> float:
        if df.empty or 'daily_return' not in df.columns:
            return 0.0
        
        returns = df['daily_return'].dropna()
        benchmark = benchmark_returns.dropna()
        
        common_index = returns.index.intersection(benchmark.index)
        
        if len(common_index) < 2:
            return 0.0
        
        returns = returns.loc[common_index]
        benchmark = benchmark.loc[common_index]
        
        covariance = returns.cov(benchmark)
        variance = benchmark.var()
        
        if variance == 0:
            return 0.0
        
        return covariance / variance
    
    def calculate_alpha(self, df: pd.DataFrame, benchmark_returns: pd.Series) -> float:
        if df.empty:
            return 0.0
        
        beta = self.calculate_beta(df, benchmark_returns)
        annualized_return = self._calculate_annualized_return(df)
        
        if benchmark_returns.empty:
            return 0.0
        
        benchmark_annualized = (1 + benchmark_returns.mean()) ** 252 - 1
        
        return annualized_return - (self.risk_free_rate + beta * (benchmark_annualized - self.risk_free_rate))
    
    def calculate_information_ratio(self, df: pd.DataFrame, benchmark_returns: pd.Series) -> float:
        if df.empty or 'daily_return' not in df.columns:
            return 0.0
        
        returns = df['daily_return'].dropna()
        benchmark = benchmark_returns.dropna()
        
        common_index = returns.index.intersection(benchmark.index)
        
        if len(common_index) < 2:
            return 0.0
        
        returns = returns.loc[common_index]
        benchmark = benchmark.loc[common_index]
        
        excess_returns = returns - benchmark
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        if tracking_error == 0:
            return 0.0
        
        annualized_excess = (1 + excess_returns.mean()) ** 252 - 1
        
        return annualized_excess / tracking_error
    
    def generate_report(self, daily_values: pd.DataFrame, 
                       trades: List[Dict] = None,
                       initial_capital: float = 1000000.0) -> Dict:
        performance = self.analyze(daily_values, initial_capital)
        
        if trades:
            trade_analysis = self.analyze_trades(trades)
            performance.update(trade_analysis)
        
        sortino = self.calculate_sortino_ratio(daily_values)
        calmar = self.calculate_calmar_ratio(daily_values)
        var_95 = self.calculate_var(daily_values, 0.95)
        cvar_95 = self.calculate_cvar(daily_values, 0.95)
        
        performance.update({
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'var_95': var_95,
            'cvar_95': cvar_95
        })
        
        return performance
