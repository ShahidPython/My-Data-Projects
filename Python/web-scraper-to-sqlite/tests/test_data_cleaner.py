import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.data_cleaner import DataCleaner


class TestDataCleaner:
    """Comprehensive test suite for DataCleaner class."""
    
    @pytest.fixture
    def sample_config(self):
        """Provide sample configuration for testing."""
        return {
            'cleaning': {
                'date_format': '%Y-%m-%d',
                'numeric_columns': ['price', 'quantity'],
                'text_columns': ['title', 'description', 'category'],
                'drop_duplicates': True
            }
        }
    
    @pytest.fixture
    def sample_raw_data(self):
        """Provide sample raw data with various data quality issues."""
        return [
            {'title': 'Product One', 'price': '$29.99', 'description': 'First product', 'date': '2023-01-15'},
            {'title': 'Product Two', 'price': '$39.99', 'description': 'Second product', 'date': '2023-02-20'},
            {'title': 'Product Three', 'price': '$25.00', 'description': '', 'date': 'invalid-date'},
            {'title': 'Product One', 'price': '$29.99', 'description': 'First product', 'date': '2023-01-15'},  # Duplicate
            {'title': None, 'price': '$19.99', 'description': 'Missing title', 'date': '2023-03-10'},
            {'title': 'Product Four', 'price': 'invalid-price', 'description': 'Fourth product', 'date': '2023-04-05'},
            {'title': '  product five  ', 'price': '$49.99', 'description': '  extra spaces  ', 'date': '1672531200'},  # Unix timestamp
        ]
    
    @pytest.fixture
    def sample_data_with_outliers(self):
        """Provide data with numeric outliers."""
        return [
            {'title': 'Normal Product', 'price': '29.99', 'quantity': '10'},
            {'title': 'Cheap Product', 'price': '1.99', 'quantity': '5'},
            {'title': 'Expensive Product', 'price': '999.99', 'quantity': '2'},
            {'title': 'Very Expensive', 'price': '5000.00', 'quantity': '1'},  # Outlier
            {'title': 'Negative Price', 'price': '-10.00', 'quantity': '3'},   # Outlier
        ]
    
    @pytest.fixture
    def cleaner(self, sample_config):
        """Create DataCleaner instance with mocked config."""
        with patch('src.data_cleaner.DataCleaner._load_config', return_value=sample_config):
            return DataCleaner()
    
    def test_initialization(self, cleaner, sample_config):
        """Test cleaner initializes with correct configuration."""
        assert cleaner.config == sample_config
        assert cleaner.logger is not None
        assert isinstance(cleaner.cleaning_stats, dict)
    
    def test_clean_data_complete_pipeline(self, cleaner, sample_raw_data):
        """Test complete data cleaning pipeline."""
        result_df = cleaner.clean_data(sample_raw_data)
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) > 0  # Should have records after cleaning
        assert 'title' in result_df.columns
        assert 'price' in result_df.columns
        assert 'description' in result_df.columns
        assert 'date' in result_df.columns
    
    def test_clean_data_empty_input(self, cleaner):
        """Test cleaning handles empty input gracefully."""
        result_df = cleaner.clean_data([])
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 0
    
    def test_handle_missing_values(self, cleaner, sample_raw_data):
        """Test missing value handling."""
        df = pd.DataFrame(sample_raw_data)
        cleaned_df = cleaner._handle_missing_values(df)
        
        # Should not have completely empty rows
        assert not cleaned_df.isna().all(axis=1).any()
        
        # Text columns should have placeholders for missing values
        if 'title' in cleaned_df.columns:
            title_missing = cleaned_df['title'].isna() | (cleaned_df['title'] == 'Not Specified')
            assert title_missing.sum() == 0  # All titles should be filled
    
    def test_standardize_text_fields(self, cleaner):
        """Test text field standardization."""
        raw_data = [
            {'title': '  product one  ', 'description': '  EXTRA   SPACES  ', 'category': 'ELECTRONICS'},
            {'title': 'product-two', 'description': 'normal description', 'category': None},
        ]
        
        df = pd.DataFrame(raw_data)
        cleaned_df = cleaner._standardize_text_fields(df)
        
        # Test whitespace removal
        assert cleaned_df.loc[0, 'title'] == 'Product One'  # Title case and trimmed
        assert cleaned_df.loc[0, 'description'] == 'EXTRA SPACES'  # Single spaces, trimmed
        
        # Test NaN handling
        assert cleaned_df.loc[1, 'category'] == 'Not Specified'
    
    def test_convert_data_types(self, cleaner):
        """Test data type conversion."""
        raw_data = [
            {'price': '$29.99', 'quantity': '10'},
            {'price': 'invalid', 'quantity': '5'},
            {'price': '15.50', 'quantity': 'abc'},
        ]
        
        df = pd.DataFrame(raw_data)
        cleaned_df = cleaner._convert_data_types(df)
        
        # Price should be converted to numeric
        assert pd.api.types.is_numeric_dtype(cleaned_df['price'])
        assert cleaned_df.loc[0, 'price'] == 29.99
        assert pd.isna(cleaned_df.loc[1, 'price'])  # Invalid becomes NaN
        assert cleaned_df.loc[2, 'price'] == 15.50
    
    def test_normalize_numeric_fields(self, cleaner, sample_data_with_outliers):
        """Test numeric field normalization and outlier handling."""
        df = pd.DataFrame(sample_data_with_outliers)
        
        # First convert to numeric
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        
        cleaned_df = cleaner._normalize_numeric_fields(df)
        
        # Outliers should be capped, not removed
        assert len(cleaned_df) == len(df)
        
        # Prices should be within reasonable bounds
        price_series = cleaned_df['price'].dropna()
        if len(price_series) > 0:
            assert price_series.max() < 1000  # Outlier capped
            assert price_series.min() >= 0    # Negative price capped
    
    def test_validate_and_fix_dates(self, cleaner):
        """Test date validation and formatting."""
        raw_data = [
            {'date': '2023-01-15'},
            {'date': 'invalid-date'},
            {'date': '1672531200'},  # Unix timestamp: 2023-01-01
            {'date': '15/01/2023'},  # Different format
            {'date': None},
        ]
        
        df = pd.DataFrame(raw_data)
        cleaned_df = cleaner._validate_and_fix_dates(df)
        
        # Valid dates should be formatted correctly
        assert cleaned_df.loc[0, 'date'] == '2023-01-15'
        assert cleaned_df.loc[2, 'date'] == '2023-01-01'  # Unix timestamp converted
        
        # Invalid dates should be None
        assert cleaned_df.loc[1, 'date'] is None
        assert cleaned_df.loc[4, 'date'] is None
    
    def test_remove_duplicates(self, cleaner):
        """Test duplicate removal."""
        raw_data = [
            {'title': 'Product A', 'date': '2023-01-01'},
            {'title': 'Product A', 'date': '2023-01-01'},  # Exact duplicate
            {'title': 'Product A', 'date': '2023-01-02'},  # Different date
            {'title': 'Product B', 'date': '2023-01-01'},
        ]
        
        df = pd.DataFrame(raw_data)
        cleaned_df = cleaner._remove_duplicates(df)
        
        # Should remove exact duplicates based on title and date
        assert len(cleaned_df) == 3  # One duplicate removed
    
    def test_remove_duplicates_disabled(self, cleaner):
        """Test duplicate removal when disabled in config."""
        # Temporarily disable duplicate removal
        cleaner.config['cleaning']['drop_duplicates'] = False
        
        raw_data = [
            {'title': 'Product A', 'date': '2023-01-01'},
            {'title': 'Product A', 'date': '2023-01-01'},  # Exact duplicate
        ]
        
        df = pd.DataFrame(raw_data)
        cleaned_df = cleaner._remove_duplicates(df)
        
        # Should not remove duplicates when disabled
        assert len(cleaned_df) == 2
    
    def test_final_validation(self, cleaner):
        """Test final data validation."""
        raw_data = [
            {'title': 'Valid Product', 'price': 29.99},
            {'title': 'Not Specified', 'price': 19.99},  # Placeholder title
            {'title': None, 'price': 9.99},  # None title
            {'title': '', 'price': 39.99},   # Empty title
        ]
        
        df = pd.DataFrame(raw_data)
        cleaned_df = cleaner._final_validation(df)
        
        # Should not remove rows with placeholder titles
        assert len(cleaned_df) == 4
    
    def test_cleaning_stats_tracking(self, cleaner, sample_raw_data):
        """Test that cleaning statistics are properly tracked."""
        initial_count = len(sample_raw_data)
        result_df = cleaner.clean_data(sample_raw_data)
        final_count = len(result_df)
        
        # Stats should be populated
        assert 'initial_count' in cleaner.cleaning_stats
        assert 'final_count' in cleaner.cleaning_stats
        assert 'records_lost' in cleaner.cleaning_stats
        
        assert cleaner.cleaning_stats['initial_count'] == initial_count
        assert cleaner.cleaning_stats['final_count'] == final_count
        assert cleaner.cleaning_stats['records_lost'] == initial_count - final_count
    
    def test_get_cleaning_report(self, cleaner, sample_raw_data):
        """Test cleaning report generation."""
        # Run cleaning to populate stats
        cleaner.clean_data(sample_raw_data)
        
        report = cleaner.get_cleaning_report()
        
        assert 'cleaning_stats' in report
        assert 'retention_rate' in report
        assert 'timestamp' in report
        assert isinstance(report['timestamp'], str)
        
        # Retention rate should be calculated correctly
        expected_rate = (report['cleaning_stats']['final_count'] / 
                        report['cleaning_stats']['initial_count'] * 100)
        assert report['retention_rate'] == pytest.approx(expected_rate)
    
    def test_config_file_not_found(self):
        """Test proper error handling when config file is missing."""
        with patch('src.data_cleaner.open', side_effect=FileNotFoundError()):
            with pytest.raises(Exception, match="Configuration file 'config.yaml' not found"):
                DataCleaner()
    
    def test_complex_cleaning_scenario(self, cleaner):
        """Test complex cleaning scenario with multiple data issues."""
        complex_data = [
            {'title': '  PRODUCT ONE  ', 'price': '$29.99', 'description': '  great product  ', 'date': '2023-01-15', 'quantity': '10'},
            {'title': 'product two', 'price': 'INVALID', 'description': '', 'date': 'invalid', 'quantity': '5'},
            {'title': None, 'price': '$9999.99', 'description': 'outlier product', 'date': '1672531200', 'quantity': '1'},
            {'title': 'product three', 'price': '-5.00', 'description': 'negative price', 'date': '2023-02-01', 'quantity': '8'},
            {'title': 'product one', 'price': '$29.99', 'description': 'great product', 'date': '2023-01-15', 'quantity': '10'},  # Duplicate
        ]
        
        result_df = cleaner.clean_data(complex_data)
        
        # Basic validation
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) > 0
        assert len(result_df) < len(complex_data)  # Some records should be removed/cleaned
        
        # Data quality checks
        assert result_df['title'].str.strip().eq('').sum() == 0  # No empty titles
        assert (result_df['price'] >= 0).all()  # All prices non-negative
        assert result_df['price'].max() < 1000  # Outlier capped
        
        # Check cleaning report
        report = cleaner.get_cleaning_report()
        assert report['retention_rate'] >= 0
        assert report['retention_rate'] <= 100
    
    @patch('src.data_cleaner.logging.Logger.info')
    def test_cleaning_summary_logging(self, mock_log, cleaner, sample_raw_data):
        """Test that cleaning summary is properly logged."""
        cleaner.clean_data(sample_raw_data)
        
        # Verify summary logging was called
        assert mock_log.called
    
    def test_numeric_columns_edge_cases(self, cleaner):
        """Test numeric conversion with edge cases."""
        edge_case_data = [
            {'price': '29,99'},  # European decimal
            {'price': '$29.99'},  # Currency symbol
            {'price': '29.99 USD'},  # Currency with text
            {'price': ''},  # Empty string
            {'price': '1,000.50'},  # Thousands separator
        ]
        
        df = pd.DataFrame(edge_case_data)
        cleaned_df = cleaner._convert_data_types(df)
        
        # Should handle various numeric formats gracefully
        assert pd.api.types.is_numeric_dtype(cleaned_df['price'])