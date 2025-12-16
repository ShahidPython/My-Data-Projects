__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@domain.com"

from .scraper import WebScraper
from .data_cleaner import DataCleaner
from .database_handler import DatabaseHandler
from .cli import create_parser, execute_pipeline

__all__ = [
    "WebScraper",
    "DataCleaner", 
    "DatabaseHandler",
    "create_parser",
    "execute_pipeline"
]