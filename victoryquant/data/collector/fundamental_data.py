"""
基本面数据采集模块
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime


class FundamentalDataCollector:
    def __init__(self, data_source: str = "akshare"):
        self.data_source = data_source
    
    def get_financial_report(self, symbol: str, report_type: str = "balance") -> pd.DataFrame:
        try:
            import akshare as ak
            
            if report_type == "balance":
                df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
            elif report_type == "income":
                df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
            elif report_type == "cashflow":
                df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
            else:
                df = pd.DataFrame()
            
            return df
        except Exception as e:
            print(f"获取财务报表失败: {e}")
            return pd.DataFrame()
    
    def get_financial_indicator(self, symbol: str) -> pd.DataFrame:
        try:
            import akshare as ak
            df = ak.stock_financial_analysis_indicator(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取财务指标失败: {e}")
            return pd.DataFrame()
    
    def get_stock_info(self, symbol: str) -> Dict:
        try:
            import akshare as ak
            df = ak.stock_individual_info_em(symbol=symbol)
            
            info = {}
            for _, row in df.iterrows():
                info[row['item']] = row['value']
            
            return info
        except Exception as e:
            print(f"获取股票信息失败: {e}")
            return {}
    
    def get_industry_classification(self, symbol: str) -> str:
        try:
            import akshare as ak
            df = ak.stock_individual_info_em(symbol=symbol)
            industry = df[df['item'] == '行业']['value'].values
            return industry[0] if len(industry) > 0 else ""
        except Exception as e:
            print(f"获取行业分类失败: {e}")
            return ""
    
    def get_pe_ratio(self, symbol: str) -> Dict:
        try:
            import akshare as ak
            df = ak.stock_a_lg_indicator(symbol=symbol)
            
            if not df.empty:
                latest = df.iloc[-1]
                return {
                    'pe_ttm': float(latest['pe_ttm']) if pd.notna(latest['pe_ttm']) else 0,
                    'pe_lyr': float(latest['pe_lyr']) if pd.notna(latest['pe_lyr']) else 0,
                    'pb': float(latest['pb']) if pd.notna(latest['pb']) else 0,
                    'ps_ttm': float(latest['ps_ttm']) if pd.notna(latest['ps_ttm']) else 0,
                    'dv_ratio': float(latest['dv_ratio']) if pd.notna(latest['dv_ratio']) else 0,
                    'total_mv': float(latest['total_mv']) if pd.notna(latest['total_mv']) else 0,
                    'circ_mv': float(latest['circ_mv']) if pd.notna(latest['circ_mv']) else 0,
                }
            return {}
        except Exception as e:
            print(f"获取估值指标失败: {e}")
            return {}
    
    def get_dividend_history(self, symbol: str) -> pd.DataFrame:
        try:
            import akshare as ak
            df = ak.stock_dividend_cninfo(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取分红历史失败: {e}")
            return pd.DataFrame()
    
    def get_ipo_info(self, symbol: str) -> Dict:
        try:
            import akshare as ak
            df = ak.stock_ipo_info()
            stock_info = df[df['stock_code'] == symbol]
            
            if not stock_info.empty:
                return {
                    'ipo_date': stock_info['ipo_date'].values[0],
                    'issue_price': float(stock_info['issue_price'].values[0]),
                    'issue_amount': float(stock_info['issue_amount'].values[0]),
                    'market_cap': float(stock_info['market_cap'].values[0]),
                }
            return {}
        except Exception as e:
            print(f"获取IPO信息失败: {e}")
            return {}
    
    def get_company_announcements(self, symbol: str) -> pd.DataFrame:
        try:
            import akshare as ak
            df = ak.stock_notice_report(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取公司公告失败: {e}")
            return pd.DataFrame()
    
    def get_holder_structure(self, symbol: str) -> pd.DataFrame:
        try:
            import akshare as ak
            df = ak.stock_gdfx_holding_teamwork(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取股东结构失败: {e}")
            return pd.DataFrame()
    
    def get_main_business(self, symbol: str) -> pd.DataFrame:
        try:
            import akshare as ak
            df = ak.stock_zygc_em(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取主营业务失败: {e}")
            return pd.DataFrame()
    
    def get_financial_summary(self, symbol: str) -> Dict:
        try:
            info = self.get_stock_info(symbol)
            pe_data = self.get_pe_ratio(symbol)
            financial_ind = self.get_financial_indicator(symbol)
            
            summary = {
                'symbol': symbol,
                'name': info.get('股票简称', ''),
                'industry': info.get('行业', ''),
                'pe_ttm': pe_data.get('pe_ttm', 0),
                'pb': pe_data.get('pb', 0),
                'market_cap': pe_data.get('total_mv', 0),
                'circulating_market_cap': pe_data.get('circ_mv', 0),
            }
            
            if not financial_ind.empty:
                latest = financial_ind.iloc[-1]
                summary.update({
                    'roe': float(latest['净资产收益率']) if pd.notna(latest.get('净资产收益率')) else 0,
                    'net_profit_margin': float(latest['销售净利率']) if pd.notna(latest.get('销售净利率')) else 0,
                    'gross_profit_margin': float(latest['销售毛利率']) if pd.notna(latest.get('销售毛利率')) else 0,
                    'debt_ratio': float(latest['资产负债率']) if pd.notna(latest.get('资产负债率')) else 0,
                })
            
            return summary
        except Exception as e:
            print(f"获取财务摘要失败: {e}")
            return {'symbol': symbol}
