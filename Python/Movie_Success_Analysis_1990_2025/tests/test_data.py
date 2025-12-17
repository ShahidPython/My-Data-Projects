import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data.loader import load_raw_data
from src.data.cleaner import clean_movie_data, validate_schema

class TestDataLoading:
    """Test data loading functionality."""
    
    def test_raw_data_exists(self):
        """Test that raw data file exists."""
        raw_path = Path(__file__).parent.parent / 'data' / 'raw' / 'movies_1990_2025.csv'
        assert raw_path.exists(), f"Raw data file not found at {raw_path}"
    
    def test_load_raw_data_shape(self):
        """Test raw data loading returns correct shape."""
        df = load_raw_data()
        assert isinstance(df, pd.DataFrame), "Should return DataFrame"
        assert len(df) > 1000, f"Dataset too small: {len(df)} rows"
        assert len(df.columns) >= 5, f"Not enough columns: {len(df.columns)}"
    
    def test_load_raw_data_columns(self):
        """Test required columns exist."""
        df = load_raw_data()
        required_cols = {'title', 'year', 'genres'}
        missing = required_cols - set(df.columns)
        assert len(missing) == 0, f"Missing required columns: {missing}"

class TestDataCleaning:
    """Test data cleaning functionality."""
    
    def setup_method(self):
        """Create test data."""
        self.test_df = pd.DataFrame({
            'title': ['Movie A', 'Movie B', 'Movie C', 'Movie A'],
            'year': [1995, 2005, 2015, 1995],
            'genres': ['Action,Drama', 'Comedy', np.nan, 'Action,Drama'],
            'director': ['Director X', np.nan, 'Director Y', 'Director X'],
            'cast': ['Actor1,Actor2', 'Actor3', '', 'Actor1,Actor2']
        })
    
    def test_clean_movie_data_removes_duplicates(self):
        """Test duplicate removal."""
        cleaned = clean_movie_data(self.test_df)
        assert len(cleaned) == 3, f"Should remove duplicates, got {len(cleaned)} rows"
    
    def test_clean_movie_data_handles_missing(self):
        """Test missing value handling."""
        cleaned = clean_movie_data(self.test_df)
        assert cleaned['genres'].isnull().sum() == 0, "Should fill missing genres"
        assert cleaned['director'].isnull().sum() == 0, "Should fill missing directors"
    
    def test_validate_schema_passes(self):
        """Test schema validation with correct data."""
        df = pd.DataFrame({
            'title': ['Test'],
            'year': [2000],
            'genres': ['Action']
        })
        assert validate_schema(df) == True, "Should validate correct schema"
    
    def test_validate_schema_fails_missing_cols(self):
        """Test schema validation fails with missing columns."""
        df = pd.DataFrame({'year': [2000]})
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_schema(df)
    
    def test_validate_schema_year_range(self):
        """Test year range validation."""
        df = pd.DataFrame({
            'title': ['Old', 'Future'],
            'year': [1989, 2026],
            'genres': ['Action', 'Drama']
        })
        try:
            validate_schema(df)
            assert False, "Should fail year validation"
        except AssertionError as e:
            assert "pre-1990" in str(e) or "post-2025" in str(e)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])