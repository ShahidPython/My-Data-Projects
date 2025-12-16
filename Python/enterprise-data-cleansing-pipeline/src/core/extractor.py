import pandas as pd
import logging
from pathlib import Path
from typing import Union, Dict, Any
import json

logger = logging.getLogger(__name__)

class DataExtractor:
    def __init__(self, config_path: str = "config/cleaning_rules.json"):
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def extract_csv(self, file_path: Union[str, Path]) -> pd.DataFrame:
        logger.info(f"Extracting data from {file_path}")
        
        try:
            df = pd.read_csv(
                file_path,
                dtype_backend='pyarrow',
                low_memory=False
            )
            logger.info(f"Successfully loaded {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to extract data: {e}")
            raise
    
    def extract_json(self, file_path: Union[str, Path]) -> pd.DataFrame:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame([data])
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        required_columns = ["transaction_id", "customer_id", "amount"]
        missing = [col for col in required_columns if col not in df.columns]
        
        if missing:
            logger.error(f"Missing required columns: {missing}")
            return False
        return True