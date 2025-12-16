import logging
from typing import Dict, Any, Optional
from datetime import datetime
import time
import json
from pathlib import Path

from src.core.extractor import DataExtractor
from src.core.transformer import DataTransformer
from src.core.loader import DataLoader
from src.validation.schema_validator import SchemaValidator
from src.validation.quality_metrics import QualityMetrics
from src.validation.anomaly_detector import AnomalyDetector
from .error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class PipelineManager:
    def __init__(self, config_path: str = "config/cleaning_rules.json"):
        self.config_path = config_path
        self.error_handler = ErrorHandler()
        self.pipeline_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.metrics = {}
        
    def initialize_components(self):
        self.extractor = DataExtractor(self.config_path)
        self.transformer = DataTransformer(self.extractor.config.get('rules', {}))
        self.loader = DataLoader()
        self.validator = SchemaValidator()
        self.quality_checker = QualityMetrics()
        self.anomaly_detector = AnomalyDetector()
    
    def execute_pipeline(self, input_file: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Starting pipeline {self.pipeline_id}")
        
        try:
            self.initialize_components()
            
            # Extract
            logger.info("Phase 1: Extraction")
            raw_data = self.extractor.extract_csv(input_file)
            
            if not self.extractor.validate_schema(raw_data):
                raise ValueError("Schema validation failed during extraction")
            
            # Validate
            logger.info("Phase 2: Validation")
            validation_results = self.validator.validate(raw_data)
            self.metrics['validation'] = validation_results
            
            if not validation_results['overall_passed']:
                logger.warning("Schema validation failed, but continuing with transformation")
            
            # Transform
            logger.info("Phase 3: Transformation")
            cleaned_data = self.transformer.transform(raw_data)
            self.metrics['transformation'] = self.transformer.cleaning_stats
            
            # Quality check
            logger.info("Phase 4: Quality assessment")
            quality_metrics = self.quality_checker.calculate_all(cleaned_data)
            self.metrics['quality'] = quality_metrics
            
            # Anomaly detection
            logger.info("Phase 5: Anomaly detection")
            anomalies = self.anomaly_detector.detect_all(cleaned_data)
            self.metrics['anomalies'] = anomalies
            
            # Load
            logger.info("Phase 6: Loading")
            output_paths = self.loader.load(cleaned_data, self.transformer.cleaning_stats)
            self.metrics['output'] = output_paths
            
            # Calculate execution metrics
            execution_time = time.time() - start_time
            self.metrics['execution'] = {
                'pipeline_id': self.pipeline_id,
                'start_time': datetime.fromtimestamp(start_time).isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': round(execution_time, 2),
                'rows_per_second': round(len(cleaned_data) / execution_time, 2)
            }
            
            # Determine success
            quality_score = quality_metrics.get('overall_score', 0)
            success = quality_score >= 95.0
            
            self.metrics['success'] = success
            self.metrics['quality_score'] = quality_score
            
            logger.info(f"Pipeline completed: success={success}, quality={quality_score}%")
            
            return {
                'success': success,
                'metrics': self.metrics,
                'output_paths': output_paths
            }
            
        except Exception as e:
            error_result = self.error_handler.handle_error(e, self.pipeline_id)
            self.metrics['error'] = error_result
            logger.error(f"Pipeline failed: {str(e)}")
            
            return {
                'success': False,
                'error': error_result,
                'metrics': self.metrics
            }
    
    def generate_report(self) -> str:
        report_path = Path("reports") / f"{self.pipeline_id}_report.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.metrics, f, indent=2, default=str)
        
        logger.info(f"Report generated: {report_path}")
        return str(report_path)