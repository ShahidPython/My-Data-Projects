import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pytest
import pandas as pd
import sqlite3
import tempfile
import shutil

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.database_handler import DatabaseHandler


class TestDatabaseHandler:
    """Comprehensive test suite for DatabaseHandler class."""
    
    @pytest.fixture
    def sample_config(self):
        """Provide sample configuration for testing."""
        return {
            'database': {
                'db_path': 'data/scraped_data.db',
                'table_name': 'scraped_records'
            }
        }
    
    @pytest.fixture
    def sample_dataframe(self):
        """Provide sample DataFrame for testing."""
        return pd.DataFrame({
            'title': ['Product One', 'Product Two', 'Product Three'],
            'price': [29.99, 39.99, 25.50],
            'description': ['First product', 'Second product', 'Third product'],
            'date': ['2023-01-15', '2023-02-20', '2023-03-10']
        })
    
    @pytest.fixture
    def temp_database(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, 'test.db')
        
        yield db_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def db_handler(self, sample_config, temp_database):
        """Create DatabaseHandler instance with mocked config."""
        config = sample_config.copy()
        config['database']['db_path'] = temp_database
        
        with patch('src.database_handler.DatabaseHandler._load_config', return_value=config):
            handler = DatabaseHandler()
            yield handler
            handler.close_connection()
    
    def test_initialization(self, db_handler, sample_config):
        """Test database handler initializes correctly."""
        assert db_handler.db_path == sample_config['database']['db_path']
        assert db_handler.connection is not None
        assert db_handler.logger is not None
    
    def test_initialization_with_custom_path(self, sample_config, temp_database):
        """Test initialization with custom database path."""
        with patch('src.database_handler.DatabaseHandler._load_config', return_value=sample_config):
            handler = DatabaseHandler(db_path=temp_database)
            assert handler.db_path == temp_database
            handler.close_connection()
    
    def test_table_creation(self, db_handler):
        """Test that table is created with correct schema."""
        # Verify table exists
        table_info = db_handler.get_table_info()
        
        expected_columns = ['id', 'title', 'price', 'description', 'date', 'created_at']
        actual_columns = table_info['name'].tolist()
        
        for col in expected_columns:
            assert col in actual_columns
        
        # Verify primary key
        id_column = table_info[table_info['name'] == 'id'].iloc[0]
        assert id_column['pk'] == 1  # Primary key
    
    def test_insert_data_success(self, db_handler, sample_dataframe):
        """Test successful data insertion."""
        initial_count = db_handler.get_record_count()
        
        success = db_handler.insert_data(sample_dataframe)
        
        assert success is True
        assert db_handler.get_record_count() == initial_count + len(sample_dataframe)
    
    def test_insert_data_empty_dataframe(self, db_handler):
        """Test insertion with empty DataFrame."""
        empty_df = pd.DataFrame()
        
        success = db_handler.insert_data(empty_df)
        
        assert success is False
    
    def test_insert_data_duplicate_handling(self, db_handler, sample_dataframe):
        """Test duplicate record handling with UNIQUE constraint."""
        # First insertion
        success1 = db_handler.insert_data(sample_dataframe)
        assert success1 is True
        
        # Second insertion of same data (should fail due to UNIQUE constraint)
        success2 = db_handler.insert_data(sample_dataframe)
        
        # Should still return True as individual insert failures are handled gracefully
        assert success2 is True
        
        # But no new records should be added due to UNIQUE constraint
        final_count = db_handler.get_record_count()
        assert final_count == len(sample_dataframe)  # Only original records
    
    def test_insert_data_with_custom_table(self, db_handler, sample_dataframe):
        """Test data insertion with custom table name."""
        custom_table = 'custom_records'
        
        success = db_handler.insert_data(sample_dataframe, table_name=custom_table)
        
        assert success is True
        assert db_handler.get_record_count(custom_table) == len(sample_dataframe)
    
    def test_execute_query_select(self, db_handler, sample_dataframe):
        """Test query execution with SELECT statement."""
        # Insert some data first
        db_handler.insert_data(sample_dataframe)
        
        query = "SELECT * FROM scraped_records WHERE price > 30"
        result_df = db_handler.execute_query(query)
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 1  # Only Product Two has price > 30
        assert result_df.iloc[0]['title'] == 'Product Two'
    
    def test_execute_query_with_parameters(self, db_handler, sample_dataframe):
        """Test parameterized query execution."""
        db_handler.insert_data(sample_dataframe)
        
        query = "SELECT * FROM scraped_records WHERE title = ?"
        params = ('Product One',)
        result_df = db_handler.execute_query(query, params)
        
        assert len(result_df) == 1
        assert result_df.iloc[0]['title'] == 'Product One'
    
    def test_execute_query_invalid_sql(self, db_handler):
        """Test error handling for invalid SQL."""
        with pytest.raises(sqlite3.Error):
            db_handler.execute_query("INVALID SQL STATEMENT")
    
    def test_get_table_info(self, db_handler):
        """Test table information retrieval."""
        table_info = db_handler.get_table_info()
        
        assert isinstance(table_info, pd.DataFrame)
        assert 'name' in table_info.columns
        assert 'type' in table_info.columns
        assert 'notnull' in table_info.columns
        assert 'pk' in table_info.columns
    
    def test_get_table_info_custom_table(self, db_handler):
        """Test table information for custom table."""
        # Create a custom table
        custom_table = 'test_table'
        create_query = """
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value REAL
        )
        """
        db_handler.execute_query(create_query)
        
        table_info = db_handler.get_table_info(custom_table)
        
        assert len(table_info) == 3
        expected_columns = ['id', 'name', 'value']
        actual_columns = table_info['name'].tolist()
        assert all(col in actual_columns for col in expected_columns)
    
    def test_get_record_count(self, db_handler, sample_dataframe):
        """Test record counting functionality."""
        initial_count = db_handler.get_record_count()
        assert initial_count == 0  # Initially empty
        
        db_handler.insert_data(sample_dataframe)
        
        final_count = db_handler.get_record_count()
        assert final_count == len(sample_dataframe)
    
    def test_get_record_count_custom_table(self, db_handler, sample_dataframe):
        """Test record counting for custom table."""
        custom_table = 'custom_table'
        
        # Create and populate custom table
        create_query = """
        CREATE TABLE IF NOT EXISTS custom_table (
            id INTEGER PRIMARY KEY,
            data TEXT
        )
        """
        db_handler.execute_query(create_query)
        
        custom_df = pd.DataFrame({'data': ['A', 'B', 'C']})
        db_handler.insert_data(custom_df, table_name=custom_table)
        
        count = db_handler.get_record_count(custom_table)
        assert count == len(custom_df)
    
    def test_context_manager(self, sample_config, temp_database):
        """Test context manager functionality."""
        config = sample_config.copy()
        config['database']['db_path'] = temp_database
        
        with patch('src.database_handler.DatabaseHandler._load_config', return_value=config):
            with DatabaseHandler() as handler:
                assert handler.connection is not None
                # Perform some operation
                count = handler.get_record_count()
                assert count == 0
            
            # Connection should be closed after context exit
            assert handler.connection is None
    
    def test_close_connection(self, db_handler):
        """Test connection closing."""
        assert db_handler.connection is not None
        
        db_handler.close_connection()
        
        assert db_handler.connection is None
    
    def test_database_rollback_on_error(self, db_handler, sample_dataframe):
        """Test transaction rollback on insertion error."""
        # Create a situation that causes insertion failure
        invalid_df = pd.DataFrame({
            'invalid_column': ['data']  # Column doesn't exist in table
        })
        
        success = db_handler.insert_data(invalid_df)
        
        assert success is False
        # Database should still be in consistent state
        assert db_handler.get_record_count() == 0
    
    def test_config_file_not_found(self):
        """Test proper error handling when config file is missing."""
        with patch('src.database_handler.open', side_effect=FileNotFoundError()):
            with pytest.raises(Exception, match="Configuration file 'config.yaml' not found"):
                DatabaseHandler()
    
    def test_database_connection_failure(self, sample_config):
        """Test handling of database connection failures."""
        with patch('src.database_handler.sqlite3.connect', side_effect=sqlite3.Error("Connection failed")):
            with patch('src.database_handler.DatabaseHandler._load_config', return_value=sample_config):
                with pytest.raises(sqlite3.Error):
                    DatabaseHandler()
    
    def test_large_dataset_insertion(self, db_handler):
        """Test insertion of large dataset."""
        # Create a larger dataset
        large_df = pd.DataFrame({
            'title': [f'Product {i}' for i in range(100)],
            'price': [i * 10.0 for i in range(100)],
            'description': [f'Description {i}' for i in range(100)],
            'date': ['2023-01-01' for _ in range(100)]
        })
        
        success = db_handler.insert_data(large_df)
        
        assert success is True
        assert db_handler.get_record_count() == 100
    
    def test_data_integrity(self, db_handler, sample_dataframe):
        """Test data integrity after insertion."""
        # Insert data
        db_handler.insert_data(sample_dataframe)
        
        # Retrieve and verify data
        query = "SELECT * FROM scraped_records ORDER BY id"
        result_df = db_handler.execute_query(query)
        
        assert len(result_df) == len(sample_dataframe)
        
        # Verify data matches
        for i, (_, original_row) in enumerate(sample_dataframe.iterrows()):
            retrieved_row = result_df.iloc[i]
            assert retrieved_row['title'] == original_row['title']
            assert retrieved_row['price'] == original_row['price']
            assert retrieved_row['description'] == original_row['description']
            assert retrieved_row['date'] == original_row['date']
    
    def test_auto_increment_primary_key(self, db_handler, sample_dataframe):
        """Test auto-increment primary key functionality."""
        db_handler.insert_data(sample_dataframe)
        
        result_df = db_handler.execute_query("SELECT id FROM scraped_records ORDER BY id")
        
        # IDs should be sequential starting from 1
        expected_ids = [1, 2, 3]
        actual_ids = result_df['id'].tolist()
        
        assert actual_ids == expected_ids
    
    def test_timestamp_auto_population(self, db_handler, sample_dataframe):
        """Test automatic timestamp population."""
        db_handler.insert_data(sample_dataframe)
        
        result_df = db_handler.execute_query("SELECT created_at FROM scraped_records")
        
        # All records should have created_at timestamps
        assert result_df['created_at'].notna().all()
        # Should be recent timestamps (within last minute)
        timestamps = pd.to_datetime(result_df['created_at'])
        time_diff = (pd.Timestamp.now() - timestamps.max()).total_seconds()
        assert time_diff < 60  # Within last minute
    
    @patch('src.database_handler.logging.Logger.error')
    def test_error_logging(self, mock_log, db_handler):
        """Test that errors are properly logged."""
        # Force an error
        with pytest.raises(sqlite3.Error):
            db_handler.execute_query("INVALID SQL")
        
        # Verify error was logged
        assert mock_log.called
    
    def test_multiple_operations_in_transaction(self, db_handler):
        """Test multiple operations within a transaction."""
        df1 = pd.DataFrame({'title': ['First'], 'price': [10.0], 'description': ['Test'], 'date': ['2023-01-01']})
        df2 = pd.DataFrame({'title': ['Second'], 'price': [20.0], 'description': ['Test'], 'date': ['2023-01-02']})
        
        # Both insertions should succeed
        success1 = db_handler.insert_data(df1)
        success2 = db_handler.insert_data(df2)
        
        assert success1 is True
        assert success2 is True
        assert db_handler.get_record_count() == 2
    
    def test_database_isolation(self, sample_config, temp_database):
        """Test that database instances are isolated."""
        config = sample_config.copy()
        config['database']['db_path'] = temp_database
        
        with patch('src.database_handler.DatabaseHandler._load_config', return_value=config):
            # First handler
            handler1 = DatabaseHandler()
            df1 = pd.DataFrame({'title': ['Handler1'], 'price': [10.0], 'description': ['Test'], 'date': ['2023-01-01']})
            handler1.insert_data(df1)
            handler1.close_connection()
            
            # Second handler should see data from first
            handler2 = DatabaseHandler()
            count = handler2.get_record_count()
            handler2.close_connection()
            
            assert count == 1