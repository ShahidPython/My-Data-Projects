import argparse
import sys
import logging
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    
    parser = argparse.ArgumentParser(
        description="Web Scraper to SQLite DB - Professional Data Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url https://example.com/products
  %(prog)s --url ./data/input/example.html --output data/products.db
  %(prog)s --url https://example.com --limit 50 --verbose --dry-run
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--url',
        type=str,
        default='./data/input/example.html',  # ADDED DEFAULT
        help='Target URL or file path (default: ./data/input/example.html)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/scraped_data.db',
        help='Output SQLite database path (default: data/scraped_data.db)'
    )
    
    parser.add_argument(
        '--table', '-t',
        type=str,
        help='Target table name (default: from config)'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of records to scrape'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='Run pipeline without saving to database'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.yaml',
        help='Configuration file path (default: config.yaml)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Web Scraper to SQLite DB v1.0.0'
    )
    
    return parser


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level."""
    
    log_level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)


def execute_pipeline(args) -> bool:
    """Execute the pipeline with given arguments."""
    from main import DataPipeline
    
    try:
        pipeline = DataPipeline(args)
        return pipeline.run()
    except KeyboardInterrupt:
        logging.info("Pipeline interrupted by user")
        return False
    except Exception as e:
        logging.error(f"Pipeline execution failed: {e}")
        return False


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    success = execute_pipeline(args)
    sys.exit(0 if success else 1)