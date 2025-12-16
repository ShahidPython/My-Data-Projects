import pandas as pd
import logging
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, output_dir: str = "data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_parquet(self, df: pd.DataFrame, filename: str) -> str:
        filepath = self.output_dir / f"{filename}.parquet"
        df.to_parquet(filepath, index=False, compression='snappy')
        logger.info(f"Saved Parquet file: {filepath}")
        return str(filepath)
    
    def save_csv(self, df: pd.DataFrame, filename: str) -> str:
        filepath = self.output_dir / f"{filename}.csv"
        df.to_csv(filepath, index=False)
        logger.info(f"Saved CSV file: {filepath}")
        return str(filepath)
    
    def generate_summary(self, df: pd.DataFrame, stats: dict) -> dict:
        summary = {
            "timestamp": datetime.now().isoformat(),
            "rows_processed": stats.get('rows_final', 0),
            "cleaning_stats": stats,
            "column_summary": {
                col: {
                    "dtype": str(df[col].dtype),
                    "null_count": int(df[col].isna().sum()),
                    "unique_count": int(df[col].nunique())
                }
                for col in df.columns
            }
        }
        return summary
    
    def save_summary(self, summary: dict, filename: str = "summary") -> str:
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary: {filepath}")
        return str(filepath)
    
    def load(self, df: pd.DataFrame, stats: dict, base_name: str = "cleaned_data"):
        parquet_path = self.save_parquet(df, base_name)
        csv_path = self.save_csv(df, f"{base_name}_backup")
        summary = self.generate_summary(df, stats)
        summary_path = self.save_summary(summary)
        
        return {
            "parquet": parquet_path,
            "csv": csv_path,
            "summary": summary_path
        }