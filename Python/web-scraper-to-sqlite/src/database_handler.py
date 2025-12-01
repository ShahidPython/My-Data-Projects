import sqlite3
import logging
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Union, Tuple
import yaml
from pathlib import Path
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseHandler:
    """Professional database management for SQLite operations."""
    
    # DEFAULT SCHEMA MATCHING EXACT SCRAPER COLUMNS FROM YOUR OUTPUT
    DEFAULT_SCHEMA = {
        'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'title': 'TEXT NOT NULL',
        'price': 'REAL',
        'category': 'TEXT',
        'rating': 'REAL',
        'stock': 'TEXT',
        'description': 'TEXT',
        'sku': 'TEXT',
        'date_added': 'TEXT',
        '_container_index': 'INTEGER',
        '_scrape_timestamp': 'TEXT',
        'featured': 'INTEGER DEFAULT 0',
        'card_type': 'TEXT',
        'discounted': 'INTEGER DEFAULT 0',  # ADDED THIS
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    }
    
    def __init__(self, db_path: str = None, table_name: str = None, auto_create: bool = True):
        """Initialize database connection with optional schema creation.
        
        Args:
            db_path: Path to SQLite database file
            table_name: Target table name
            auto_create: Automatically create table if it doesn't exist
        """
        self.config = self._load_config()
        self.db_path = db_path or self.config['database']['db_path']
        self.table_name = table_name or self.config['database']['table_name']
        self.connection = None
        self.auto_create = auto_create
        
        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._initialize_database()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open('config.yaml', 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning("Configuration file 'config.yaml' not found. Using defaults.")
            return {
                'database': {
                    'db_path': 'data/scraped_data.db',
                    'table_name': 'scraped_records',
                    'max_retries': 3,
                    'timeout': 30
                }
            }
    
    def _initialize_database(self) -> None:
        """Initialize database connection."""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                timeout=30,
                check_same_thread=False
            )
            # Enable foreign keys and WAL mode for better performance
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.execute("PRAGMA journal_mode = WAL")
            
            logger.info(f"✅ Database connection established: {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def _table_exists(self, table_name: str = None) -> bool:
        """Check if table exists in database."""
        table_name = table_name or self.table_name
        query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
        """
        try:
            result = pd.read_sql_query(query, self.connection, params=(table_name,))
            return not result.empty
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False
    
    def _create_default_table(self, table_name: str = None) -> bool:
        """Create table with default schema."""
        table_name = table_name or self.table_name
        try:
            # Build CREATE TABLE query from default schema
            columns = []
            for col_name, col_type in self.DEFAULT_SCHEMA.items():
                columns.append(f"{col_name} {col_type}")
            
            create_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns)}
            );
            """
            
            cursor = self.connection.cursor()
            cursor.execute(create_query)
            self.connection.commit()
            
            # Create indexes for performance
            self._create_indexes(table_name)
            
            logger.info(f"✅ Default table '{table_name}' created successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Default table creation failed: {e}")
            self.connection.rollback()
            return False
    
    def ensure_table_exists(self, df: pd.DataFrame = None, table_name: str = None) -> bool:
        """Ensure table exists with proper schema.
        
        Args:
            df: DataFrame to check schema against (optional)
            table_name: Table to check
            
        Returns:
            bool: True if table exists and is compatible
        """
        table_name = table_name or self.table_name
        
        # Check if table exists
        if not self._table_exists(table_name):
            logger.info(f"Table '{table_name}' doesn't exist. Creating...")
            return self._create_default_table(table_name)
        
        logger.info(f"Table '{table_name}' already exists")
        return True
    
    def _create_indexes(self, table_name: str = None) -> None:
        """Create performance indexes on common query columns."""
        table_name = table_name or self.table_name
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_title ON {table_name}(title)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_price ON {table_name}(price)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_category ON {table_name}(category)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_sku ON {table_name}(sku)",
            f"CREATE INDEX IF NOT EXISTS idx_{table_name}_created_at ON {table_name}(created_at)",
        ]
        
        try:
            cursor = self.connection.cursor()
            for index_query in indexes:
                cursor.execute(index_query)
            self.connection.commit()
            logger.info(f"✅ Indexes created for table '{table_name}'")
        except sqlite3.Error as e:
            logger.warning(f"Index creation failed (non-critical): {e}")
            self.connection.rollback()
    
    def insert_data(self, df: pd.DataFrame, table_name: str = None, 
                   conflict_action: str = 'ignore') -> bool:
        """Insert DataFrame data into database with conflict handling.
        
        Args:
            df: Pandas DataFrame with cleaned data
            table_name: Target table name
            conflict_action: 'ignore', 'replace', or 'update'
            
        Returns:
            bool: True if successful
        """
        table_name = table_name or self.table_name
        
        if df.empty:
            logger.warning("⚠️  Attempted to insert empty DataFrame")
            return False
        
        # Ensure table exists with proper schema
        if not self.ensure_table_exists(df, table_name):
            logger.error(f"❌ Table validation failed for '{table_name}'")
            return False
        
        try:
            # Insert data
            df.to_sql(
                name=table_name,
                con=self.connection,
                if_exists='append',
                index=False
            )
            
            self.connection.commit()
            inserted_count = len(df)
            logger.info(f"✅ Successfully inserted {inserted_count} records into '{table_name}'")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Data insertion failed: {e}")
            self.connection.rollback()
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            return pd.read_sql_query(query, self.connection, params=params)
        except sqlite3.Error as e:
            logger.error(f"❌ Query execution failed: {e}")
            raise
    
    def get_table_info(self, table_name: str = None) -> pd.DataFrame:
        """Get schema information for specified table.
        
        Args:
            table_name: Table to inspect
            
        Returns:
            pd.DataFrame: Table schema information
        """
        table_name = table_name or self.table_name
        query = f"PRAGMA table_info({table_name})"
        return self.execute_query(query)
    
    def get_record_count(self, table_name: str = None) -> int:
        """Get total number of records in specified table.
        
        Args:
            table_name: Table to count
            
        Returns:
            int: Number of records
        """
        table_name = table_name or self.table_name
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        try:
            result = self.execute_query(query)
            return int(result.iloc[0]['count'])
        except Exception as e:
            logger.warning(f"Could not get record count: {e}")
            return 0
    
    def close_connection(self) -> None:
        """Safely close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Support context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when exiting context."""
        pass  # Don't close automatically, let user call close_connection()
