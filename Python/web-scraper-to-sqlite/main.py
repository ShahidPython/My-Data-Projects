import logging
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Import project modules
from src.scraper import WebScraper, ScrapeResult
from src.data_cleaner import DataCleaner
from src.database_handler import DatabaseHandler
from src.cli import create_parser, setup_logging


class DataPipeline:
    """Production-grade data pipeline with monitoring and error handling."""
    
    def __init__(self, args):
        """Initialize pipeline with configuration."""
        self.args = args
        self.logger = logging.getLogger(__name__)
        self.pipeline_stats = {
            'start_time': datetime.now().isoformat(),
            'success': False,
            'phases': {},
            'records_processed': 0,
            'duration_seconds': 0
        }
        self._setup_directories()
    
    def _setup_directories(self) -> None:
        """Ensure required directories exist."""
        directories = ['data', 'data/input', 'data/output', 'logs', 'data/cache']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def run(self) -> bool:
        """Execute the complete ETL pipeline."""
        try:
            self.logger.info("🚀 INITIATING DATA PIPELINE")
            self.logger.info("=" * 60)
            
            # Display configuration
            self._log_configuration()
            
            # PHASE 1: EXTRACTION
            extraction_result = self._extract_data()
            if not extraction_result:
                return False
            
            # PHASE 2: TRANSFORMATION
            transformation_result = self._transform_data(extraction_result)
            if transformation_result is None:
                return False
            
            # PHASE 3: LOADING
            loading_result = self._load_data(transformation_result)
            if not loading_result:
                return False
            
            # Generate analytics report
            self._generate_analytics()
            
            # Pipeline success
            self.pipeline_stats['success'] = True
            self.pipeline_stats['records_processed'] = len(transformation_result)
            
            self.logger.info("=" * 60)
            self.logger.info("✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
            
            return True
            
        except KeyboardInterrupt:
            self.logger.warning("⚠️  Pipeline interrupted by user")
            return False
            
        except Exception as e:
            self.logger.error(f"💥 PIPELINE FAILURE: {str(e)}")
            
            if self.args.verbose:
                import traceback
                self.logger.debug(f"Exception traceback:\n{traceback.format_exc()}")
            
            return False
            
        finally:
            self._log_final_stats()
    
    def _log_configuration(self) -> None:
        """Log pipeline configuration."""
        config_info = []
        
        if self.args.url:
            config_info.append(f"Target URL: {self.args.url}")
        if self.args.table:
            config_info.append(f"Target Table: {self.args.table}")
        if self.args.limit:
            config_info.append(f"Record Limit: {self.args.limit}")
        if self.args.output:
            config_info.append(f"Database Path: {self.args.output}")
        
        config_info.append(f"Verbose Mode: {self.args.verbose}")
        config_info.append(f"Dry Run: {self.args.dry_run}")
        
        for info in config_info:
            self.logger.info(info)
        
        self.logger.info("-" * 60)
    
    def _extract_data(self) -> Optional[ScrapeResult]:
        """Extract data from source."""
        self.logger.info("📥 PHASE 1: EXTRACTING DATA FROM SOURCE")
        
        phase_start = time.time()
        
        try:
            # Initialize scraper
            scraper = WebScraper(
                target_url=self.args.url,
                cache_enabled=True,
                max_concurrent=5
            )
            
            # Test selectors in verbose mode
            if self.args.verbose:
                selector_test = scraper.test_selectors()
                if selector_test.get('valid'):
                    self.logger.debug(f"Selector validation: {selector_test['container_count']} containers found")
                else:
                    self.logger.warning(f"Selector issues: {selector_test.get('warnings', [])}")
            
            # Scrape data - USING SYNC WRAPPER TO FIX ASYNC ISSUE
            result = scraper.scrape_sync(limit=self.args.limit)
            
            # Log extraction results
            if result.stats['success']:
                self.logger.info(f"✅ Extraction successful: {result.stats['records_extracted']} records")
                self.logger.debug(f"Extraction rate: {result.stats['extraction_rate']:.1f} records/sec")
                
                # Log sample data in verbose mode
                if self.args.verbose and result.data:
                    self.logger.debug(f"Sample record: {json.dumps(result.data[0], indent=2)}")
                
                # Save phase stats
                self.pipeline_stats['phases']['extraction'] = {
                    'duration': round(time.time() - phase_start, 2),
                    'records': result.stats['records_extracted'],
                    'success_rate': result.stats['success_rate'],
                    'errors': result.stats['errors_count']
                }
                
                return result
            else:
                self.logger.error(f"❌ Extraction failed: {result.stats.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Extraction phase failed: {str(e)}")
            return None
    
    def _transform_data(self, scrape_result: ScrapeResult) -> Optional[Any]:
        """Transform and clean extracted data."""
        self.logger.info("🔄 PHASE 2: TRANSFORMING AND CLEANING DATA")
        
        phase_start = time.time()
        
        try:
            # Initialize cleaner
            cleaner = DataCleaner()
            
            # Clean data
            cleaned_data = cleaner.clean_data(scrape_result.data)
            
            if cleaned_data.empty:
                self.logger.error("❌ Transformation resulted in empty dataset")
                return None
            
            # Get cleaning report
            cleaning_report = cleaner.get_cleaning_report()
            
            # Log transformation results
            retention_rate = cleaning_report['retention_rate']
            records_lost = cleaning_report['cleaning_stats']['records_lost']
            
            self.logger.info(f"✅ Transformation complete: {len(cleaned_data)} records")
            self.logger.info(f"📊 Data quality: {retention_rate:.1f}% retention ({records_lost} records cleaned)")
            
            # Show cleaning summary
            if hasattr(cleaner, '_log_cleaning_summary'):
                cleaner._log_cleaning_summary()
            
            # Display sample in verbose mode
            if self.args.verbose and not cleaned_data.empty:
                self.logger.debug("Sample of cleaned data:")
                sample = cleaned_data.head(3).to_dict(orient='records')
                for i, record in enumerate(sample):
                    self.logger.debug(f"  Record {i+1}: {json.dumps(record, default=str)}")
            
            # Save phase stats
            self.pipeline_stats['phases']['transformation'] = {
                'duration': round(time.time() - phase_start, 2),
                'records_input': cleaning_report['cleaning_stats']['initial_count'],
                'records_output': cleaning_report['cleaning_stats']['final_count'],
                'retention_rate': retention_rate,
                'records_lost': records_lost
            }
            
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"❌ Transformation phase failed: {str(e)}")
            return None
    
    def _load_data(self, cleaned_data) -> bool:
        """Load cleaned data into database."""
        
        if self.args.dry_run:
            self.logger.info("🛑 DRY RUN - Skipping database loading")
            self.logger.info(f"📊 Data ready for loading: {len(cleaned_data)} records")
            
            # Show sample output
            if not cleaned_data.empty:
                self.logger.info("Sample output (first 5 records):")
                print(cleaned_data.head().to_string())
            
            # Simulate phase stats
            self.pipeline_stats['phases']['loading'] = {
                'duration': 0,
                'records': len(cleaned_data),
                'mode': 'dry_run',
                'database': 'none'
            }
            
            return True
        
        self.logger.info("💾 PHASE 3: LOADING DATA INTO DATABASE")
        
        phase_start = time.time()
        
        db = None
        try:
            # Initialize database handler MANUALLY (not with context manager)
            db = DatabaseHandler(db_path=self.args.output)
            
            # Get table name
            table_name = self.args.table or db.config['database']['table_name']
            
            # Ensure table exists with proper schema BEFORE getting count
            if not db.ensure_table_exists(cleaned_data, table_name):
                self.logger.error(f"❌ Failed to ensure table '{table_name}' exists")
                return False
            
            # Get initial count
            initial_count = db.get_record_count(table_name)
            
            # Insert data
            success = db.insert_data(cleaned_data, table_name=table_name)
            
            if success:
                # Get final statistics
                final_count = db.get_record_count(table_name)
                new_records = final_count - initial_count
                
                self.logger.info(f"✅ Loading complete: {new_records} new records added")
                self.logger.info(f"📊 Database status: {final_count} total records in '{table_name}'")
                
                # Show table info in verbose mode
                if self.args.verbose:
                    table_info = db.get_table_info(table_name)
                    self.logger.debug(f"Table schema: {len(table_info)} columns")
                
                # Save phase stats
                self.pipeline_stats['phases']['loading'] = {
                    'duration': round(time.time() - phase_start, 2),
                    'records': new_records,
                    'initial_count': initial_count,
                    'final_count': final_count,
                    'database': self.args.output or 'default'
                }
                
                return True
            else:
                self.logger.error("❌ Loading phase failed: Database insertion failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Loading phase failed: {str(e)}")
            return False
            
        finally:
            # Always close database connection
            if db:
                db.close_connection()
    
    def _generate_analytics(self) -> None:
        """Generate basic analytics and reports."""
        if self.args.verbose or self.args.dry_run:
            self.logger.info("📈 GENERATING ANALYTICS REPORT")
            
            try:
                # Initialize database for analytics
                db = DatabaseHandler(db_path=self.args.output)
                
                try:
                    table_name = self.args.table or db.config['database']['table_name']
                    
                    # Get basic statistics
                    query = f"""
                    SELECT 
                        COUNT(*) as total_records,
                        ROUND(AVG(price), 2) as avg_price,
                        MIN(price) as min_price,
                        MAX(price) as max_price,
                        COUNT(DISTINCT category) as unique_categories
                    FROM {table_name}
                    WHERE price IS NOT NULL
                    """
                    
                    stats = db.execute_query(query)
                    
                    if not stats.empty:
                        self.logger.info("📊 DATABASE ANALYTICS:")
                        for col in stats.columns:
                            value = stats.iloc[0][col]
                            self.logger.info(f"  • {col.replace('_', ' ').title()}: {value}")
                finally:
                    db.close_connection()
            
            except Exception as e:
                self.logger.debug(f"Analytics generation skipped: {str(e)}")
    
    def _log_final_stats(self) -> None:
        """Log final pipeline statistics."""
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.pipeline_stats['start_time'])
        duration = (end_time - start_time).total_seconds()
        
        self.pipeline_stats['duration_seconds'] = round(duration, 2)
        self.pipeline_stats['end_time'] = end_time.isoformat()
        
        self.logger.info(f"⏱️  Total execution time: {duration:.2f} seconds")
        
        # Log phase breakdown
        if 'phases' in self.pipeline_stats:
            self.logger.info("📊 Phase breakdown:")
            for phase, stats in self.pipeline_stats['phases'].items():
                duration = stats.get('duration', 0)
                records = stats.get('records', 0)
                self.logger.info(f"  • {phase.title()}: {duration}s, {records} records")
        
        # Final status
        if self.pipeline_stats['success']:
            self.logger.info("🏁 PIPELINE STATUS: SUCCESS")
        else:
            self.logger.error("🏁 PIPELINE STATUS: FAILED")
        
        self.logger.info("=" * 60)
        
        # Save pipeline stats to file
        self._save_pipeline_stats()
    
    def _save_pipeline_stats(self) -> None:
        """Save pipeline statistics to JSON file for monitoring."""
        try:
            stats_file = Path("logs/pipeline_stats.json")
            
            # Load existing stats or create new list
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    all_stats = json.load(f)
            else:
                all_stats = []
            
            # Add current run
            all_stats.append(self.pipeline_stats)
            
            # Keep only last 100 runs
            if len(all_stats) > 100:
                all_stats = all_stats[-100:]
            
            # Save to file
            with open(stats_file, 'w') as f:
                json.dump(all_stats, f, indent=2, default=str)
            
            self.logger.debug(f"Pipeline statistics saved to {stats_file}")
            
        except Exception as e:
            self.logger.debug(f"Failed to save pipeline stats: {str(e)}")


def main() -> None:
    """Main entry point for the application."""
    
    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Welcome message
    logger.info("=" * 60)
    logger.info("WEB SCRAPER TO SQLITE DB - PROFESSIONAL DATA PIPELINE")
    logger.info("=" * 60)
    
    # Create and run pipeline
    pipeline = DataPipeline(args)
    success = pipeline.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()