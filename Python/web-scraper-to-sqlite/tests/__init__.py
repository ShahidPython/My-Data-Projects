__version__ = "1.0.0"
__author__ = "Your Name"

# Import test modules to make them easily accessible
from .test_scraper import TestWebScraper
from .test_data_cleaner import TestDataCleaner
from .test_database_handler import TestDatabaseHandler

__all__ = [
    "TestWebScraper",
    "TestDataCleaner", 
    "TestDatabaseHandler"
]