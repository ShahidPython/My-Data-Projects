import logging
import logging.config
import yaml
from pathlib import Path
import json
from datetime import datetime
from typing import Optional, Dict, Any

def setup_logger(
    config_path: str = "config/logging_config.yaml",
    log_dir: str = "logs",
    module_name: Optional[str] = None
) -> logging.Logger:
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(exist_ok=True)
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        config = get_default_config(log_dir)
    
    logging.config.dictConfig(config)
    
    logger_name = module_name if module_name else __name__
    logger = logging.getLogger(logger_name)
    
    return logger

def get_default_config(log_dir: str) -> Dict[str, Any]:
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': f'{log_dir}/pipeline.log',
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {
                'level': 'DEBUG',
                'handlers': ['console', 'file']
            }
        }
    }

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_metric(self, metric_name: str, value: float, tags: Dict[str, Any] = None):
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'metric': metric_name,
            'value': value,
            'tags': tags or {}
        }
        
        if self.logger.isEnabledFor(logging.INFO):
            self.logger.info(json.dumps(log_data))
    
    def log_pipeline_event(self, event_type: str, pipeline_id: str, data: Dict[str, Any]):
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'pipeline_id': pipeline_id,
            'data': data
        }
        
        if self.logger.isEnabledFor(logging.INFO):
            self.logger.info(json.dumps(event_data))
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'level': 'ERROR',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        if self.logger.isEnabledFor(logging.ERROR):
            self.logger.error(json.dumps(error_data))