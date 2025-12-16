import pytest
import pandas as pd
from src.validation.schema_validator import SchemaValidator
from src.validation.quality_metrics import QualityMetrics
from src.validation.anomaly_detector import AnomalyDetector

class TestSchemaValidator:
    def setup_method(self):
        self.validator = SchemaValidator()
    
    def test_validate_column_presence_success(self):
        df = pd.DataFrame({
            'transaction_id': [100001],
            'customer_id': ['CUST-100001'],
            'transaction_timestamp': ['2024-01-15 10:30:00'],
            'transaction_type': ['purchase'],
            'product_sku': ['SKU-001'],
            'quantity': [1],
            'unit_price': [100.0],
            'discount_amount': [0.0],
            'tax_amount': [10.0],
            'total_amount': [110.0],
            'payment_method': ['credit_card'],
            'fraud_score': [0.1]
        })
        passed, missing = self.validator.validate_column_presence(df)
        assert passed == True
        assert len(missing) == 0
    
    def test_validate_column_presence_failure(self):
        df = pd.DataFrame({
            'transaction_id': [100001],
            'customer_id': ['CUST-100001']
        })
        passed, missing = self.validator.validate_column_presence(df)
        assert passed == False
        assert len(missing) > 0
    
    def test_validate_data_types(self):
        df = pd.DataFrame({
            'transaction_id': [100001, 'invalid'],
            'customer_id': ['CUST-100001', 123],
            'unit_price': [100.0, 'text']
        })
        errors = self.validator.validate_data_types(df)
        assert isinstance(errors, dict)
    
    def test_validate_constraints(self):
        df = pd.DataFrame({
            'transaction_id': [100001, None, 99999],
            'customer_id': ['CUST-100001', None, 'CUST-100002']
        })
        errors = self.validator.validate_constraints(df)
        assert 'transaction_id' in errors or 'customer_id' in errors

class TestQualityMetrics:
    def setup_method(self):
        self.metrics = QualityMetrics()
    
    def test_calculate_completeness(self):
        df = pd.DataFrame({
            'col1': [1, 2, None, 4],
            'col2': [None, None, 3, 4]
        })
        result = self.metrics.calculate_completeness(df)
        assert result['overall'] == 62.5
        assert result['by_column']['col1'] == 75.0
        assert result['by_column']['col2'] == 50.0
    
    def test_calculate_uniqueness(self):
        df = pd.DataFrame({
            'col1': [1, 1, 2, 3],
            'col2': ['A', 'B', 'C', 'D']
        })
        result = self.metrics.calculate_uniqueness(df)
        assert result['by_column']['col1'] == 75.0
        assert result['by_column']['col2'] == 100.0
    
    def test_calculate_validity(self):
        df = pd.DataFrame({
            'transaction_id': [100001, 100002, 99999, 1000000],
            'customer_id': ['CUST-100001', 'INVALID', 'CUST-100002', None],
            'amount': [100.0, -50.0, 0.0, 200.0]
        })
        result = self.metrics.calculate_validity(df)
        assert result['overall'] > 0

class TestAnomalyDetector:
    def setup_method(self):
        self.detector = AnomalyDetector(threshold=3.0)
    
    def test_detect_numeric_outliers(self):
        data = [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1000]
        df = pd.DataFrame({'value': data})
        outliers = self.detector.detect_numeric_outliers(df, 'value')
        assert outliers.sum() >= 1
    
    def test_detect_missing_patterns(self):
        df = pd.DataFrame({
            'col1': [1, None, None, None],
            'col2': [1, 2, 3, 4]
        })
        patterns = self.detector.detect_missing_patterns(df)
        assert 'col1' in patterns
    
    def test_detect_duplicate_keys(self):
        df = pd.DataFrame({
            'transaction_id': [1001, 1002, 1001, 1003],
            'data': ['A', 'B', 'C', 'D']
        })
        duplicates = self.detector.detect_duplicate_keys(df, ['transaction_id'])
        assert duplicates['count'] == 2
    
    def test_detect_all(self):
        df = pd.DataFrame({
            'transaction_id': range(100),
            'value': [1000] + [10] * 98 + [1000],
            'date': pd.date_range('2024-01-01', periods=100, freq='H')
        })
        anomalies = self.detector.detect_all(df)
        assert 'summary' in anomalies