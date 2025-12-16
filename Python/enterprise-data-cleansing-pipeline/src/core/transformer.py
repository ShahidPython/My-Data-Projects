import pandas as pd
import numpy as np
from datetime import datetime
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules
        self.cleaning_stats = {}
        
    def clean_transaction_id(self, df: pd.DataFrame) -> pd.DataFrame:
        df['transaction_id'] = pd.to_numeric(df['transaction_id'], errors='coerce')
        invalid = df['transaction_id'].isna().sum()
        self.cleaning_stats['invalid_transaction_ids'] = int(invalid)
        return df
    
    def clean_customer_id(self, df: pd.DataFrame) -> pd.DataFrame:
        pattern = r'^CUST-\d+$'
        mask = df['customer_id'].astype(str).str.match(pattern, na=False)
        df.loc[~mask, 'customer_id'] = np.nan
        self.cleaning_stats['invalid_customer_ids'] = int((~mask).sum())
        return df
    
    def clean_amount(self, df: pd.DataFrame) -> pd.DataFrame:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df['amount'] = df['amount'].abs()
        
        q99 = df['amount'].quantile(0.99)
        df.loc[df['amount'] > q99, 'amount'] = q99
        self.cleaning_stats['amount_outliers_capped'] = int((df['amount'] > q99).sum())
        
        return df
    
    def clean_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        date_formats = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M', '%m-%d-%Y %H:%M', '%Y/%m/%d %H:%M']
        
        for fmt in date_formats:
            try:
                parsed = pd.to_datetime(df['transaction_date'], format=fmt, errors='coerce')
                if parsed.notna().any():
                    df['transaction_date'] = parsed
                    break
            except:
                continue
        
        invalid_dates = df['transaction_date'].isna().sum()
        self.cleaning_stats['invalid_dates'] = int(invalid_dates)
        return df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        initial_count = len(df)
        df = df.drop_duplicates(subset=['transaction_id'], keep='last')
        duplicates_removed = initial_count - len(df)
        self.cleaning_stats['duplicates_removed'] = duplicates_removed
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting data transformation")
        
        df = self.clean_transaction_id(df)
        df = self.clean_customer_id(df)
        df = self.clean_amount(df)
        df = self.clean_dates(df)
        df = self.remove_duplicates(df)
        
        df = df.dropna(subset=['transaction_id', 'amount'])
        self.cleaning_stats['rows_final'] = len(df)
        
        logger.info(f"Transformation complete. Stats: {self.cleaning_stats}")
        return df