import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class QualityMetrics:
    def __init__(self):
        self.metrics = {}
    
    def calculate_completeness(self, df: pd.DataFrame) -> Dict[str, float]:
        completeness = {}
        total_rows = len(df)
        
        for column in df.columns:
            non_null = df[column].count()
            completeness[column] = round(non_null / total_rows * 100, 2)
        
        overall = sum(completeness.values()) / len(completeness)
        self.metrics['completeness'] = {
            'overall': round(overall, 2),
            'by_column': completeness
        }
        
        return self.metrics['completeness']
    
    def calculate_uniqueness(self, df: pd.DataFrame) -> Dict[str, float]:
        uniqueness = {}
        total_rows = len(df)
        
        for column in df.columns:
            unique_count = df[column].nunique()
            uniqueness[column] = round(unique_count / total_rows * 100, 2)
        
        overall = sum(uniqueness.values()) / len(uniqueness)
        self.metrics['uniqueness'] = {
            'overall': round(overall, 2),
            'by_column': uniqueness
        }
        
        return self.metrics['uniqueness']
    
    def calculate_validity(self, df: pd.DataFrame) -> Dict[str, float]:
        validity = {}
        
        for column in df.columns:
            if column == 'transaction_id':
                valid = df[column].between(100000, 999999).sum()
            elif column == 'customer_id':
                pattern = r'^CUST-\d+$'
                valid = df[column].astype(str).str.match(pattern).sum()
            elif column == 'amount':
                valid = (df[column] > 0).sum()
            else:
                valid = df[column].notna().sum()
            
            validity[column] = round(valid / len(df) * 100, 2)
        
        overall = sum(validity.values()) / len(validity)
        self.metrics['validity'] = {
            'overall': round(overall, 2),
            'by_column': validity
        }
        
        return self.metrics['validity']
    
    def calculate_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        consistency_checks = {}
        
        if all(col in df.columns for col in ['amount', 'unit_price', 'quantity']):
            calculated = df['unit_price'] * df['quantity']
            diff = abs(calculated - df['amount'])
            consistency_checks['amount_calculation'] = {
                'passed': (diff < 0.01).all(),
                'max_difference': diff.max()
            }
        
        self.metrics['consistency'] = consistency_checks
        return consistency_checks
    
    def calculate_all(self, df: pd.DataFrame) -> Dict[str, Any]:
        logger.info("Calculating data quality metrics")
        
        self.calculate_completeness(df)
        self.calculate_uniqueness(df)
        self.calculate_validity(df)
        self.calculate_consistency(df)
        
        overall_score = (
            self.metrics['completeness']['overall'] +
            self.metrics['uniqueness']['overall'] +
            self.metrics['validity']['overall']
        ) / 3
        
        self.metrics['overall_score'] = round(overall_score, 2)
        
        logger.info(f"Overall quality score: {overall_score}%")
        return self.metrics