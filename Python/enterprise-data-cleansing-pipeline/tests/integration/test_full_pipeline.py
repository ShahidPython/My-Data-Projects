import pytest
import pandas as pd
import tempfile
import json
from pathlib import Path
from src.orchestration.pipeline_manager import PipelineManager

class TestFullPipeline:
    def setup_method(self):
        self.pipeline = PipelineManager()
        
    def create_test_csv(self, content: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            return f.name
    
    def test_pipeline_with_clean_data(self):
        csv_content = """transaction_id,customer_id,transaction_date,amount,product,region,email,phone
1001,CUST-1001,2024-01-15 10:30:00,150.00,Widget A,North America,john@company.com,+15551234567
1002,CUST-1002,2024-01-15 11:30:00,250.00,Widget B,Europe,jane@company.com,+441234567890
1003,CUST-1003,2024-01-15 12:30:00,350.00,Widget C,Asia,alice@company.com,+81312345678"""
        
        temp_file = self.create_test_csv(csv_content)
        
        try:
            result = self.pipeline.execute_pipeline(temp_file)
            
            assert result['success'] == True
            assert 'metrics' in result
            assert 'output_paths' in result
            
            metrics = result['metrics']
            assert metrics['quality']['overall_score'] >= 95.0
            assert metrics['transformation']['rows_final'] == 3
            
            output_paths = result['output_paths']
            assert Path(output_paths['parquet']).exists()
            assert Path(output_paths['summary']).exists()
            
        finally:
            Path(temp_file).unlink()
    
    def test_pipeline_with_dirty_data(self):
        csv_content = """transaction_id,customer_id,transaction_date,amount,product,region,email,phone
1001,CUST-1001,15/01/2024 10:30,150.00,Widget A,NA,john@company,+15551234567
1002,INVALID,2024-01-15 11:30:00,-50.00,Widget B,Europe,not-email,123
1003,CUST-1003,2024-01-15 12:30:00,1000000.00,Widget C,Asia,alice@company.com,+81312345678
1004,CUST-1004,2024-01-15 13:30:00,,Widget D,Australia,bob@company.com,
1001,CUST-1001,2024-01-15 14:30:00,200.00,Widget A,North America,john@company.com,+15551234567"""
        
        temp_file = self.create_test_csv(csv_content)
        
        try:
            result = self.pipeline.execute_pipeline(temp_file)
            
            metrics = result['metrics']
            
            assert metrics['transformation']['invalid_transaction_ids'] >= 0
            assert metrics['transformation']['invalid_customer_ids'] >= 1
            assert metrics['transformation']['duplicates_removed'] >= 1
            
            if result['success']:
                assert metrics['quality']['overall_score'] >= 0
            else:
                assert 'error' in result
            
        finally:
            Path(temp_file).unlink()
    
    def test_pipeline_with_missing_required_columns(self):
        csv_content = """customer_id,amount
CUST-1001,150.00
CUST-1002,250.00"""
        
        temp_file = self.create_test_csv(csv_content)
        
        try:
            result = self.pipeline.execute_pipeline(temp_file)
            
            assert result['success'] == False
            assert 'error' in result
            
        finally:
            Path(temp_file).unlink()
    
    def test_pipeline_with_empty_file(self):
        csv_content = """transaction_id,customer_id,transaction_date,amount,product,region,email,phone"""
        
        temp_file = self.create_test_csv(csv_content)
        
        try:
            result = self.pipeline.execute_pipeline(temp_file)
            
            metrics = result['metrics']
            assert metrics['transformation']['rows_final'] == 0
            
        finally:
            Path(temp_file).unlink()
    
    def test_pipeline_with_large_dataset(self):
        records = []
        for i in range(1000):
            records.append(f"{100000 + i},CUST-{100000 + i},2024-01-15 10:30:00,{i * 10}.00,Widget,Region,test{i}@company.com,+1555000{i:04d}")
        
        csv_content = "transaction_id,customer_id,transaction_date,amount,product,region,email,phone\n" + "\n".join(records)
        
        temp_file = self.create_test_csv(csv_content)
        
        try:
            result = self.pipeline.execute_pipeline(temp_file)
            
            assert result['success'] == True
            metrics = result['metrics']
            assert metrics['transformation']['rows_final'] == 1000
            assert metrics['execution']['duration_seconds'] > 0
            
        finally:
            Path(temp_file).unlink()
    
    def test_pipeline_error_handling(self):
        result = self.pipeline.execute_pipeline("non_existent_file.csv")
        
        assert result['success'] == False
        assert 'error' in result
        assert 'error_file' in result['error']
    
    def test_pipeline_report_generation(self):
        csv_content = """transaction_id,customer_id,transaction_date,amount,product,region,email,phone
1001,CUST-1001,2024-01-15 10:30:00,150.00,Widget A,North America,john@company.com,+15551234567"""
        
        temp_file = self.create_test_csv(csv_content)
        
        try:
            result = self.pipeline.execute_pipeline(temp_file)
            
            if result['success']:
                report_path = self.pipeline.generate_report()
                assert Path(report_path).exists()
                
                with open(report_path, 'r') as f:
                    report_data = json.load(f)
                
                assert 'pipeline_id' in report_data.get('execution', {})
                assert 'quality' in report_data
                
        finally:
            Path(temp_file).unlink()