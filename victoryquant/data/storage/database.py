"""
数据库管理模块 - MySQL版本
"""
import pymysql
from pymysql import cursors
from dbutils.pooled_db import PooledDB
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os


class DatabaseManager:
    def __init__(self, host: str = "localhost", port: int = 3306,
                 user: str = "root", password: str = "", 
                 database: str = "victoryquant",
                 charset: str = "utf8mb4"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        
        self._pool = None
        self._init_pool()
        self._init_tables()
    
    def _init_pool(self):
        self._pool = PooledDB(
            creator=pymysql,
            maxconnections=20,
            mincached=2,
            maxcached=5,
            maxshared=3,
            blocking=True,
            maxusage=None,
            setsession=[],
            ping=1,
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            cursorclass=cursors.DictCursor
        )
    
    def _get_connection(self):
        return self._pool.connection()
    
    def _init_tables(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_daily (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    date DATE NOT NULL,
                    open DECIMAL(10, 3),
                    high DECIMAL(10, 3),
                    low DECIMAL(10, 3),
                    close DECIMAL(10, 3),
                    volume BIGINT,
                    amount DECIMAL(20, 2),
                    change_ratio DECIMAL(10, 4),
                    turnover DECIMAL(10, 4),
                    created_at DATETIME,
                    UNIQUE KEY uk_symbol_date (symbol, date),
                    INDEX idx_date (date),
                    INDEX idx_symbol (symbol)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_info (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL UNIQUE,
                    name VARCHAR(50),
                    industry VARCHAR(50),
                    market VARCHAR(20),
                    list_date DATE,
                    updated_at DATETIME,
                    INDEX idx_symbol (symbol),
                    INDEX idx_industry (industry)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    report_date DATE NOT NULL,
                    report_type VARCHAR(20),
                    data_json TEXT,
                    created_at DATETIME,
                    UNIQUE KEY uk_symbol_report (symbol, report_date, report_type),
                    INDEX idx_symbol (symbol),
                    INDEX idx_report_date (report_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    strategy_id VARCHAR(50),
                    symbol VARCHAR(20) NOT NULL,
                    trade_date DATE NOT NULL,
                    trade_time TIME,
                    direction VARCHAR(10),
                    price DECIMAL(10, 3),
                    quantity INT,
                    amount DECIMAL(20, 2),
                    commission DECIMAL(10, 4),
                    profit DECIMAL(20, 2),
                    created_at DATETIME,
                    INDEX idx_strategy_id (strategy_id),
                    INDEX idx_symbol (symbol),
                    INDEX idx_trade_date (trade_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS strategy_performance (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    strategy_id VARCHAR(50) NOT NULL,
                    date DATE NOT NULL,
                    total_value DECIMAL(20, 2),
                    cash DECIMAL(20, 2),
                    position_value DECIMAL(20, 2),
                    daily_return DECIMAL(10, 6),
                    cumulative_return DECIMAL(10, 6),
                    max_drawdown DECIMAL(10, 6),
                    sharpe_ratio DECIMAL(10, 4),
                    created_at DATETIME,
                    UNIQUE KEY uk_strategy_date (strategy_id, date),
                    INDEX idx_strategy_id (strategy_id),
                    INDEX idx_date (date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    strategy_id VARCHAR(50),
                    symbol VARCHAR(20) NOT NULL,
                    signal_date DATE NOT NULL,
                    signal_type VARCHAR(20),
                    signal_strength DECIMAL(10, 4),
                    price DECIMAL(10, 3),
                    metadata TEXT,
                    created_at DATETIME,
                    INDEX idx_strategy_id (strategy_id),
                    INDEX idx_symbol (symbol),
                    INDEX idx_signal_date (signal_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_minute (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    datetime DATETIME NOT NULL,
                    open DECIMAL(10, 3),
                    high DECIMAL(10, 3),
                    low DECIMAL(10, 3),
                    close DECIMAL(10, 3),
                    volume BIGINT,
                    amount DECIMAL(20, 2),
                    created_at DATETIME,
                    UNIQUE KEY uk_symbol_datetime (symbol, datetime),
                    INDEX idx_symbol (symbol),
                    INDEX idx_datetime (datetime)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_weekly (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    date DATE NOT NULL,
                    open DECIMAL(10, 3),
                    high DECIMAL(10, 3),
                    low DECIMAL(10, 3),
                    close DECIMAL(10, 3),
                    volume BIGINT,
                    amount DECIMAL(20, 2),
                    created_at DATETIME,
                    UNIQUE KEY uk_symbol_date (symbol, date),
                    INDEX idx_symbol (symbol),
                    INDEX idx_date (date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_monthly (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    date DATE NOT NULL,
                    open DECIMAL(10, 3),
                    high DECIMAL(10, 3),
                    low DECIMAL(10, 3),
                    close DECIMAL(10, 3),
                    volume BIGINT,
                    amount DECIMAL(20, 2),
                    created_at DATETIME,
                    UNIQUE KEY uk_symbol_date (symbol, date),
                    INDEX idx_symbol (symbol),
                    INDEX idx_date (date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            
            conn.commit()
        finally:
            conn.close()
    
    def save_daily_data(self, data: pd.DataFrame, symbol: str):
        if data.empty:
            return
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            for idx, row in data.iterrows():
                date_str = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)
                
                sql = '''
                    INSERT INTO stock_daily 
                    (symbol, date, open, high, low, close, volume, amount, 
                     change_ratio, turnover, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    open = VALUES(open),
                    high = VALUES(high),
                    low = VALUES(low),
                    close = VALUES(close),
                    volume = VALUES(volume),
                    amount = VALUES(amount),
                    change_ratio = VALUES(change_ratio),
                    turnover = VALUES(turnover),
                    created_at = VALUES(created_at)
                '''
                
                cursor.execute(sql, (
                    symbol,
                    date_str,
                    row.get('open'),
                    row.get('high'),
                    row.get('low'),
                    row.get('close'),
                    row.get('volume'),
                    row.get('amount'),
                    row.get('change_ratio'),
                    row.get('turnover'),
                    datetime.now()
                ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_daily_data(self, symbol: str, start_date: str = None, 
                       end_date: str = None) -> pd.DataFrame:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM stock_daily WHERE symbol = %s"
            params = [symbol]
            
            if start_date:
                query += " AND date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND date <= %s"
                params.append(end_date)
            
            query += " ORDER BY date"
            
            df = pd.read_sql_query(query, conn, params=params)
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                df = df.drop(columns=['id'], errors='ignore')
            
            return df
        finally:
            conn.close()
    
    def save_stock_info(self, info: Dict):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            sql = '''
                INSERT INTO stock_info 
                (symbol, name, industry, market, list_date, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                industry = VALUES(industry),
                market = VALUES(market),
                list_date = VALUES(list_date),
                updated_at = VALUES(updated_at)
            '''
            
            cursor.execute(sql, (
                info.get('symbol'),
                info.get('name'),
                info.get('industry'),
                info.get('market'),
                info.get('list_date'),
                datetime.now()
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_stock_info(self, symbol: str) -> Dict:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stock_info WHERE symbol = %s", (symbol,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'industry': row['industry'],
                    'market': row['market'],
                    'list_date': row['list_date'],
                    'updated_at': row['updated_at']
                }
            return {}
        finally:
            conn.close()
    
    def save_financial_data(self, symbol: str, report_date: str, 
                           report_type: str, data: Dict):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            sql = '''
                INSERT INTO financial_data 
                (symbol, report_date, report_type, data_json, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                data_json = VALUES(data_json),
                created_at = VALUES(created_at)
            '''
            
            cursor.execute(sql, (
                symbol,
                report_date,
                report_type,
                json.dumps(data, ensure_ascii=False),
                datetime.now()
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_financial_data(self, symbol: str, report_type: str = None) -> List[Dict]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            if report_type:
                cursor.execute('''
                    SELECT report_date, data_json FROM financial_data 
                    WHERE symbol = %s AND report_type = %s
                    ORDER BY report_date DESC
                ''', (symbol, report_type))
            else:
                cursor.execute('''
                    SELECT report_date, report_type, data_json FROM financial_data 
                    WHERE symbol = %s
                    ORDER BY report_date DESC
                ''', (symbol,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'report_date': row['report_date'],
                    'report_type': row.get('report_type', report_type),
                    'data': json.loads(row['data_json'])
                })
            
            return results
        finally:
            conn.close()
    
    def save_trading_record(self, record: Dict):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            sql = '''
                INSERT INTO trading_records 
                (strategy_id, symbol, trade_date, trade_time, direction, 
                 price, quantity, amount, commission, profit, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            cursor.execute(sql, (
                record.get('strategy_id'),
                record.get('symbol'),
                record.get('trade_date'),
                record.get('trade_time'),
                record.get('direction'),
                record.get('price'),
                record.get('quantity'),
                record.get('amount'),
                record.get('commission'),
                record.get('profit'),
                datetime.now()
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_trading_records(self, strategy_id: str = None, symbol: str = None,
                           start_date: str = None, end_date: str = None) -> pd.DataFrame:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM trading_records WHERE 1=1"
            params = []
            
            if strategy_id:
                query += " AND strategy_id = %s"
                params.append(strategy_id)
            if symbol:
                query += " AND symbol = %s"
                params.append(symbol)
            if start_date:
                query += " AND trade_date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND trade_date <= %s"
                params.append(end_date)
            
            query += " ORDER BY trade_date, trade_time"
            
            df = pd.read_sql_query(query, conn, params=params)
            if not df.empty:
                df = df.drop(columns=['id'], errors='ignore')
            return df
        finally:
            conn.close()
    
    def save_strategy_performance(self, performance: Dict):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            sql = '''
                INSERT INTO strategy_performance 
                (strategy_id, date, total_value, cash, position_value, 
                 daily_return, cumulative_return, max_drawdown, sharpe_ratio, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                total_value = VALUES(total_value),
                cash = VALUES(cash),
                position_value = VALUES(position_value),
                daily_return = VALUES(daily_return),
                cumulative_return = VALUES(cumulative_return),
                max_drawdown = VALUES(max_drawdown),
                sharpe_ratio = VALUES(sharpe_ratio),
                created_at = VALUES(created_at)
            '''
            
            cursor.execute(sql, (
                performance.get('strategy_id'),
                performance.get('date'),
                performance.get('total_value'),
                performance.get('cash'),
                performance.get('position_value'),
                performance.get('daily_return'),
                performance.get('cumulative_return'),
                performance.get('max_drawdown'),
                performance.get('sharpe_ratio'),
                datetime.now()
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_strategy_performance(self, strategy_id: str, 
                                start_date: str = None) -> pd.DataFrame:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM strategy_performance WHERE strategy_id = %s"
            params = [strategy_id]
            
            if start_date:
                query += " AND date >= %s"
                params.append(start_date)
            
            query += " ORDER BY date"
            
            df = pd.read_sql_query(query, conn, params=params)
            if not df.empty:
                df = df.drop(columns=['id'], errors='ignore')
            return df
        finally:
            conn.close()
    
    def save_signal(self, signal: Dict):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            sql = '''
                INSERT INTO signals 
                (strategy_id, symbol, signal_date, signal_type, 
                 signal_strength, price, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            cursor.execute(sql, (
                signal.get('strategy_id'),
                signal.get('symbol'),
                signal.get('signal_date'),
                signal.get('signal_type'),
                signal.get('signal_strength'),
                signal.get('price'),
                json.dumps(signal.get('metadata', {}), ensure_ascii=False),
                datetime.now()
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_signals(self, strategy_id: str = None, symbol: str = None,
                   start_date: str = None) -> pd.DataFrame:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM signals WHERE 1=1"
            params = []
            
            if strategy_id:
                query += " AND strategy_id = %s"
                params.append(strategy_id)
            if symbol:
                query += " AND symbol = %s"
                params.append(symbol)
            if start_date:
                query += " AND signal_date >= %s"
                params.append(start_date)
            
            query += " ORDER BY signal_date"
            
            df = pd.read_sql_query(query, conn, params=params)
            if not df.empty:
                df = df.drop(columns=['id'], errors='ignore')
            return df
        finally:
            conn.close()
    
    def save_minute_data(self, data: pd.DataFrame, symbol: str):
        if data.empty:
            return
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            for idx, row in data.iterrows():
                datetime_str = idx.strftime('%Y-%m-%d %H:%M:%S') if hasattr(idx, 'strftime') else str(idx)
                
                sql = '''
                    INSERT INTO stock_minute 
                    (symbol, datetime, open, high, low, close, volume, amount, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    open = VALUES(open),
                    high = VALUES(high),
                    low = VALUES(low),
                    close = VALUES(close),
                    volume = VALUES(volume),
                    amount = VALUES(amount),
                    created_at = VALUES(created_at)
                '''
                
                cursor.execute(sql, (
                    symbol,
                    datetime_str,
                    row.get('open'),
                    row.get('high'),
                    row.get('low'),
                    row.get('close'),
                    row.get('volume'),
                    row.get('amount'),
                    datetime.now()
                ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_minute_data(self, symbol: str, start_datetime: str = None, 
                        end_datetime: str = None) -> pd.DataFrame:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM stock_minute WHERE symbol = %s"
            params = [symbol]
            
            if start_datetime:
                query += " AND datetime >= %s"
                params.append(start_datetime)
            if end_datetime:
                query += " AND datetime <= %s"
                params.append(end_datetime)
            
            query += " ORDER BY datetime"
            
            df = pd.read_sql_query(query, conn, params=params)
            
            if not df.empty:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)
                df = df.drop(columns=['id'], errors='ignore')
            
            return df
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        conn = self._get_connection()
        try:
            if params:
                return pd.read_sql_query(query, conn, params=params)
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = None):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
        finally:
            conn.close()
    
    def batch_insert(self, table: str, data: List[Dict]):
        if not data:
            return
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            columns = list(data[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            
            sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
            
            values = [tuple(d.get(col) for col in columns) for d in data]
            cursor.executemany(sql, values)
            
            conn.commit()
        finally:
            conn.close()
    
    def close_pool(self):
        if self._pool:
            self._pool.close()
