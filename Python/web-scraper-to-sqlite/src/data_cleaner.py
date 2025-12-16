import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List
import re
from datetime import datetime
import yaml


class DataCleaner:
    """Professional data cleaning and transformation pipeline."""
    
    def __init__(self):
        """Initialize cleaner with configuration."""
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
        self.cleaning_stats = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load cleaning configuration from YAML."""
        try:
            with open('config.yaml', 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise Exception("Configuration file 'config.yaml' not found")
    
    def clean_data(self, raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Execute complete data cleaning pipeline.
        
        Args:
            raw_data: List of dictionaries from scraper
            
        Returns:
            pd.DataFrame: Cleaned and transformed data
        """
        self.cleaning_stats = {'initial_count': len(raw_data)}
        self.logger.info(f"Starting data cleaning pipeline for {len(raw_data)} records")
        
        if not raw_data:
            self.logger.warning("No data provided for cleaning")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_data)
        self.logger.info(f"Converted to DataFrame with shape: {df.shape}")
        
        # Execute cleaning steps
        df = self._handle_missing_values(df)
        df = self._standardize_text_fields(df)
        df = self._convert_data_types(df)
        df = self._normalize_numeric_fields(df)
        df = self._validate_and_fix_dates(df)
        df = self._remove_duplicates(df)
        df = self._final_validation(df)
        
        self.cleaning_stats['final_count'] = len(df)
        self.cleaning_stats['records_lost'] = self.cleaning_stats['initial_count'] - len(df)
        
        self._log_cleaning_summary()
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values according to data type."""
        self.logger.info("Handling missing values")
        
        initial_count = len(df)
        
        # Column-specific missing value handling
        for column in df.columns:
            missing_count = df[column].isna().sum()
            
            if missing_count > 0:
                self.logger.debug(f"Column '{column}': {missing_count} missing values")
                
                if column in self.config['cleaning']['numeric_columns']:
                    # For numeric columns, fill with median
                    if not df[column].empty:
                        median_val = df[column].median()
                        df[column] = df[column].fillna(median_val)
                        self.logger.debug(f"Filled numeric column '{column}' with median: {median_val}")
                
                elif column in self.config['cleaning']['text_columns']:
                    # For text columns, fill with placeholder
                    df[column] = df[column].fillna('Not Specified')
                    self.logger.debug(f"Filled text column '{column}' with placeholder")
                
                else:
                    # For other columns, use mode or specific logic
                    if not df[column].empty and df[column].notna().any():
                        mode_val = df[column].mode().iloc[0] if not df[column].mode().empty else 'Unknown'
                        df[column] = df[column].fillna(mode_val)
        
        # Remove rows where critical fields are entirely missing
        critical_columns = [col for col in self.config['cleaning']['text_columns'] if col in df.columns]
        if critical_columns:
            before_drop = len(df)
            df = df.dropna(subset=critical_columns, how='all')
            dropped_count = before_drop - len(df)
            if dropped_count > 0:
                self.logger.warning(f"Dropped {dropped_count} rows with all critical fields missing")
        
        self.cleaning_stats['after_missing_handling'] = len(df)
        return df
    
    def _standardize_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize text fields."""
        self.logger.info("Standardizing text fields")
        
        text_columns = [col for col in self.config['cleaning']['text_columns'] if col in df.columns]
        
        for column in text_columns:
            if column in df.columns:
                # Convert to string and handle NaN
                df[column] = df[column].astype(str)
                
                # Remove extra whitespace
                df[column] = df[column].str.strip()
                
                # Replace multiple spaces with single space
                df[column] = df[column].str.replace(r'\s+', ' ', regex=True)
                
                # Capitalize first letter of each word for titles
                if column == 'title':
                    df[column] = df[column].str.title()
                
                # Handle empty strings
                df[column] = df[column].replace({'nan': 'Not Specified', '': 'Not Specified'})
        
        return df
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate data types."""
        self.logger.info("Converting data types")
        
        # Convert numeric columns
        numeric_columns = [col for col in self.config['cleaning']['numeric_columns'] if col in df.columns]
        for column in numeric_columns:
            try:
                # Remove currency symbols, commas, etc.
                df[column] = df[column].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                df[column] = pd.to_numeric(df[column], errors='coerce')
                self.logger.debug(f"Converted '{column}' to numeric")
            except Exception as e:
                self.logger.warning(f"Failed to convert '{column}' to numeric: {e}")
        
        return df
    
    def _normalize_numeric_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle numeric field normalization and outlier detection."""
        self.logger.info("Normalizing numeric fields")
        
        numeric_columns = [col for col in self.config['cleaning']['numeric_columns'] if col in df.columns]
        
        for column in numeric_columns:
            if column in df.columns and df[column].notna().any():
                # Remove extreme outliers using IQR method
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = ((df[column] < lower_bound) | (df[column] > upper_bound)).sum()
                if outliers > 0:
                    self.logger.info(f"Found {outliers} outliers in '{column}', capping values")
                    df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def _validate_and_fix_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and standardize date fields."""
        self.logger.info("Processing date fields")
        
        if 'date' in df.columns:
            date_format = self.config['cleaning']['date_format']
            valid_dates = []
            
            for date_str in df['date']:
                try:
                    if pd.isna(date_str):
                        valid_dates.append(None)
                        continue
                    
                    # Try multiple date parsing strategies
                    parsed_date = pd.to_datetime(date_str, errors='coerce', utc=True)
                    
                    if pd.isna(parsed_date):
                        # Try parsing as Unix timestamp
                        try:
                            parsed_date = pd.to_datetime(float(date_str), unit='s', errors='coerce', utc=True)
                        except:
                            parsed_date = pd.NaT
                    
                    valid_dates.append(parsed_date)
                    
                except Exception as e:
                    self.logger.debug(f"Date parsing failed for '{date_str}': {e}")
                    valid_dates.append(pd.NaT)
            
            df['date'] = valid_dates
            
            # Format valid dates to string
            df['date'] = df['date'].apply(
                lambda x: x.strftime(date_format) if pd.notna(x) else None
            )
            
            invalid_dates = df['date'].isna().sum()
            if invalid_dates > 0:
                self.logger.warning(f"Could not parse {invalid_dates} date values")
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records based on configuration."""
        if self.config['cleaning']['drop_duplicates']:
            initial_count = len(df)
            
            # Use title and date as unique identifier if available
            subset_cols = []
            if 'title' in df.columns:
                subset_cols.append('title')
            if 'date' in df.columns:
                subset_cols.append('date')
            
            if subset_cols:
                df = df.drop_duplicates(subset=subset_cols, keep='first')
            else:
                df = df.drop_duplicates()
            
            duplicates_removed = initial_count - len(df)
            if duplicates_removed > 0:
                self.logger.info(f"Removed {duplicates_removed} duplicate records")
        
        return df
    
    def _final_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform final data validation and quality checks."""
        self.logger.info("Performing final data validation")
        
        # Ensure no completely empty rows
        df = df.dropna(how='all')
        
        # Validate required fields
        if 'title' in df.columns:
            empty_titles = (df['title'].isna() | (df['title'] == 'Not Specified')).sum()
            if empty_titles > 0:
                self.logger.warning(f"{empty_titles} records have empty titles")
        
        return df
    
    def _log_cleaning_summary(self) -> None:
        """Log comprehensive cleaning summary."""
        summary = f"""
        📊 DATA CLEANING SUMMARY
        =========================
        Initial Records:    {self.cleaning_stats['initial_count']}
        Final Records:      {self.cleaning_stats['final_count']}
        Records Lost:       {self.cleaning_stats['records_lost']}
        Retention Rate:     {(self.cleaning_stats['final_count'] / self.cleaning_stats['initial_count'] * 100):.1f}%
        =========================
        """
        self.logger.info(summary)
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """Generate detailed cleaning report."""
        return {
            'cleaning_stats': self.cleaning_stats,
            'retention_rate': (self.cleaning_stats['final_count'] / self.cleaning_stats['initial_count'] * 100) if self.cleaning_stats['initial_count'] > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }