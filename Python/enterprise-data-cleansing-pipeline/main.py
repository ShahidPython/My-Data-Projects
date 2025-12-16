#!/usr/bin/env python3
"""
Enterprise Data Cleaning Pipeline
Main entry point for the data cleaning and validation system
"""

import logging
import sys
from pathlib import Path

from src.orchestration.pipeline_manager import PipelineManager
from src.utils.logger import setup_logger

def main():
    logger = setup_logger(module_name=__name__)
    logger.setLevel(logging.DEBUG)
    
    logger.info("🚀 Starting Enterprise Data Cleaning Pipeline")
    
    input_file = "data/input/transactions_dirty.csv"
    output_dir = "data/output"
    config_file = "config/cleaning_rules.json"
    
    if not Path(input_file).exists():
        logger.error(f"❌ Input file not found: {input_file}")
        logger.info("📁 Creating sample data file...")
        
        sample_data = """transaction_id,customer_id,transaction_date,amount,product,region,email,phone
1001,CUST-1001,2024-01-15 10:30:00,150.00,Widget A,North America,john@company.com,+15551234567
1002,CUST-1002,2024-01-15 11:30:00,250.00,Widget B,Europe,jane@company.com,+441234567890
1003,CUST-1003,2024-01-15 12:30:00,350.00,Widget C,Asia,alice@company.com,+81312345678"""
        
        Path(input_file).parent.mkdir(exist_ok=True)
        with open(input_file, 'w') as f:
            f.write(sample_data)
        logger.info(f"✅ Created sample data: {input_file}")
    
    try:
        pipeline = PipelineManager(config_file)
        result = pipeline.execute_pipeline(input_file)
        
        if result['success']:
            logger.info("✅ Pipeline completed successfully!")
            logger.info(f"📊 Quality Score: {result['metrics'].get('quality_score', 0)}%")
            logger.info(f"📈 Rows Processed: {result['metrics'].get('transformation', {}).get('rows_final', 0)}")
            logger.info(f"⏱️  Duration: {result['metrics'].get('execution', {}).get('duration_seconds', 0)} seconds")
            
            report_path = pipeline.generate_report()
            logger.info(f"📄 Report generated: {report_path}")
            
            print("\n" + "="*50)
            print("🎉 PIPELINE SUCCESSFULLY COMPLETED!")
            print("="*50)
            print(f"📁 Input: {input_file}")
            print(f"📁 Output: {output_dir}")
            print(f"📊 Quality: {result['metrics'].get('quality_score', 0)}%")
            print(f"📈 Rows: {result['metrics'].get('transformation', {}).get('rows_final', 0)}")
            print(f"⏱️  Time: {result['metrics'].get('execution', {}).get('duration_seconds', 0)}s")
            print("="*50)
            
            sys.exit(0)
        else:
            logger.error("❌ Pipeline failed")
            if 'error' in result:
                logger.error(f"Error details: {result['error']}")
            
            print("\n" + "="*50)
            print("❌ PIPELINE FAILED")
            print("="*50)
            print("Check logs for details.")
            print("="*50)
            
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}", exc_info=True)
        print(f"\n💥 CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()