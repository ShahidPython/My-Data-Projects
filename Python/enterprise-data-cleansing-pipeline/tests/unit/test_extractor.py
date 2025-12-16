import pytest
import pandas as pd
from pathlib import Path
import tempfile
import json
from src.core.extractor import DataExtractor

class TestDataExtractor:
    def setup_method(self):
        self.extractor = DataExtractor()
        
    def test_extract_csv_valid(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("transaction_id,customer_id,amount\n")
            f.write("1001,CUST-1001,150.00\n")
            f.write("1002,CUST-1002,250.00\n")
            temp_path = f.name
        
        try:
            df = self.extractor.extract_csv(temp_path)
            assert len(df) == 2
            assert list(df.columns) == ['transaction_id', 'customer_id', 'amount']
            assert df['transaction_id'].iloc[0] == 1001
        finally:
            Path(temp_path).unlink()
    
    def test_extract_csv_missing_file(self):
        with pytest.raises(Exception):
            self.extractor.extract_csv("nonexistent.csv")
    
    def test_validate_schema_success(self):
        df = pd.DataFrame({
            'transaction_id': [1001, 1002],
            'customer_id': ['CUST-1001', 'CUST-1002'],
            'amount': [150.0, 250.0]
        })
        assert self.extractor.validate_schema(df) == True
    
    def test_validate_schema_failure(self):
        df = pd.DataFrame({
            'transaction_id': [1001, 1002],
            'amount': [150.0, 250.0]
        })
        assert self.extractor.validate_schema(df) == False
    
    def test_extract_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"customer_id": "CUST-1001", "amount": 150.0}, f)
            temp_path = f.name
        
        try:
            df = self.extractor.extract_json(temp_path)
            assert len(df) == 1
            assert df['customer_id'].iloc[0] == 'CUST-1001'
        finally:
            Path(temp_path).unlink()