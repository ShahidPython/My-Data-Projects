import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.features.engineering import (
    create_genre_features,
    create_temporal_features,
    create_textual_features,
    engineer_all_features
)

class TestFeatureEngineering:
    """Test feature engineering functions."""
    
    def setup_method(self):
        """Create test data."""
        self.test_df = pd.DataFrame({
            'title': ['The Great Adventure', 'Short', 'Another Movie Title'],
            'year': [1995, 2005, 2018],
            'genres': ['Action,Adventure', 'Comedy,Romance', 'Drama,Thriller'],
            'director': ['Director A', 'Director B', np.nan],
            'cast': ['Actor1,Actor2,Actor3', 'Actor4', 'Actor5,Actor6']
        })
    
    def test_create_genre_features_counts(self):
        """Test genre count feature."""
        df = create_genre_features(self.test_df)
        assert 'genre_count' in df.columns
        assert df['genre_count'].iloc[0] == 2
        assert df['genre_count'].dtype == int
    
    def test_create_genre_features_flags(self):
        """Test genre flag features."""
        df = create_genre_features(self.test_df)
        genre_columns = [col for col in df.columns if col.startswith('genre_')]
        assert len(genre_columns) > 0
        assert all(df[col].dtype == int for col in genre_columns)
    
    def test_create_temporal_features_decade(self):
        """Test decade feature creation."""
        df = create_temporal_features(self.test_df)
        assert 'decade' in df.columns
        assert df['decade'].iloc[0] == 1990
        assert df['decade'].dtype == int
    
    def test_create_temporal_features_era(self):
        """Test release era feature."""
        df = create_temporal_features(self.test_df)
        assert 'release_era' in df.columns
        assert set(df['release_era'].unique()) == {'90s', '2000s', '2010s'}
    
    def test_create_textual_features_title(self):
        """Test title-based features."""
        df = create_textual_features(self.test_df)
        assert 'title_length' in df.columns
        assert df['title_length'].iloc[0] == len('The Great Adventure')
        assert 'title_word_count' in df.columns
        assert df['title_word_count'].iloc[0] == 3
    
    def test_create_textual_features_cast(self):
        """Test cast-based features."""
        df = create_textual_features(self.test_df)
        assert 'cast_size' in df.columns
        assert df['cast_size'].iloc[0] == 3
        assert 'has_ensemble_cast' in df.columns
        assert df['has_ensemble_cast'].dtype == int
    
    def test_engineer_all_features_shape(self):
        """Test all features are created."""
        df = engineer_all_features(self.test_df)
        expected_cols = {'genre_count', 'decade', 'release_era', 'title_length', 
                        'cast_size', 'complexity_score'}
        assert expected_cols.issubset(set(df.columns))
        assert df.shape[0] == 3  # Same number of rows
    
    def test_engineer_all_features_no_data_loss(self):
        """Test no data is lost during engineering."""
        original_len = len(self.test_df)
        df = engineer_all_features(self.test_df)
        assert len(df) == original_len
    
    def test_engineer_all_features_complexity_score(self):
        """Test complexity score calculation."""
        df = engineer_all_features(self.test_df)
        assert 'complexity_score' in df.columns
        assert df['complexity_score'].dtype == float
        assert not df['complexity_score'].isnull().any()

if __name__ == '__main__':
    pytest.main([__file__, '-v'])