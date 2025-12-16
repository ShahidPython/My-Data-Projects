import pandas as pd
import json
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class SchemaValidator:
    def __init__(self, schema_path: str = "config/data_schema.json"):
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
    
    def validate_column_presence(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        required = list(self.schema['columns'].keys())
        missing = [col for col in required if col not in df.columns]
        present = [col for col in required if col in df.columns]
        
        logger.info(f"Required columns: {len(required)}")
        logger.info(f"Present columns: {len(present)}")
        logger.info(f"Missing columns: {missing}")
        
        return len(missing) == 0, missing
    
    def validate_data_types(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        errors = {}
        
        for col, rules in self.schema['columns'].items():
            if col not in df.columns:
                continue
                
            col_errors = []
            
            if rules['data_type'] == 'INTEGER':
                if not pd.api.types.is_integer_dtype(df[col]):
                    col_errors.append(f"Expected integer, got {df[col].dtype}")
            
            elif rules['data_type'] == 'DECIMAL':
                if not pd.api.types.is_float_dtype(df[col]):
                    col_errors.append(f"Expected decimal, got {df[col].dtype}")
            
            elif rules['data_type'] == 'VARCHAR':
                if not pd.api.types.is_string_dtype(df[col]):
                    col_errors.append(f"Expected string, got {df[col].dtype}")
            
            if col_errors:
                errors[col] = col_errors
        
        return errors
    
    def validate_constraints(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        errors = {}
        
        for col, rules in self.schema['columns'].items():
            if col not in df.columns:
                continue
                
            col_errors = []
            
            if 'nullable' in rules and rules['nullable'] == False:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    col_errors.append(f"Contains {null_count} null values (non-nullable)")
            
            if 'validation' in rules:
                try:
                    if rules['validation'] == 'BETWEEN 100000 AND 999999':
                        mask = (df[col] < 100000) | (df[col] > 999999)
                        if mask.any():
                            col_errors.append(f"{mask.sum()} values outside range 100000-999999")
                except:
                    pass
            
            if col_errors:
                errors[col] = col_errors
        
        return errors
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        logger.info("Starting schema validation")
        
        results = {
            "column_presence": {"passed": False, "missing": []},
            "data_types": {"errors": {}},
            "constraints": {"errors": {}},
            "overall_passed": False
        }
        
        presence_passed, missing = self.validate_column_presence(df)
        results["column_presence"]["passed"] = presence_passed
        results["column_presence"]["missing"] = missing
        
        type_errors = self.validate_data_types(df)
        results["data_types"]["errors"] = type_errors
        
        constraint_errors = self.validate_constraints(df)
        results["constraints"]["errors"] = constraint_errors
        
        overall_passed = (
            presence_passed and 
            len(type_errors) == 0 and 
            len(constraint_errors) == 0
        )
        results["overall_passed"] = overall_passed
        
        return results