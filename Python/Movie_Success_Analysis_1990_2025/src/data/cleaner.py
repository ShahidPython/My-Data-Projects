import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def validate_schema(df):
    """Validate dataset schema and constraints."""
    required_cols = ['title', 'year', 'genres']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    if 'year' in df.columns:
        assert df['year'].min() >= 1990, "Data contains pre-1990 records"
        assert df['year'].max() <= 2025, "Data contains post-2025 records"
    
    logger.info(f"Schema validated: {df.shape[0]:,} records")
    return True

def clean_movie_data(df):
    """Perform comprehensive data cleaning."""
    df_clean = df.copy()
    
    # Year filtering
    df_clean = df_clean[(df_clean['year'] >= 1990) & (df_clean['year'] <= 2025)]
    
    # Handle missing values
    df_clean['genres'] = df_clean['genres'].fillna('Unknown')
    if 'director' in df_clean.columns:
       df_clean['director'] = df_clean['director'].fillna('Unknown')
    else:
       df_clean['director'] = 'Unknown'
    
    if 'cast' in df_clean.columns:
       df_clean['cast'] = df_clean['cast'].fillna('')
    else:
       df_clean['cast'] = ''
    
    # Standardize text columns
    text_cols = ['title', 'genres', 'director', 'cast']
    for col in text_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
    
    # Remove exact duplicates
    initial_count = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=['title', 'year', 'director'], keep='first')
    removed = initial_count - len(df_clean)
    if removed > 0:
        logger.info(f"Removed {removed} duplicate records")
    
    logger.info(f"Cleaning complete: {len(df_clean):,} records retained")
    return df_clean