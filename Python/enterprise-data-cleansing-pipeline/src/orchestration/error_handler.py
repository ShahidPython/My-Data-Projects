import logging
import traceback
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self, error_log_dir: str = "logs/errors"):
        self.error_log_dir = Path(error_log_dir)
        self.error_log_dir.mkdir(parents=True, exist_ok=True)
    
    def classify_error(self, error: Exception) -> Dict[str, Any]:
        error_type = type(error).__name__
        
        classification = {
            'type': error_type,
            'message': str(error),
            'severity': 'medium',
            'category': 'unknown'
        }
        
        # Classification logic
        if 'file' in str(error).lower() or 'not found' in str(error).lower():
            classification.update({
                'category': 'file_io',
                'severity': 'high'
            })
        elif 'memory' in str(error).lower() or 'size' in str(error).lower():
            classification.update({
                'category': 'resource',
                'severity': 'high'
            })
        elif 'type' in str(error).lower() or 'cast' in str(error).lower():
            classification.update({
                'category': 'data_type',
                'severity': 'medium'
            })
        elif 'key' in str(error).lower() or 'index' in str(error).lower():
            classification.update({
                'category': 'data_integrity',
                'severity': 'medium'
            })
        
        return classification
    
    def log_error(self, error: Exception, pipeline_id: str) -> str:
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'pipeline_id': pipeline_id,
            'error': self.classify_error(error),
            'traceback': traceback.format_exc()
        }
        
        # Create error log file
        error_file = self.error_log_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(error_file, 'w') as f:
            json.dump(error_data, f, indent=2)
        
        logger.error(f"Error logged: {error_file}")
        return str(error_file)
    
    def handle_error(self, error: Exception, pipeline_id: str) -> Dict[str, Any]:
        error_file = self.log_error(error, pipeline_id)
        
        response = {
            'handled_at': datetime.now().isoformat(),
            'pipeline_id': pipeline_id,
            'error_file': error_file,
            'classification': self.classify_error(error),
            'action_taken': 'logged_and_continued'
        }
        
        # Determine recovery action
        error_class = self.classify_error(error)
        
        if error_class['severity'] == 'high':
            response['action_taken'] = 'pipeline_stopped'
        elif error_class['category'] == 'data_type':
            response['action_taken'] = 'default_values_applied'
        elif error_class['category'] == 'file_io':
            response['action_taken'] = 'retry_scheduled'
        
        return response
    
    def get_error_stats(self, hours: int = 24) -> Dict[str, Any]:
        error_files = list(self.error_log_dir.glob("error_*.json"))
        
        stats = {
            'total_errors': len(error_files),
            'by_category': {},
            'by_severity': {},
            'recent_errors': []
        }
        
        for error_file in error_files[-100:]:
            try:
                with open(error_file, 'r') as f:
                    error_data = json.load(f)
                
                category = error_data['error']['category']
                severity = error_data['error']['severity']
                
                stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
                stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
                
                if len(stats['recent_errors']) < 10:
                    stats['recent_errors'].append({
                        'time': error_data['timestamp'],
                        'type': error_data['error']['type'],
                        'message': error_data['error']['message'][:100]
                    })
                    
            except:
                continue
        
        return stats