import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import logging
from config import settings

logger = logging.getLogger(__name__)

class FinancialDataProcessor:
    def __init__(self):
        self.raw_path = settings.DATA_RAW
        self.processed_path = settings.DATA_PROCESSED
        self.master_path = settings.PROJECT_ROOT / "data" / "master_dataset.csv"
        
    def load_equity_data(self):
        equity_files = list(self.raw_path.glob("equity_*.json"))
        all_equity_data = []
        
        for file_path in equity_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                symbol = data['metadata']['symbol']
                df = pd.DataFrame(data['historical_data'])
                
                if not df.empty:
                    # Fix: Convert 'Date' column to datetime with UTC
                    df['Date'] = pd.to_datetime(df['Date'], utc=True)
                    df = df.rename(columns={'Date': 'date'})
                    df['symbol'] = symbol
                    df['company_name'] = data['metadata']['company_name']
                    df['sector'] = data['metadata']['sector']
                    
                    all_equity_data.append(df)
                    
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
                continue
        
        if all_equity_data:
            combined_df = pd.concat(all_equity_data, ignore_index=True)
            combined_df.to_parquet(self.processed_path / "equity_data.parquet")
            return combined_df
        return pd.DataFrame()
    
    def load_fred_data(self):
        fred_files = list(self.raw_path.glob("fred_*.json"))
        all_fred_data = []
        
        for file_path in fred_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if 'observations' in data:
                    series_id = data.get('series_info', {}).get('id', 
                               file_path.stem.split('_')[1])
                    
                    df = pd.DataFrame(data['observations'])
                    df['date'] = pd.to_datetime(df['date'])
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
                    df['series_id'] = series_id
                    df['series_name'] = settings.FRED_SERIES.get(series_id, 'Unknown')
                    
                    all_fred_data.append(df)
                    
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
                continue
        
        if all_fred_data:
            combined_df = pd.concat(all_fred_data, ignore_index=True)
            combined_df.to_parquet(self.processed_path / "fred_data.parquet")
            return combined_df
        return pd.DataFrame()
    
    def calculate_technical_indicators(self, df):
        df = df.sort_values(['symbol', 'date'])
        
        df['returns'] = df.groupby('symbol')['Close'].pct_change()
        df['daily_range'] = (df['High'] - df['Low']) / df['Close'] * 100
        df['volume_ratio'] = df['Volume'] / df.groupby('symbol')['Volume'].transform('mean')
        
        df['ma_20'] = df.groupby('symbol')['Close'].transform(
            lambda x: x.rolling(window=settings.MOVING_AVERAGE_WINDOW, min_periods=1).mean()
        )
        df['ma_50'] = df.groupby('symbol')['Close'].transform(
            lambda x: x.rolling(window=50, min_periods=1).mean()
        )
        
        df['volatility'] = df.groupby('symbol')['returns'].transform(
            lambda x: x.rolling(window=20, min_periods=1).std() * np.sqrt(252)
        )
        
        return df
    
    def merge_datasets(self, equity_df, fred_df):
        if equity_df.empty:
            logger.error("No equity data to merge")
            return pd.DataFrame()
        
        # Fix: Ensure 'date' column is datetime before using .dt accessor
        equity_df['date'] = pd.to_datetime(equity_df['date'])
        equity_df['date_only'] = equity_df['date'].dt.date
        
        fred_df['date'] = pd.to_datetime(fred_df['date'])
        fred_df['date_only'] = fred_df['date'].dt.date
        
        merged_data = []
        
        for symbol in equity_df['symbol'].unique():
            symbol_df = equity_df[equity_df['symbol'] == symbol].copy()
            
            for _, fred_row in fred_df.iterrows():
                temp_df = symbol_df.copy()
                temp_df['series_id'] = fred_row['series_id']
                temp_df['series_value'] = fred_row['value']
                temp_df['series_name'] = fred_row['series_name']
                
                merged_data.append(temp_df)
        
        if merged_data:
            final_df = pd.concat(merged_data, ignore_index=True)
            final_df = final_df.drop(columns=['date_only'])
            
            column_order = [
                'date', 'symbol', 'Open', 'High', 'Low', 'Close', 'Volume',
                'Dividends', 'Stock Splits', 'ma_20', 'ma_50', 'returns',
                'daily_range', 'volatility', 'volume_ratio', 'company_name',
                'sector', 'series_id', 'series_value', 'series_name'
            ]
            
            existing_columns = [col for col in column_order if col in final_df.columns]
            final_df = final_df[existing_columns]
            
            final_df.to_csv(self.master_path, index=False)
            final_df.to_parquet(self.processed_path / "merged_financial_data.parquet")
            
            logger.info(f"Master dataset created with {len(final_df)} rows")
            return final_df
        
        return pd.DataFrame()
    
    def generate_summary_statistics(self, df):
        if df.empty:
            return {}
        
        summary = {
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d'),
                'end': df['date'].max().strftime('%Y-%m-%d')
            },
            'symbols_analyzed': df['symbol'].unique().tolist(),
            'total_observations': len(df),
            'equity_metrics': {}
        }
        
        for symbol in df['symbol'].unique():
            symbol_data = df[df['symbol'] == symbol]
            
            if not symbol_data.empty:
                latest = symbol_data.iloc[-1]
                summary['equity_metrics'][symbol] = {
                    'latest_close': round(float(latest['Close']), 2),
                    'avg_daily_volume': int(symbol_data['Volume'].mean()),
                    'total_return': round(float(symbol_data['returns'].sum() * 100), 2),
                    'avg_volatility': round(float(symbol_data['volatility'].mean() * 100), 2),
                    'sector': latest.get('sector', 'Unknown')
                }
        
        return summary
    
    def process_all_data(self):
        logger.info("Starting data processing pipeline")
        
        equity_df = self.load_equity_data()
        fred_df = self.load_fred_data()
        
        if not equity_df.empty:
            equity_df = self.calculate_technical_indicators(equity_df)
        
        master_df = self.merge_datasets(equity_df, fred_df)
        summary_stats = self.generate_summary_statistics(master_df)
        
        logger.info("Data processing completed")
        return master_df, summary_stats