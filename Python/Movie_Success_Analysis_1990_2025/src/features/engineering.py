import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_genre_features(df):
    """Extract features from genres column."""
    df = df.copy()
    
    # Genre count
    df['genre_count'] = df['genres'].str.split(',').str.len().fillna(0).astype(int)
    
    # Genre flags for top genres
    all_genres = []
    for genre_str in df['genres'].dropna():
        all_genres.extend([g.strip().lower() for g in genre_str.split(',')])
    
    from collections import Counter
    top_genres = [genre for genre, _ in Counter(all_genres).most_common(10)]
    
    for genre in top_genres:
        df[f'genre_{genre}'] = df['genres'].str.lower().str.contains(genre).astype(int)
    
    logger.info(f"Created {len(top_genres)} genre flag features")
    return df

def create_temporal_features(df):
    """Create time-based features."""
    df = df.copy()
    
    # Decade
    df['decade'] = (df['year'] // 10 * 10).astype(int)
    
    # Release era
    conditions = [
        (df['year'] < 2000),
        ((df['year'] >= 2000) & (df['year'] < 2010)),
        ((df['year'] >= 2010) & (df['year'] < 2020)),
        (df['year'] >= 2020)
    ]
    choices = ['90s', '2000s', '2010s', '2020s']
    df['release_era'] = np.select(conditions, choices, default='unknown')
    
    # Years since 1990
    df['years_since_1990'] = df['year'] - 1990
    
    logger.info("Created temporal features")
    return df

def create_textual_features(df):
    """Create features from text columns."""
    df = df.copy()
    
    # Title features
    df['title_length'] = df['title'].str.len().fillna(0)
    df['title_word_count'] = df['title'].str.split().str.len().fillna(0)
    
    # Cast features
    df['cast_size'] = df['cast'].str.split(',').str.len().fillna(0)
    df['has_ensemble_cast'] = (df['cast_size'] > 5).astype(int)
    
    # Director features
    df['has_director'] = (~df['director'].isna() & (df['director'] != 'Unknown')).astype(int)
    
    logger.info("Created textual features")
    return df

def engineer_all_features(df):
    """Apply all feature engineering steps."""
    logger.info("Starting feature engineering pipeline")
    
    # Apply transformations
    df = create_genre_features(df)
    df = create_temporal_features(df)
    df = create_textual_features(df)
    
    # Composite feature
    df['complexity_score'] = (
        df['genre_count'] * 0.3 + 
        df['cast_size'] * 0.2 + 
        df['title_word_count'] * 0.1 +
        df['years_since_1990'] * 0.4
    ).round(2)
    
    logger.info(f"Feature engineering complete. Final shape: {df.shape}")
    return df