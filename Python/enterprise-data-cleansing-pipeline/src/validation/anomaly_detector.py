import pandas as pd
import numpy as np
from scipy import stats
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self, threshold: float = 3.5):
        self.threshold = threshold
        self.anomalies = {}
    
    def detect_numeric_outliers(self, df: pd.DataFrame, column: str) -> pd.Series:
        if not pd.api.types.is_numeric_dtype(df[column]):
            return pd.Series(False, index=df.index)
        
        z_scores = np.abs(stats.zscore(df[column].dropna()))
        median_abs_dev = np.median(np.abs(df[column] - np.median(df[column])))
        modified_z_scores = 0.6745 * (df[column] - np.median(df[column])) / median_abs_dev
        
        outlier_mask = np.abs(modified_z_scores) > self.threshold
        self.anomalies[f'{column}_outliers'] = {
            'count': int(outlier_mask.sum()),
            'indices': df.index[outlier_mask].tolist()
        }
        
        return outlier_mask
    
    def detect_missing_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        missing_patterns = {}
        
        for col in df.columns:
            null_pct = df[col].isna().mean()
            if null_pct > 0.3:
                missing_patterns[col] = {
                    'missing_percentage': round(null_pct * 100, 2),
                    'warning': 'High missing rate'
                }
        
        self.anomalies['missing_patterns'] = missing_patterns
        return missing_patterns
    
    def detect_duplicate_keys(self, df: pd.DataFrame, key_columns: List[str]) -> Dict[str, Any]:
        duplicates = df.duplicated(subset=key_columns, keep=False)
        
        duplicate_info = {
            'count': int(duplicates.sum()),
            'percentage': round(duplicates.mean() * 100, 2),
            'example_ids': df.loc[duplicates, 'transaction_id'].head(5).tolist()
        }
        
        self.anomalies['duplicate_keys'] = duplicate_info
        return duplicate_info
    
    def detect_temporal_anomalies(self, df: pd.DataFrame, date_column: str) -> Dict[str, Any]:
        if date_column not in df.columns:
            return {}
        
        df_sorted = df.sort_values(date_column)
        time_diff = df_sorted[date_column].diff().dt.total_seconds()
        
        rapid_succession = time_diff < 60
        future_dates = df[date_column] > pd.Timestamp.now()
        
        temporal_issues = {
            'rapid_succession': {
                'count': int(rapid_succession.sum()),
                'threshold_seconds': 60
            },
            'future_dates': {
                'count': int(future_dates.sum())
            }
        }
        
        self.anomalies['temporal_anomalies'] = temporal_issues
        return temporal_issues
    
    def detect_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        logger.info("Detecting anomalies in data")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col in ['transaction_id', 'customer_id']:
                continue
            self.detect_numeric_outliers(df, col)
        
        self.detect_missing_patterns(df)
        self.detect_duplicate_keys(df, ['transaction_id'])
        
        if 'transaction_date' in df.columns:
            self.detect_temporal_anomalies(df, 'transaction_date')
        
        total_anomalies = sum(
            anomaly.get('count', 0) 
            for anomaly in self.anomalies.values() 
            if isinstance(anomaly, dict)
        )
        
        self.anomalies['summary'] = {
            'total_anomalies_detected': total_anomalies,
            'anomaly_rate': round(total_anomalies / len(df) * 100, 2)
        }
        
        return self.anomalies