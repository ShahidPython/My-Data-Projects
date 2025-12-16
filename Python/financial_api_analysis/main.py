#!/usr/bin/env python3
"""
Financial API Analysis Pipeline
Main orchestration script for end-to-end data processing and reporting.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import settings
from src.data_fetcher import EquityDataFetcher, FREDDataFetcher
from src.data_processor import FinancialDataProcessor
from src.visualization import FinancialVisualizer
from src.report_generator import PDFReportGenerator

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=settings.LOG_FORMAT,
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def fetch_data_phase(logger):
    """Phase 1: Fetch data from external APIs."""
    logger.info("=" * 60)
    logger.info("STARTING DATA FETCHING PHASE")
    logger.info("=" * 60)
    
    equity_fetcher = EquityDataFetcher()
    fred_fetcher = FREDDataFetcher()
    
    logger.info(f"Fetching equity data for symbols: {settings.YFINANCE_SYMBOLS}")
    equity_results = equity_fetcher.fetch_all_symbols()
    logger.info(f"Equity data fetched: {len(equity_results)} successful")
    
    logger.info(f"Fetching FRED data for series: {list(settings.FRED_SERIES.keys())}")
    fred_results = fred_fetcher.fetch_all_series()
    logger.info(f"FRED data fetched: {len(fred_results)} successful")
    
    return equity_results, fred_results

def process_data_phase(logger):
    """Phase 2: Process and analyze the fetched data."""
    logger.info("=" * 60)
    logger.info("STARTING DATA PROCESSING PHASE")
    logger.info("=" * 60)
    
    processor = FinancialDataProcessor()
    master_df, summary_stats = processor.process_all_data()
    
    if master_df.empty:
        logger.error("Master dataset is empty. Pipeline cannot continue.")
        return None, None
    
    logger.info(f"Data processing complete. Master dataset shape: {master_df.shape}")
    logger.info(f"Date range: {master_df['date'].min()} to {master_df['date'].max()}")
    logger.info(f"Symbols processed: {master_df['symbol'].unique().tolist()}")
    
    return master_df, summary_stats

def visualization_phase(logger, master_df):
    """Phase 3: Generate visualizations from processed data."""
    logger.info("=" * 60)
    logger.info("STARTING VISUALIZATION PHASE")
    logger.info("=" * 60)
    
    visualizer = FinancialVisualizer()
    chart_paths = visualizer.generate_all_visualizations(master_df)
    
    logger.info(f"Generated {len(chart_paths)} visualization files")
    for chart_name, path in chart_paths.items():
        if path:
            logger.info(f"  - {chart_name}: {path.name}")
    
    return chart_paths

def report_generation_phase(logger, summary_stats, chart_paths):
    """Phase 4: Generate comprehensive PDF report."""
    logger.info("=" * 60)
    logger.info("STARTING REPORT GENERATION PHASE")
    logger.info("=" * 60)
    
    report_generator = PDFReportGenerator(summary_stats, chart_paths)
    report_path = report_generator.generate_report()
    
    if report_path:
        logger.info(f"PDF report successfully generated: {report_path}")
        return report_path
    else:
        logger.error("Failed to generate PDF report")
        return None

def pipeline_summary(logger, start_time, report_path):
    """Display pipeline execution summary."""
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    
    logger.info("=" * 60)
    logger.info("PIPELINE EXECUTION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Total Execution Time: {execution_time:.2f} seconds")
    
    if report_path:
        logger.info(f"Final Output: {report_path}")
        logger.info("Pipeline completed successfully!")
    else:
        logger.error("Pipeline completed with errors")
    
    logger.info("=" * 60)

def main():
    """Main orchestration function."""
    start_time = datetime.now()
    logger = setup_logging()
    
    try:
        logger.info("=" * 60)
        logger.info("FINANCIAL API ANALYSIS PIPELINE")
        logger.info(f"Version: 1.0.0 | Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Phase 1: Data Fetching
        equity_results, fred_results = fetch_data_phase(logger)
        
        if not equity_results and not fred_results:
            logger.error("No data fetched. Exiting pipeline.")
            return False
        
        # Phase 2: Data Processing
        master_df, summary_stats = process_data_phase(logger)
        
        if master_df is None:
            return False
        
        # Phase 3: Visualization
        chart_paths = visualization_phase(logger, master_df)
        
        # Phase 4: Report Generation
        report_path = report_generation_phase(logger, summary_stats, chart_paths)
        
        # Final Summary
        pipeline_summary(logger, start_time, report_path)
        
        return report_path is not None
        
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        return False
    except Exception as e:
        logger.exception(f"Critical pipeline error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)