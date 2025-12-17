#!/usr/bin/env python3
"""
Main pipeline script for Movie Success Analysis.
Runs the complete data processing and modeling pipeline.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import load_raw_data
from src.data.cleaner import clean_movie_data, validate_schema
from src.features.engineering import engineer_all_features
from src.models.predictor import train_predictor
from src.visualization.custom_plots import create_dashboard_figures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'logs' / 'pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from YAML file."""
    config_path = project_root / 'config' / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    logger.info(f"Loaded configuration from {config_path}")
    return config

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        'data/processed',
        'results/figures',
        'results/tables',
        'logs'
    ]
    
    for dir_path in directories:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {full_path}")

def run_data_pipeline():
    """Run the complete data processing pipeline."""
    logger.info("=" * 60)
    logger.info("STARTING MOVIE SUCCESS ANALYSIS PIPELINE")
    logger.info("=" * 60)
    
    config = load_config()
    create_directories()
    
    # Step 1: Load raw data
    logger.info("Step 1: Loading raw data...")
    raw_data_path = project_root / config['data']['raw']['path']
    df_raw = load_raw_data()
    logger.info(f"✓ Raw data loaded: {df_raw.shape[0]:,} rows, {df_raw.shape[1]} columns")
    
    # Step 2: Validate and clean
    logger.info("Step 2: Validating and cleaning data...")
    validate_schema(df_raw)
    df_clean = clean_movie_data(df_raw)
    logger.info(f"✓ Data cleaned: {df_clean.shape[0]:,} rows retained")
    
    # Step 3: Feature engineering
    logger.info("Step 3: Engineering features...")
    df_features = engineer_all_features(df_clean)
    processed_path = project_root / config['data']['processed']['path']
    df_features.to_csv(processed_path, index=False)
    logger.info(f"✓ Features engineered: {df_features.shape[1]} total columns")
    logger.info(f"✓ Processed data saved to: {processed_path}")
    
    # Step 4: Train model
    logger.info("Step 4: Training predictive model...")
    model_path = project_root / config['paths']['models']
    predictor, metrics = train_predictor(df_features, save_path=str(model_path))
    logger.info(f"✓ Model trained and saved to: {model_path}")
    logger.info(f"✓ Model performance: Accuracy = {metrics['accuracy']:.3f}, F1 = {metrics['f1']:.3f}")
    
    # Step 5: Generate visualizations
    logger.info("Step 5: Generating visualizations...")
    figures_dir = project_root / config['paths']['figures']
    create_dashboard_figures(df_features, output_dir=str(figures_dir))
    
    # Step 6: Create summary report
    logger.info("Step 6: Creating summary report...")
    summary = {
        'pipeline_completed': pd.Timestamp.now().isoformat(),
        'data_points': len(df_features),
        'features_created': len(df_features.columns),
        'model_performance': metrics,
        'output_files': [
            str(processed_path.relative_to(project_root)),
            str(model_path.relative_to(project_root)),
            str(figures_dir.relative_to(project_root))
        ]
    }
    
    summary_path = project_root / 'results' / 'pipeline_summary.json'
    import json
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)
    logger.info(f"Summary report: {summary_path}")
    
    return True

def main():
    """Main entry point."""
    try:
        success = run_data_pipeline()
        if success:
            print("\n✅ Pipeline completed successfully!")
            print("📊 Check logs/pipeline.log for detailed output")
            print("📈 Visualizations saved to results/figures/")
            print("🤖 Model saved to results/model_performance.pkl")
            sys.exit(0)
        else:
            logger.error("Pipeline failed")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()