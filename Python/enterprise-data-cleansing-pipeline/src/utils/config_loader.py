import yaml
import json
from pathlib import Path
from typing import Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            logger.error(f"Config file not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML config {filename}: {e}")
            return {}
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            logger.error(f"Config file not found: {filepath}")
            return {}
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f) or {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON config {filename}: {e}")
            return {}
    
    def load_config(self, filename: str) -> Dict[str, Any]:
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            logger.error(f"Config file not found: {filepath}")
            return {}
        
        if filepath.suffix.lower() == '.yaml' or filepath.suffix.lower() == '.yml':
            return self.load_yaml(filename)
        elif filepath.suffix.lower() == '.json':
            return self.load_json(filename)
        else:
            logger.error(f"Unsupported config format: {filepath.suffix}")
            return {}
    
    def get_cleaning_rules(self) -> Dict[str, Any]:
        return self.load_config("cleaning_rules.json")
    
    def get_data_schema(self) -> Dict[str, Any]:
        return self.load_config("data_schema.json")
    
    def get_logging_config(self) -> Dict[str, Any]:
        return self.load_config("logging_config.yaml")
    
    def save_config(self, filename: str, data: Dict[str, Any]):
        filepath = self.config_dir / filename
        
        if filepath.suffix.lower() == '.yaml' or filepath.suffix.lower() == '.yml':
            with open(filepath, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        elif filepath.suffix.lower() == '.json':
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported config format: {filepath.suffix}")
        
        logger.info(f"Config saved: {filepath}")