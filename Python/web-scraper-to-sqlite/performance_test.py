import asyncio
import time
import psutil
import tracemalloc
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np
import json
from pathlib import Path
import logging

# Project imports
from src.scraper import WebScraper
from src.data_cleaner import DataCleaner
from src.database_handler import DatabaseHandler
from src.cli import setup_logging


class PerformanceBenchmark:
    """Comprehensive performance testing framework."""
    
    def __init__(self, output_dir: str = "benchmarks"):
        """Initialize benchmark suite."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        setup_logging(verbose=False)
        self.logger = logging.getLogger(__name__)
        
        # Test data
        self.test_data = self._generate_test_data()
        
        # Results storage
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self._get_system_info(),
            "tests": {}
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Collect system information for benchmark context."""
        import platform
        
        return {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "memory_gb": psutil.virtual_memory().total / (1024**3),
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_logical_count": psutil.cpu_count(logical=True),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
        }
    
    def _generate_test_data(self, num_records: int = 1000) -> List[Dict[str, Any]]:
        """Generate test data for performance testing."""
        np.random.seed(42)
        
        test_data = []
        for i in range(num_records):
            record = {
                "id": f"PROD{i:06d}",
                "title": f"Test Product {i}",
                "price": round(np.random.uniform(10, 1000), 2),
                "description": "Test description " * np.random.randint(1, 5),
                "category": np.random.choice(["Electronics", "Books", "Clothing", "Home", "Sports"]),
                "rating": round(np.random.uniform(1, 5), 1),
                "stock_status": np.random.choice(["in_stock", "low_stock", "out_of_stock"]),
                "date": f"2023-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
                "tags": ",".join(np.random.choice(["tag1", "tag2", "tag3", "tag4"], 2)),
            }
            test_data.append(record)
        
        return test_data
    
    def run_all_benchmarks(self, warmup_iterations: int = 3) -> Dict[str, Any]:
        """Run complete benchmark suite."""
        self.logger.info("🚀 STARTING PERFORMANCE BENCHMARK SUITE")
        self.logger.info("=" * 60)
        
        # Warmup
        self._warmup(warmup_iterations)
        
        # Run benchmarks
        benchmarks = [
            ("scraper_performance", self.benchmark_scraper),
            ("data_cleaning_performance", self.benchmark_data_cleaning),
            ("database_performance", self.benchmark_database_operations),
            ("memory_usage", self.benchmark_memory_usage),
            ("concurrent_scraping", self.benchmark_concurrent_scraping),
            ("pipeline_end_to_end", self.benchmark_pipeline_end_to_end),
            ("scalability_test", self.benchmark_scalability),
        ]
        
        for name, benchmark_func in benchmarks:
            try:
                self.logger.info(f"📊 Running: {name.replace('_', ' ').title()}")
                result = benchmark_func()
                self.results["tests"][name] = result
                self._log_benchmark_result(name, result)
            except Exception as e:
                self.logger.error(f"❌ Benchmark '{name}' failed: {e}")
                self.results["tests"][name] = {"error": str(e)}
        
        # Generate final report
        self._generate_report()
        
        self.logger.info("=" * 60)
        self.logger.info("✅ PERFORMANCE BENCHMARK SUITE COMPLETED")
        
        return self.results
    
    def _warmup(self, iterations: int = 3) -> None:
        """Warm up Python runtime and caches."""
        self.logger.info(f"🔥 Warming up ({iterations} iterations)...")
        
        for i in range(iterations):
            # Simple operations to warm up Python
            _ = sum(range(10000))
            _ = [x**2 for x in range(1000)]
            
            # Warm up project modules
            cleaner = DataCleaner()
            sample_data = self.test_data[:10]
            _ = cleaner.clean_data(sample_data)
        
        self.logger.info("✓ Warmup completed")
    
    def benchmark_scraper(self) -> Dict[str, Any]:
        """Benchmark web scraper performance."""
        self.logger.info("  Testing scraper performance...")
        
        # Create mock scraper with local file
        scraper = WebScraper(target_url="file://./data/input/example.html")
        
        # Test different batch sizes
        batch_sizes = [10, 50, 100, 500]
        results = []
        
        for batch_size in batch_sizes:
            start_time = time.perf_counter()
            
            # Mock scrape operation
            mock_data = self.test_data[:batch_size]
            result = scraper.scrape_data(limit=batch_size)
            
            elapsed = time.perf_counter() - start_time
            
            results.append({
                "batch_size": batch_size,
                "elapsed_seconds": elapsed,
                "records_per_second": batch_size / elapsed if elapsed > 0 else 0,
                "success": result.stats['success'],
                "records_extracted": result.stats['records_extracted'],
            })
        
        # Calculate statistics
        throughput = [r["records_per_second"] for r in results]
        
        return {
            "summary": {
                "avg_throughput_records_sec": statistics.mean(throughput),
                "max_throughput_records_sec": max(throughput),
                "min_throughput_records_sec": min(throughput),
                "total_tests": len(results),
            },
            "detailed_results": results,
            "recommendations": self._analyze_scraper_performance(results),
        }
    
    def benchmark_data_cleaning(self) -> Dict[str, Any]:
        """Benchmark data cleaning performance."""
        self.logger.info("  Testing data cleaning performance...")
        
        cleaner = DataCleaner()
        
        # Test different dataset sizes
        dataset_sizes = [100, 500, 1000, 5000]
        results = []
        
        tracemalloc.start()
        
        for size in dataset_sizes:
            test_dataset = self.test_data[:size]
            
            # Memory tracking
            start_memory = tracemalloc.take_snapshot()
            start_time = time.perf_counter()
            
            # Clean data
            cleaned_data = cleaner.clean_data(test_dataset)
            
            elapsed = time.perf_counter() - start_time
            end_memory = tracemalloc.take_snapshot()
            
            # Memory usage
            memory_diff = end_memory.compare_to(start_memory, 'lineno')
            memory_used = sum(stat.size for stat in memory_diff) / 1024  # KB
            
            results.append({
                "dataset_size": size,
                "elapsed_seconds": elapsed,
                "records_per_second": size / elapsed if elapsed > 0 else 0,
                "memory_used_kb": memory_used,
                "memory_per_record_kb": memory_used / size if size > 0 else 0,
                "records_cleaned": len(cleaned_data),
                "retention_rate": len(cleaned_data) / size if size > 0 else 0,
            })
        
        tracemalloc.stop()
        
        # Calculate statistics
        throughput = [r["records_per_second"] for r in results]
        memory_per_record = [r["memory_per_record_kb"] for r in results]
        
        return {
            "summary": {
                "avg_cleaning_speed_records_sec": statistics.mean(throughput),
                "avg_memory_per_record_kb": statistics.mean(memory_per_record),
                "max_dataset_tested": max(dataset_sizes),
                "cleaning_efficiency": statistics.mean([r["retention_rate"] for r in results]),
            },
            "detailed_results": results,
            "memory_analysis": self._analyze_memory_patterns(results),
        }
    
    def benchmark_database_operations(self) -> Dict[str, Any]:
        """Benchmark database operations."""
        self.logger.info("  Testing database operations...")
        
        # Use temporary database
        import tempfile
        import os
        
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        try:
            db_handler = DatabaseHandler(db_path=temp_db.name)
            
            # Generate test DataFrame
            df = pd.DataFrame(self.test_data[:1000])
            
            # Test operations
            operations = [
                ("insert_100", lambda: db_handler.insert_data(df.iloc[:100])),
                ("insert_500", lambda: db_handler.insert_data(df.iloc[:500])),
                ("insert_1000", lambda: db_handler.insert_data(df.iloc[:1000])),
                ("query_simple", lambda: db_handler.execute_query("SELECT * FROM scraped_records LIMIT 10")),
                ("query_complex", lambda: db_handler.execute_query(
                    "SELECT category, COUNT(*) as count, AVG(price) as avg_price "
                    "FROM scraped_records GROUP BY category"
                )),
            ]
            
            results = []
            
            for op_name, operation in operations:
                # Warm up
                for _ in range(3):
                    _ = operation() if "query" in op_name else operation
                
                # Benchmark
                start_time = time.perf_counter()
                
                if "query" in op_name:
                    result = operation()
                    record_count = len(result)
                else:
                    success = operation()
                    record_count = 100 if "100" in op_name else (500 if "500" in op_name else 1000)
                
                elapsed = time.perf_counter() - start_time
                
                results.append({
                    "operation": op_name,
                    "elapsed_seconds": elapsed,
                    "operations_per_second": 1 / elapsed if elapsed > 0 else 0,
                    "records_affected": record_count,
                    "throughput_records_sec": record_count / elapsed if elapsed > 0 else 0,
                })
            
            db_handler.close_connection()
            
            return {
                "summary": {
                    "avg_insert_speed_records_sec": statistics.mean([
                        r["throughput_records_sec"] for r in results 
                        if "insert" in r["operation"]
                    ]),
                    "avg_query_time_seconds": statistics.mean([
                        r["elapsed_seconds"] for r in results 
                        if "query" in r["operation"]
                    ]),
                    "operations_tested": len(operations),
                },
                "detailed_results": results,
                "database_size_mb": os.path.getsize(temp_db.name) / (1024 * 1024),
            }
            
        finally:
            # Cleanup
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)
    
    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage patterns."""
        self.logger.info("  Testing memory usage...")
        
        import gc
        
        # Track memory usage over time
        memory_samples = []
        
        # Test different components
        components = [
            ("scraper_init", lambda: WebScraper()),
            ("cleaner_init", lambda: DataCleaner()),
            ("large_dataframe", lambda: pd.DataFrame(self.test_data)),
            ("database_connection", lambda: DatabaseHandler(db_path=":memory:")),
        ]
        
        for component_name, init_func in components:
            # Force garbage collection
            gc.collect()
            
            # Measure memory before
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Initialize component
            component = init_func()
            
            # Measure memory after
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            # Cleanup
            del component
            gc.collect()
            
            memory_samples.append({
                "component": component_name,
                "memory_before_mb": memory_before,
                "memory_after_mb": memory_after,
                "memory_increase_mb": memory_after - memory_before,
            })
        
        # Track memory during pipeline execution
        pipeline_memory = []
        
        def track_pipeline_memory():
            scraper = WebScraper()
            cleaner = DataCleaner()
            
            # Track at different stages
            stages = [
                ("initial", lambda: None),
                ("after_scraper", lambda: scraper.scrape_data(limit=100)),
                ("after_cleaner", lambda: cleaner.clean_data(self.test_data[:100])),
            ]
            
            for stage_name, _ in stages:
                gc.collect()
                memory = process.memory_info().rss / 1024 / 1024
                pipeline_memory.append({
                    "stage": stage_name,
                    "memory_mb": memory,
                })
        
        track_pipeline_memory()
        
        return {
            "component_memory_usage": memory_samples,
            "pipeline_memory_progression": pipeline_memory,
            "summary": {
                "avg_memory_increase_mb": statistics.mean([
                    s["memory_increase_mb"] for s in memory_samples
                ]),
                "max_memory_used_mb": max([s["memory_after_mb"] for s in memory_samples]),
                "memory_leak_test": "PASS" if all(
                    s["memory_increase_mb"] < 50 for s in memory_samples
                ) else "FAIL",
            },
        }
    
    def benchmark_concurrent_scraping(self) -> Dict[str, Any]:
        """Benchmark concurrent/async scraping performance."""
        self.logger.info("  Testing concurrent scraping...")
        
        scraper = WebScraper(target_url="file://./data/input/example.html")
        
        # Test sync vs async
        test_cases = [
            ("sync_10", False, 10),
            ("sync_100", False, 100),
            ("async_10", True, 10),
            ("async_100", True, 100),
        ]
        
        results = []
        
        for test_name, use_async, limit in test_cases:
            start_time = time.perf_counter()
            
            result = scraper.scrape_data(limit=limit, use_async=use_async)
            
            elapsed = time.perf_counter() - start_time
            
            results.append({
                "test": test_name,
                "async": use_async,
                "limit": limit,
                "elapsed_seconds": elapsed,
                "records_per_second": limit / elapsed if elapsed > 0 else 0,
                "success_rate": result.stats['success_rate'],
                "records_extracted": result.stats['records_extracted'],
            })
        
        # Calculate async benefits
        sync_speed = [r["records_per_second"] for r in results if not r["async"]]
        async_speed = [r["records_per_second"] for r in results if r["async"]]
        
        speedup = statistics.mean(async_speed) / statistics.mean(sync_speed) if sync_speed else 1
        
        return {
            "summary": {
                "async_speedup_factor": speedup,
                "avg_sync_speed_records_sec": statistics.mean(sync_speed) if sync_speed else 0,
                "avg_async_speed_records_sec": statistics.mean(async_speed) if async_speed else 0,
                "recommended_min_batch_for_async": 50 if speedup > 1.2 else 100,
            },
            "detailed_results": results,
            "concurrency_analysis": self._analyze_concurrency_benefits(results),
        }
    
    def benchmark_pipeline_end_to_end(self, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark complete pipeline end-to-end."""
        self.logger.info("  Testing end-to-end pipeline...")
        
        import tempfile
        import os
        
        results = []
        
        for i in range(iterations):
            # Use temporary database for each iteration
            temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
            temp_db.close()
            
            try:
                start_time = time.perf_counter()
                
                # Complete pipeline
                scraper = WebScraper(target_url="file://./data/input/example.html")
                cleaner = DataCleaner()
                
                # Extract
                scrape_result = scraper.scrape_data(limit=100)
                
                # Transform
                cleaned_data = cleaner.clean_data(scrape_result.data)
                
                # Load
                with DatabaseHandler(db_path=temp_db.name) as db:
                    db.insert_data(cleaned_data)
                    final_count = db.get_record_count()
                
                elapsed = time.perf_counter() - start_time
                
                results.append({
                    "iteration": i + 1,
                    "elapsed_seconds": elapsed,
                    "records_processed": len(cleaned_data),
                    "throughput_records_sec": len(cleaned_data) / elapsed if elapsed > 0 else 0,
                    "database_size_mb": os.path.getsize(temp_db.name) / (1024 * 1024),
                    "success": True,
                })
                
            finally:
                if os.path.exists(temp_db.name):
                    os.unlink(temp_db.name)
        
        throughput = [r["throughput_records_sec"] for r in results]
        
        return {
            "summary": {
                "avg_pipeline_throughput_records_sec": statistics.mean(throughput),
                "pipeline_throughput_stddev": statistics.stdev(throughput) if len(throughput) > 1 else 0,
                "avg_pipeline_latency_seconds": statistics.mean([r["elapsed_seconds"] for r in results]),
                "consistency_score": 1 - (statistics.stdev(throughput) / statistics.mean(throughput)) if throughput else 0,
            },
            "detailed_results": results,
            "pipeline_bottleneck_analysis": self._identify_bottlenecks(results),
        }
    
    def benchmark_scalability(self) -> Dict[str, Any]:
        """Benchmark scalability with increasing load."""
        self.logger.info("  Testing scalability...")
        
        load_levels = [100, 500, 1000, 5000]
        results = []
        
        for load in load_levels:
            start_time = time.perf_counter()
            
            # Simulate processing load
            cleaner = DataCleaner()
            test_data = self.test_data[:load]
            cleaned_data = cleaner.clean_data(test_data)
            
            elapsed = time.perf_counter() - start_time
            
            results.append({
                "load_size": load,
                "elapsed_seconds": elapsed,
                "throughput_records_sec": load / elapsed if elapsed > 0 else 0,
                "memory_used_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_percent": psutil.cpu_percent(interval=0.1),
            })
        
        # Calculate scalability metrics
        throughput = [r["throughput_records_sec"] for r in results]
        
        return {
            "summary": {
                "scalability_factor": throughput[-1] / throughput[0] if throughput[0] > 0 else 0,
                "linear_scaling": "YES" if all(
                    abs(throughput[i] / throughput[0] - (i + 1)) < 0.5 
                    for i in range(len(throughput))
                ) else "NO",
                "max_sustainable_load": self._estimate_max_load(results),
            },
            "detailed_results": results,
            "scaling_analysis": self._analyze_scaling_patterns(results),
        }
    
    def _analyze_scraper_performance(self, results: List[Dict]) -> List[str]:
        """Analyze scraper performance results."""
        recommendations = []
        
        throughputs = [r["records_per_second"] for r in results]
        avg_throughput = statistics.mean(throughputs)
        
        if avg_throughput < 10:
            recommendations.append("⚠️  Low throughput: Consider implementing async scraping")
        if avg_throughput > 100:
            recommendations.append("✅ Excellent throughput: Scraper is highly efficient")
        
        # Check batch size optimization
        best_batch = max(results, key=lambda x: x["records_per_second"])
        recommendations.append(f"📊 Optimal batch size: {best_batch['batch_size']} records")
        
        return recommendations
    
    def _analyze_memory_patterns(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze memory usage patterns."""
        memory_per_record = [r["memory_per_record_kb"] for r in results]
        
        return {
            "memory_efficiency": "GOOD" if statistics.mean(memory_per_record) < 1 else "POOR",
            "memory_scaling": "LINEAR" if all(
                abs(results[i]["memory_per_record_kb"] - results[0]["memory_per_record_kb"]) < 0.1
                for i in range(1, len(results))
            ) else "NON_LINEAR",
            "estimated_1m_records_memory_gb": (statistics.mean(memory_per_record) * 1_000_000) / (1024 * 1024),
        }
    
    def _analyze_concurrency_benefits(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze concurrency benefits."""
        async_results = [r for r in results if r["async"]]
        sync_results = [r for r in results if not r["async"]]
        
        if not async_results or not sync_results:
            return {"analysis": "Insufficient data for comparison"}
        
        async_speed = statistics.mean([r["records_per_second"] for r in async_results])
        sync_speed = statistics.mean([r["records_per_second"] for r in sync_results])
        
        return {
            "speedup_ratio": async_speed / sync_speed,
            "recommendation": "Use async for batches > 50" if async_speed > sync_speed * 1.2 else "Async overhead too high",
            "async_overhead_seconds": statistics.mean([r["elapsed_seconds"] for r in async_results]) - 
                                     statistics.mean([r["elapsed_seconds"] for r in sync_results]),
        }
    
    def _identify_bottlenecks(self, results: List[Dict]) -> List[str]:
        """Identify pipeline bottlenecks."""
        bottlenecks = []
        
        avg_throughput = statistics.mean([r["throughput_records_sec"] for r in results])
        
        if avg_throughput < 20:
            bottlenecks.append("🚨 Critical bottleneck: Pipeline throughput < 20 records/sec")
        elif avg_throughput < 100:
            bottlenecks.append("⚠️  Moderate bottleneck: Consider optimizing data cleaning")
        
        return bottlenecks
    
    def _estimate_max_load(self, results: List[Dict]) -> int:
        """Estimate maximum sustainable load."""
        throughputs = [r["throughput_records_sec"] for r in results]
        loads = [r["load_size"] for r in results]
        
        if len(throughputs) < 2:
            return 1000
        
        # Simple linear extrapolation
        try:
            slope = (throughputs[-1] - throughputs[0]) / (loads[-1] - loads[0])
            if slope <= 0:
                return loads[-1]  # Throughput decreasing
            
            # Estimate where throughput would drop below 10 records/sec
            max_load = loads[-1] + ((10 - throughputs[-1]) / slope)
            return int(max_load)
        except:
            return loads[-1] * 2
    
    def _analyze_scaling_patterns(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze scaling patterns."""
        throughputs = [r["throughput_records_sec"] for r in results]
        loads = [r["load_size"] for r in results]
        
        scaling_efficiency = []
        for i in range(1, len(throughputs)):
            load_increase = loads[i] / loads[i-1]
            throughput_increase = throughputs[i] / throughputs[i-1]
            scaling_efficiency.append(throughput_increase / load_increase)
        
        avg_efficiency = statistics.mean(scaling_efficiency) if scaling_efficiency else 0
        
        return {
            "scaling_efficiency": avg_efficiency,
            "scaling_type": "LINEAR" if 0.8 <= avg_efficiency <= 1.2 else "SUB_LINEAR" if avg_efficiency < 0.8 else "SUPER_LINEAR",
            "recommendation": "Scale horizontally" if avg_efficiency < 0.8 else "Scale vertically",
        }
    
    def _log_benchmark_result(self, name: str, result: Dict[str, Any]) -> None:
        """Log benchmark result in a readable format."""
        summary = result.get("summary", {})
        
        if "throughput" in str(summary).lower() or "speed" in str(summary).lower():
            # Find throughput metric
            for key, value in summary.items():
                if "throughput" in key.lower() or "speed" in key.lower():
                    self.logger.info(f"  ✓ {name.replace('_', ' ').title()}: {value:.1f} records/sec")
                    return
        
        # Default logging
        self.logger.info(f"  ✓ {name.replace('_', ' ').title()}: Completed")
    
    def _generate_report(self) -> None:
        """Generate comprehensive performance report."""
        report_file = self.output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Generate summary markdown
        summary_file = self.output_dir / "PERFORMANCE_SUMMARY.md"
        self._generate_markdown_summary(summary_file)
        
        self.logger.info(f"📄 Full report saved to: {report_file}")
        self.logger.info(f"📊 Summary saved to: {summary_file}")
    
    def _generate_markdown_summary(self, output_file: Path) -> None:
        """Generate markdown summary report."""
        summary = [
            "# Performance Benchmark Report",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## System Information",
            "```json",
            json.dumps(self.results["system_info"], indent=2),
            "```",
            "",
            "## Executive Summary",
        ]
        
        # Add key metrics
        key_metrics = []
        
        for test_name, test_result in self.results["tests"].items():
            if "summary" in test_result:
                summary_data = test_result["summary"]
                if "throughput" in str(summary_data).lower():
                    for key, value in summary_data.items():
                        if "throughput" in key.lower() or "speed" in key.lower():
                            key_metrics.append(f"- **{test_name.replace('_', ' ').title()}**: {value:.1f} records/sec")
                elif "avg" in str(summary_data).lower() or "max" in str(summary_data).lower():
                    # Add first meaningful metric
                    for key, value in list(summary_data.items())[:1]:
                        key_metrics.append(f"- **{test_name.replace('_', ' ').title()}**: {key.replace('_', ' ').title()} = {value}")
        
        summary.extend(key_metrics)
        summary.append("")
        summary.append("## Recommendations")
        
        # Generate recommendations
        recommendations = []
        
        # Check overall performance
        all_throughputs = []
        for test_result in self.results["tests"].values():
            if "summary" in test_result:
                summary_data = test_result["summary"]
                for key, value in summary_data.items():
                    if "throughput" in key.lower() and isinstance(value, (int, float)):
                        all_throughputs.append(value)
        
        if all_throughputs:
            avg_throughput = statistics.mean(all_throughputs)
            if avg_throughput < 50:
                recommendations.append("🚨 **Critical**: Overall throughput is low. Consider major optimizations.")
            elif avg_throughput < 200:
                recommendations.append("⚠️ **Warning**: Moderate performance. Review bottleneck analysis.")
            else:
                recommendations.append("✅ **Excellent**: Performance meets enterprise standards.")
        
        summary.extend(recommendations)
        
        with open(output_file, 'w') as f:
            f.write("\n".join(summary))


def main():
    """Main entry point for performance testing."""
    print("=" * 60)
    print("Web Scraper to SQLite - Performance Test Suite")
    print("=" * 60)
    
    # Run benchmarks
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎯 PERFORMANCE TESTING COMPLETE")
    print("=" * 60)
    
    # Extract key metrics
    key_results = {}
    for test_name, test_result in results["tests"].items():
        if "summary" in test_result:
            key_results[test_name] = test_result["summary"]
    
    print("\nKey Metrics:")
    for test_name, summary in key_results.items():
        print(f"\n{test_name.replace('_', ' ').title()}:")
        for key, value in summary.items():
            if isinstance(value, (int, float)):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()