"""
文件存储模块
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import pickle
import csv


class FileStorage:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        self._ensure_dir(base_dir)
    
    def _ensure_dir(self, path: str):
        if not os.path.exists(path):
            os.makedirs(path)
    
    def _get_path(self, *args) -> str:
        path = os.path.join(self.base_dir, *args)
        self._ensure_dir(os.path.dirname(path))
        return path
    
    def save_dataframe(self, df: pd.DataFrame, filename: str, 
                      subdir: str = None, format: str = "csv"):
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        if format == "csv":
            path = path if path.endswith('.csv') else f"{path}.csv"
            df.to_csv(path, encoding='utf-8-sig')
        elif format == "parquet":
            path = path if path.endswith('.parquet') else f"{path}.parquet"
            df.to_parquet(path)
        elif format == "hdf":
            path = path if path.endswith('.h5') else f"{path}.h5"
            df.to_hdf(path, key='data', mode='w')
        elif format == "pickle":
            path = path if path.endswith('.pkl') else f"{path}.pkl"
            df.to_pickle(path)
        elif format == "excel":
            path = path if path.endswith('.xlsx') else f"{path}.xlsx"
            df.to_excel(path)
    
    def load_dataframe(self, filename: str, subdir: str = None, 
                      format: str = "csv") -> pd.DataFrame:
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        if format == "csv":
            path = path if path.endswith('.csv') else f"{path}.csv"
            return pd.read_csv(path, encoding='utf-8-sig')
        elif format == "parquet":
            path = path if path.endswith('.parquet') else f"{path}.parquet"
            return pd.read_parquet(path)
        elif format == "hdf":
            path = path if path.endswith('.h5') else f"{path}.h5"
            return pd.read_hdf(path, key='data')
        elif format == "pickle":
            path = path if path.endswith('.pkl') else f"{path}.pkl"
            return pd.read_pickle(path)
        elif format == "excel":
            path = path if path.endswith('.xlsx') else f"{path}.xlsx"
            return pd.read_excel(path)
        
        return pd.DataFrame()
    
    def save_json(self, data: Dict, filename: str, subdir: str = None):
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        path = path if path.endswith('.json') else f"{path}.json"
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def load_json(self, filename: str, subdir: str = None) -> Dict:
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        path = path if path.endswith('.json') else f"{path}.json"
        
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_pickle(self, obj: Any, filename: str, subdir: str = None):
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        path = path if path.endswith('.pkl') else f"{path}.pkl"
        
        with open(path, 'wb') as f:
            pickle.dump(obj, f)
    
    def load_pickle(self, filename: str, subdir: str = None) -> Any:
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        path = path if path.endswith('.pkl') else f"{path}.pkl"
        
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return pickle.load(f)
        return None
    
    def save_text(self, text: str, filename: str, subdir: str = None):
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    
    def load_text(self, filename: str, subdir: str = None) -> str:
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def list_files(self, subdir: str = None, pattern: str = None) -> List[str]:
        if subdir:
            path = self._get_path(subdir)
        else:
            path = self.base_dir
        
        if not os.path.exists(path):
            return []
        
        files = os.listdir(path)
        
        if pattern:
            files = [f for f in files if pattern in f]
        
        return files
    
    def delete_file(self, filename: str, subdir: str = None):
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        if os.path.exists(path):
            os.remove(path)
    
    def file_exists(self, filename: str, subdir: str = None) -> bool:
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        return os.path.exists(path)
    
    def get_file_info(self, filename: str, subdir: str = None) -> Dict:
        if subdir:
            path = self._get_path(subdir, filename)
        else:
            path = self._get_path(filename)
        
        if os.path.exists(path):
            stat = os.stat(path)
            return {
                'path': path,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat()
            }
        return {}
    
    def save_stock_data(self, symbol: str, data: pd.DataFrame, 
                       data_type: str = "daily"):
        subdir = os.path.join("stocks", symbol)
        filename = f"{data_type}.csv"
        self.save_dataframe(data, filename, subdir)
    
    def load_stock_data(self, symbol: str, data_type: str = "daily") -> pd.DataFrame:
        subdir = os.path.join("stocks", symbol)
        filename = f"{data_type}.csv"
        return self.load_dataframe(filename, subdir)
    
    def save_backtest_result(self, strategy_name: str, result: Dict):
        subdir = os.path.join("backtest", strategy_name)
        
        if 'trades' in result:
            trades_df = pd.DataFrame(result['trades'])
            self.save_dataframe(trades_df, "trades.csv", subdir)
        
        if 'performance' in result:
            perf_df = pd.DataFrame([result['performance']])
            self.save_dataframe(perf_df, "performance.csv", subdir)
        
        if 'daily_values' in result:
            daily_df = pd.DataFrame(result['daily_values'])
            self.save_dataframe(daily_df, "daily_values.csv", subdir)
        
        self.save_json(result.get('metrics', {}), "metrics.json", subdir)
    
    def load_backtest_result(self, strategy_name: str) -> Dict:
        subdir = os.path.join("backtest", strategy_name)
        
        result = {}
        
        trades_path = self._get_path(subdir, "trades.csv")
        if os.path.exists(trades_path):
            result['trades'] = self.load_dataframe("trades.csv", subdir).to_dict('records')
        
        perf_path = self._get_path(subdir, "performance.csv")
        if os.path.exists(perf_path):
            result['performance'] = self.load_dataframe("performance.csv", subdir).to_dict('records')[0]
        
        daily_path = self._get_path(subdir, "daily_values.csv")
        if os.path.exists(daily_path):
            result['daily_values'] = self.load_dataframe("daily_values.csv", subdir).to_dict('records')
        
        result['metrics'] = self.load_json("metrics.json", subdir)
        
        return result
