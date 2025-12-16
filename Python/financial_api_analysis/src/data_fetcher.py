import yfinance as yf
import pandas as pd
import requests
import json
from datetime import datetime
import time
from pathlib import Path
import logging
from config import settings

logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
logger = logging.getLogger(__name__)

class EquityDataFetcher:
    def __init__(self):
        self.symbols = settings.YFINANCE_SYMBOLS
        self.start_date = settings.ANALYSIS_START_DATE
        self.end_date = settings.ANALYSIS_END_DATE
        self.raw_data_path = settings.DATA_RAW
        
    def fetch_symbol_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(start=self.start_date, end=self.end_date)
            
            if hist_data.empty:
                logger.warning(f"No data retrieved for {symbol}")
                return None
            
            # Convert datetime index to string for JSON serialization
            hist_data.index = hist_data.index.strftime('%Y-%m-%d')
            
            metadata = {
                'symbol': symbol,
                'company_name': ticker.info.get('longName', ''),
                'sector': ticker.info.get('sector', ''),
                'market_cap': ticker.info.get('marketCap', 0),
                'currency': ticker.info.get('currency', 'USD')
            }
            
            data_dict = {
                'metadata': metadata,
                'historical_data': hist_data.reset_index().to_dict('records'),
                'dates_list': hist_data.index.tolist(),  # Store dates separately
                'columns_list': hist_data.columns.tolist()
            }
            
            filename = self.raw_data_path / f"equity_{symbol}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(data_dict, f, default=str)
            
            logger.info(f"Successfully fetched {len(hist_data)} records for {symbol}")
            return filename
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def fetch_all_symbols(self):
        results = {}
        for symbol in self.symbols:
            file_path = self.fetch_symbol_data(symbol)
            if file_path:
                results[symbol] = file_path
            time.sleep(0.5)
        return results

class FREDDataFetcher:
    def __init__(self):
        self.series = settings.FRED_SERIES
        self.raw_data_path = settings.DATA_RAW
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        
    def fetch_series_data(self, series_id):
        try:
            # FRED requires API key - using mock data for free version
            return self._generate_mock_fred_data(series_id)
                
        except Exception as e:
            logger.error(f"Error in FRED fetch for {series_id}: {str(e)}")
            return self._generate_mock_fred_data(series_id)
    
    def _generate_mock_fred_data(self, series_id):
        # Fix: Use 'ME' instead of deprecated 'M'
        dates = pd.date_range(start=settings.ANALYSIS_START_DATE, end=settings.ANALYSIS_END_DATE, freq='ME')
        
        if series_id == 'DGS10':
            values = [round(3.5 + (i * 0.1) + (0.1 * (i % 3)), 2) for i in range(len(dates))]
        elif series_id == 'UNRATE':
            values = [round(3.5 + (0.1 * (i % 5)), 1) for i in range(len(dates))]
        else:  # CPIAUCSL
            values = [round(300 + (i * 0.5), 2) for i in range(len(dates))]
        
        mock_data = {
            'observations': [
                {'date': date.strftime('%Y-%m-%d'), 'value': str(val)}
                for date, val in zip(dates, values)
            ],
            'series_info': {
                'id': series_id,
                'title': self.series.get(series_id, 'Unknown Series'),
                'frequency': 'Monthly'
            }
        }
        
        filename = self.raw_data_path / f"fred_{series_id}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(mock_data, f)
        
        logger.info(f"Generated data for FRED series {series_id}")
        return filename
    
    def fetch_all_series(self):
        results = {}
        for series_id in self.series.keys():
            file_path = self.fetch_series_data(series_id)
            if file_path:
                results[series_id] = file_path
            time.sleep(0.3)
        return results