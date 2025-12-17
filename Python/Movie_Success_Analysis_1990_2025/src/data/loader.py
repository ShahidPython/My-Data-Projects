import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_raw_data(filename='movies_1990_2025.csv'):
    """Load raw movie dataset from data/raw/ directory."""
    raw_path = Path(__file__).parents[2] / 'data' / 'raw' / filename
    try:
        df = pd.read_csv(raw_path, low_memory=False)
        logger.info(f"Loaded raw data: {df.shape[0]:,} rows, {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        logger.error(f"Raw data file not found at {raw_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading raw data: {e}")
        raise

def load_processed_data(filename='movies_engineered.csv'):
    """Load processed dataset from data/processed/ directory."""
    processed_path = Path(__file__).parents[2] / 'data' / 'processed' / filename
    try:
        df = pd.read_csv(processed_path)
        logger.info(f"Loaded processed data: {df.shape[0]:,} rows")
        return df
    except FileNotFoundError:
        logger.warning(f"Processed file not found at {processed_path}")
        return None