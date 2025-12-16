import pytest
import pandas as pd
import numpy as np
from src.core.transformer import DataTransformer

class TestDataTransformer:
    def setup_method(self):
        self.rules = {
            "missing_values": {"threshold": 0.3},
            "outlier_detection": {"threshold": 3.5}
        }
        self.transformer = DataTransformer(self.rules)
    
    def test_clean_transaction_id(self):
        df = pd.DataFrame({
            'transaction_id': ['1001', '1002', 'invalid', None]
        })
        result = self.transformer.clean_transaction_id(df)
        assert result['transaction_id'].iloc[0] == 1001.0
        assert result['transaction_id'].iloc[1] == 1002.0
        assert pd.isna(result['transaction_id'].iloc[2])
        assert pd.isna(result['transaction_id'].iloc[3])
        assert self.transformer.cleaning_stats['invalid_transaction_ids'] == 2
    
    def test_clean_customer_id(self):
        df = pd.DataFrame({
            'customer_id': ['CUST-1001', 'INVALID', None, 'CUST-1002']
        })
        result = self.transformer.clean_customer_id(df)
        assert result['customer_id'].iloc[0] == 'CUST-1001'
        assert pd.isna(result['customer_id'].iloc[1])
        assert pd.isna(result['customer_id'].iloc[2])
        assert result['customer_id'].iloc[3] == 'CUST-1002'
        assert self.transformer.cleaning_stats['invalid_customer_ids'] == 2
    
    def test_clean_amount(self):
        df = pd.DataFrame({
            'amount': [100.0, -50.0, 0.0, 1000000.0]
        })
        result = self.transformer.clean_amount(df)
        assert result['amount'].iloc[0] == 100.0
        assert result['amount'].iloc[1] == 50.0
        assert result['amount'].iloc[2] == 0.0
        assert result['amount'].iloc[3] < 1000000.0
    
    def test_clean_dates(self):
        df = pd.DataFrame({
            'transaction_date': [
                '2024-01-15 10:30:00',
                '15/01/2024 10:30',
                'invalid',
                None
            ]
        })
        result = self.transformer.clean_dates(df)
        assert pd.api.types.is_datetime64_any_dtype(result['transaction_date'])
        assert self.transformer.cleaning_stats['invalid_dates'] >= 2
    
    def test_remove_duplicates(self):
        df = pd.DataFrame({
            'transaction_id': [1001, 1002, 1001, 1003],
            'amount': [100, 200, 300, 400]
        })
        result = self.transformer.remove_duplicates(df)
        assert len(result) == 3
        assert result['transaction_id'].nunique() == 3
        assert self.transformer.cleaning_stats['duplicates_removed'] == 1
    
    def test_transform_integration(self):
        df = pd.DataFrame({
            'transaction_id': ['1001', '1002', '1001', 'invalid'],
            'customer_id': ['CUST-1001', 'INVALID', 'CUST-1001', 'CUST-1003'],
            'amount': [100.0, -50.0, 200.0, None],
            'transaction_date': ['2024-01-15 10:30:00', 'invalid', None, '2024-01-15 11:30:00']
        })
        result = self.transformer.transform(df)
        assert 'rows_final' in self.transformer.cleaning_stats
        assert len(result) <= 4