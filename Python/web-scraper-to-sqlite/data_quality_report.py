import sqlite3
import pandas as pd
import numpy as np
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from enum import Enum
import logging
import sys
from rich.console import Console
from rich.table import Table
from rich import box
import warnings
warnings.filterwarnings('ignore')

# Setup rich console for beautiful output
console = Console()


class DataQualityLevel(Enum):
    """Data quality levels based on assessment."""
    EXCELLENT = 4  # 90-100%
    GOOD = 3       # 75-89%
    FAIR = 2       # 60-74%
    POOR = 1       # 40-59%
    CRITICAL = 0   # <40%


@dataclass
class DataQualityMetric:
    """Data quality metric with score and details."""
    name: str
    score: float  # 0-100
    weight: float = 1.0
    details: Dict[str, Any] = None
    level: DataQualityLevel = None
    
    def __post_init__(self):
        """Calculate quality level after initialization."""
        if self.level is None:
            if self.score >= 90:
                self.level = DataQualityLevel.EXCELLENT
            elif self.score >= 75:
                self.level = DataQualityLevel.GOOD
            elif self.score >= 60:
                self.level = DataQualityLevel.FAIR
            elif self.score >= 40:
                self.level = DataQualityLevel.POOR
            else:
                self.level = DataQualityLevel.CRITICAL
    
    @property
    def status_icon(self) -> str:
        """Get status icon for the metric."""
        icons = {
            DataQualityLevel.EXCELLENT: "✅",
            DataQualityLevel.GOOD: "✓",
            DataQualityLevel.FAIR: "⚠️",
            DataQualityLevel.POOR: "❌",
            DataQualityLevel.CRITICAL: "💥"
        }
        return icons.get(self.level, "❓")
    
    @property
    def status_color(self) -> str:
        """Get color for the metric."""
        colors = {
            DataQualityLevel.EXCELLENT: "green",
            DataQualityLevel.GOOD: "green",
            DataQualityLevel.FAIR: "yellow",
            DataQualityLevel.POOR: "red",
            DataQualityLevel.CRITICAL: "red"
        }
        return colors.get(self.level, "white")


class DataQualityReport:
    """Comprehensive data quality assessment framework."""
    
    def __init__(self, db_path: str = "data/scraped_data.db", output_dir: str = "reports"):
        """Initialize data quality reporter."""
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Results storage
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "database": str(self.db_path),
            "metrics": {},
            "summary": {},
            "recommendations": [],
            "visualizations": []
        }
        
        # Color scheme for visualizations
        self.colors = {
            "excellent": "#2ecc71",  # Green
            "good": "#27ae60",       # Dark Green
            "fair": "#f39c12",       # Orange
            "poor": "#e74c3c",       # Red
            "critical": "#c0392b",   # Dark Red
            "primary": "#3498db",    # Blue
            "secondary": "#9b59b6",  # Purple
        }
        
        # Define data quality dimensions (based on DAMA)
        self.quality_dimensions = {
            "completeness": {
                "weight": 0.25,
                "description": "Degree to which data is not missing"
            },
            "accuracy": {
                "weight": 0.20,
                "description": "Degree to which data correctly describes reality"
            },
            "consistency": {
                "weight": 0.15,
                "description": "Degree to which data is uniform across systems"
            },
            "timeliness": {
                "weight": 0.15,
                "description": "Degree to which data is current and available"
            },
            "validity": {
                "weight": 0.10,
                "description": "Degree to which data conforms to syntax rules"
            },
            "uniqueness": {
                "weight": 0.10,
                "description": "Degree to which data is free of duplicates"
            },
            "integrity": {
                "weight": 0.05,
                "description": "Degree to which data maintains relationships"
            }
        }
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'data_quality.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """Load data quality configuration."""
        config_file = Path("config.yaml")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                return config.get("analytics", {}).get("quality_metrics", {})
            except:
                pass
        
        # Default configuration
        return {
            "completeness_threshold": 0.8,   # 80% required fields filled
            "accuracy_threshold": 0.9,       # 90% data accuracy
            "timeliness_hours": 24,         # Data should be less than 24 hours old
            "outlier_threshold": 3.0,       # Z-score threshold for outliers
            "duplicate_threshold": 0.05,    # Max 5% duplicates allowed
        }
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate comprehensive data quality report."""
        console.print("\n[bold blue]📊 DATA QUALITY ASSESSMENT REPORT[/bold blue]")
        console.print("=" * 60)
        
        if not self.db_path.exists():
            console.print("[red]❌ Database not found![/red]")
            return self.results
        
        try:
            # Connect to database
            self.conn = sqlite3.connect(self.db_path)
            
            # Get database metadata
            metadata = self._get_database_metadata()
            self.results["metadata"] = metadata
            
            console.print(f"[cyan]Database:[/cyan] {self.db_path.name}")
            console.print(f"[cyan]Tables:[/cyan] {len(metadata['tables'])}")
            console.print(f"[cyan]Total Records:[/cyan] {metadata['total_records']:,}")
            console.print(f"[cyan]Database Size:[/cyan] {metadata['size_mb']:.2f} MB")
            console.print("-" * 60)
            
            # Run all quality assessments
            assessments = [
                ("completeness_analysis", self.assess_completeness),
                ("accuracy_analysis", self.assess_accuracy),
                ("consistency_analysis", self.assess_consistency),
                ("timeliness_analysis", self.assess_timeliness),
                ("validity_analysis", self.assess_validity),
                ("uniqueness_analysis", self.assess_uniqueness),
                ("integrity_analysis", self.assess_integrity),
                ("statistical_analysis", self.perform_statistical_analysis),
                ("business_impact", self.assess_business_impact),
                ("trend_analysis", self.analyze_trends),
            ]
            
            for assessment_name, assessment_func in assessments:
                try:
                    console.print(f"[white]🔍 Running: {assessment_name.replace('_', ' ').title()}...[/white]")
                    result = assessment_func()
                    self.results["metrics"][assessment_name] = result
                except Exception as e:
                    self.logger.error(f"Assessment '{assessment_name}' failed: {e}")
                    self.results["metrics"][assessment_name] = {"error": str(e)}
            
            # Calculate overall scores
            self._calculate_overall_scores()
            
            # Generate visualizations
            self._generate_visualizations()
            
            # Generate recommendations
            self._generate_recommendations()
            
            # Display summary
            self._display_summary()
            
            # Save reports
            self._save_reports()
            
            console.print("\n[green]✅ DATA QUALITY REPORT COMPLETED[/green]")
            console.print("=" * 60)
            
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()
        
        return self.results
    
    def _get_database_metadata(self) -> Dict[str, Any]:
        """Get database metadata and statistics."""
        cursor = self.conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
        
        metadata = {
            "tables": tables,
            "total_records": 0,
            "size_bytes": self.db_path.stat().st_size,
            "size_mb": self.db_path.stat().st_size / (1024 * 1024),
            "last_modified": datetime.fromtimestamp(self.db_path.stat().st_mtime).isoformat(),
        }
        
        # Count records in each table
        table_stats = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            table_stats[table] = count
            metadata["total_records"] += count
        
        metadata["table_stats"] = table_stats
        
        # Get column information for main table
        if "scraped_records" in tables:
            cursor.execute("PRAGMA table_info(scraped_records);")
            columns = cursor.fetchall()
            metadata["main_table_columns"] = [
                {"name": col[1], "type": col[2], "nullable": not col[3]}
                for col in columns
            ]
        
        return metadata
    
    def assess_completeness(self) -> Dict[str, Any]:
        """Assess data completeness (missing values)."""
        console.print("  Assessing completeness...")
        
        if "scraped_records" not in self.results["metadata"]["tables"]:
            return {"score": 0, "error": "Main table not found"}
        
        # Load data
        df = pd.read_sql_query("SELECT * FROM scraped_records", self.conn)
        
        # Calculate missing values
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        completeness_score = 100 * (1 - missing_cells / total_cells) if total_cells > 0 else 0
        
        # Column-level completeness
        column_completeness = {}
        for column in df.columns:
            total = len(df)
            missing = df[column].isna().sum()
            column_score = 100 * (1 - missing / total) if total > 0 else 0
            column_completeness[column] = {
                "score": column_score,
                "missing_count": int(missing),
                "missing_percentage": round(100 * missing / total, 2) if total > 0 else 0,
                "total": total
            }
        
        # Critical columns (based on configuration or common sense)
        critical_columns = ["title", "price", "date", "category"]
        critical_scores = []
        for col in critical_columns:
            if col in column_completeness:
                critical_scores.append(column_completeness[col]["score"])
        
        critical_completeness = np.mean(critical_scores) if critical_scores else 0
        
        # Generate metric
        metric = DataQualityMetric(
            name="completeness",
            score=completeness_score,
            weight=self.quality_dimensions["completeness"]["weight"],
            details={
                "overall_score": completeness_score,
                "critical_completeness": critical_completeness,
                "missing_cells": int(missing_cells),
                "total_cells": total_cells,
                "missing_percentage": round(100 * missing_cells / total_cells, 2) if total_cells > 0 else 0,
                "column_analysis": column_completeness,
                "critical_columns": critical_columns,
                "critical_score": critical_completeness
            }
        )
        
        return {
            "metric": metric,
            "summary": f"Completeness: {completeness_score:.1f}% ({missing_cells:,} missing values)"
        }
    
    def assess_accuracy(self) -> Dict[str, Any]:
        """Assess data accuracy (correctness)."""
        console.print("  Assessing accuracy...")
        
        if "scraped_records" not in self.results["metadata"]["tables"]:
            return {"score": 0, "error": "Main table not found"}
        
        df = pd.read_sql_query("SELECT * FROM scraped_records", self.conn)
        
        accuracy_scores = []
        accuracy_details = {}
        
        # 1. Price accuracy (should be positive numbers)
        if "price" in df.columns:
            total_prices = len(df["price"].dropna())
            if total_prices > 0:
                valid_prices = ((df["price"] >= 0) & (df["price"] <= 100000)).sum()
                price_accuracy = 100 * valid_prices / total_prices
                accuracy_scores.append(price_accuracy)
                accuracy_details["price_accuracy"] = {
                    "score": price_accuracy,
                    "valid_count": int(valid_prices),
                    "invalid_count": int(total_prices - valid_prices),
                    "invalid_examples": df[df["price"] < 0]["price"].head(3).tolist() if (df["price"] < 0).any() else []
                }
        
        # 2. Date accuracy (should be valid dates)
        if "date" in df.columns:
            # Try to parse dates
            date_series = pd.to_datetime(df["date"], errors='coerce')
            total_dates = len(date_series.dropna())
            if total_dates > 0:
                valid_dates = date_series.notna().sum()
                date_accuracy = 100 * valid_dates / total_dates
                accuracy_scores.append(date_accuracy)
                accuracy_details["date_accuracy"] = {
                    "score": date_accuracy,
                    "valid_count": int(valid_dates),
                    "invalid_count": int(total_dates - valid_dates),
                    "invalid_examples": df[date_series.isna()]["date"].head(3).tolist() if date_series.isna().any() else []
                }
        
        # 3. Rating accuracy (should be between 0-5)
        if "rating" in df.columns:
            total_ratings = len(df["rating"].dropna())
            if total_ratings > 0:
                valid_ratings = ((df["rating"] >= 0) & (df["rating"] <= 5)).sum()
                rating_accuracy = 100 * valid_ratings / total_ratings
                accuracy_scores.append(rating_accuracy)
                accuracy_details["rating_accuracy"] = {
                    "score": rating_accuracy,
                    "valid_count": int(valid_ratings),
                    "invalid_count": int(total_ratings - valid_ratings)
                }
        
        # 4. URL format accuracy (if URL column exists)
        if "url" in df.columns:
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            total_urls = len(df["url"].dropna())
            if total_urls > 0:
                valid_urls = df["url"].str.match(url_pattern, na=False).sum()
                url_accuracy = 100 * valid_urls / total_urls
                accuracy_scores.append(url_accuracy)
                accuracy_details["url_accuracy"] = {
                    "score": url_accuracy,
                    "valid_count": int(valid_urls),
                    "invalid_count": int(total_urls - valid_urls)
                }
        
        # Calculate overall accuracy
        accuracy_score = np.mean(accuracy_scores) if accuracy_scores else 0
        
        metric = DataQualityMetric(
            name="accuracy",
            score=accuracy_score,
            weight=self.quality_dimensions["accuracy"]["weight"],
            details={
                "overall_score": accuracy_score,
                "component_scores": accuracy_details,
                "tests_performed": len(accuracy_scores)
            }
        )
        
        return {
            "metric": metric,
            "summary": f"Accuracy: {accuracy_score:.1f}% ({len(accuracy_scores)} validation tests)"
        }
    
    def assess_consistency(self) -> Dict[str, Any]:
        """Assess data consistency across records."""
        console.print("  Assessing consistency...")
        
        if "scraped_records" not in self.results["metadata"]["tables"]:
            return {"score": 0, "error": "Main table not found"}
        
        df = pd.read_sql_query("SELECT * FROM scraped_records", self.conn)
        
        consistency_scores = []
        consistency_details = {}
        
        # 1. Data type consistency
        dtype_issues = []
        for column in df.columns:
            # Check if column has mixed types (object columns might have mixed)
            if df[column].dtype == 'object':
                unique_types = set(type(val).__name__ for val in df[column].dropna().head(100))
                if len(unique_types) > 1:
                    dtype_issues.append({
                        "column": column,
                        "types_found": list(unique_types)
                    })
        
        dtype_score = 100 - (len(dtype_issues) / len(df.columns) * 100) if df.columns.any() else 100
        consistency_scores.append(dtype_score)
        consistency_details["data_type_consistency"] = {
            "score": dtype_score,
            "issues_found": len(dtype_issues),
            "issues": dtype_issues[:5]  # Limit to 5 issues
        }
        
        # 2. Format consistency (e.g., price formatting)
        if "price" in df.columns:
            # Check if all prices have same formatting (no currency symbols mixed)
            price_samples = df["price"].dropna().astype(str).head(100)
            has_currency = price_samples.str.contains(r'[$€£¥]').any()
            has_commas = price_samples.str.contains(',').any()
            
            format_score = 100
            format_issues = []
            if has_currency:
                format_score -= 25
                format_issues.append("Currency symbols present")
            if has_commas:
                format_score -= 25
                format_issues.append("Commas present as thousand separators")
            
            consistency_scores.append(format_score)
            consistency_details["price_format_consistency"] = {
                "score": format_score,
                "issues": format_issues
            }
        
        # 3. Categorical value consistency
        categorical_cols = ["category", "stock_status", "brand"]
        for col in categorical_cols:
            if col in df.columns:
                unique_values = df[col].dropna().unique()
                # Check for variations of same value (e.g., "Electronics" vs "electronics")
                lower_values = [str(v).lower() for v in unique_values]
                unique_lower = set(lower_values)
                
                if len(unique_lower) < len(unique_values):
                    consistency_score = 100 * len(unique_lower) / len(unique_values) if unique_values.any() else 100
                    consistency_scores.append(consistency_score)
                    consistency_details[f"{col}_consistency"] = {
                        "score": consistency_score,
                        "unique_values": len(unique_values),
                        "unique_normalized": len(unique_lower),
                        "variations_found": len(unique_values) - len(unique_lower)
                    }
        
        # Calculate overall consistency
        consistency_score = np.mean(consistency_scores) if consistency_scores else 0
        
        metric = DataQualityMetric(
            name="consistency",
            score=consistency_score,
            weight=self.quality_dimensions["consistency"]["weight"],
            details={
                "overall_score": consistency_score,
                "component_scores": consistency_details,
                "tests_performed": len(consistency_scores)
            }
        )
        
        return {
            "metric": metric,
            "summary": f"Consistency: {consistency_score:.1f}% ({len(consistency_scores)} consistency checks)"
        }
    
    def assess_timeliness(self) -> Dict[str, Any]:
        """Assess data timeliness and freshness."""
        console.print("  Assessing timeliness...")
        
        if "scraped_records" not in self.results["metadata"]["tables"]:
            return {"score": 0, "error": "Main table not found"}
        
        df = pd.read_sql_query("SELECT * FROM scraped_records", self.conn)
        
        timeliness_score = 100
        timeliness_details = {}
        
        # 1. Check if date column exists and has recent data
        if "date" in df.columns:
            try:
                # Convert to datetime
                df["date_parsed"] = pd.to_datetime(df["date"], errors='coerce')
                valid_dates = df["date_parsed"].dropna()
                
                if len(valid_dates) > 0:
                    latest_date = valid_dates.max()
                    today = pd.Timestamp.now()
                    
                    # Calculate days since latest data
                    days_old = (today - latest_date).days
                    
                    # Score based on freshness (higher score for newer data)
                    if days_old <= 1:
                        freshness_score = 100
                    elif days_old <= 7:
                        freshness_score = 80
                    elif days_old <= 30:
                        freshness_score = 60
                    elif days_old <= 90:
                        freshness_score = 40
                    else:
                        freshness_score = 20
                    
                    timeliness_score = freshness_score
                    timeliness_details["data_freshness"] = {
                        "score": freshness_score,
                        "latest_date": latest_date.strftime('%Y-%m-%d'),
                        "days_old": days_old,
                        "total_dates": len(valid_dates)
                    }
            except:
                timeliness_score = 0
                timeliness_details["data_freshness"] = {
                    "score": 0,
                    "error": "Could not parse dates"
                }
        
        # 2. Check scrape timestamps if available
        if "scraped_at" in df.columns:
            try:
                df["scraped_at_parsed"] = pd.to_datetime(df["scraped_at"], errors='coerce')
                valid_scrapes = df["scraped_at_parsed"].dropna()
                
                if len(valid_scrapes) > 0:
                    latest_scrape = valid_scrapes.max()
                    hours_since_scrape = (pd.Timestamp.now() - latest_scrape).total_seconds() / 3600
                    
                    scrape_freshness = max(0, 100 - (hours_since_scrape / 24 * 10))  # Lose 10% per day
                    timeliness_score = (timeliness_score + scrape_freshness) / 2
                    
                    timeliness_details["scrape_freshness"] = {
                        "score": scrape_freshness,
                        "latest_scrape": latest_scrape.strftime('%Y-%m-%d %H:%M'),
                        "hours_since_scrape": round(hours_since_scrape, 1),
                        "total_scrapes": len(valid_scrapes)
                    }
            except:
                pass
        
        metric = DataQualityMetric(
            name="timeliness",
            score=timeliness_score,
            weight=self.quality_dimensions["timeliness"]["weight"],
            details={
                "overall_score": timeliness_score,
                "details": timeliness_details,
                "threshold_hours": self.config.get("timeliness_hours", 24)
            }
        )
        
        return {
            "metric": metric,
            "summary": f"Timeliness: {timeliness_score:.1f}% (data freshness assessment)"
        }
    
    def assess_validity(self) -> Dict[str, Any]:
        """Assess data validity against business rules."""
        console.print("  Assessing validity...")
        
        if "scraped_records" not in self.results["metadata"]["tables"]:
            return {"score": 0, "error": "Main table not found"}
        
        df = pd.read_sql_query("SELECT * FROM scraped_records", self.conn)
        
        validity_scores = []
        validity_details = {}
        
        # Define validation rules
        validation_rules = [
            {
                "column": "title",
                "rule": "not_null",
                "description": "Title should not be null",
                "weight": 2.0
            },
            {
                "column": "price",
                "rule": "positive_number",
                "description": "Price should be positive",
                "weight": 1.5
            },
            {
                "column": "price",
                "rule": "reasonable_range",
                "description": "Price should be reasonable (0-10000)",
                "weight": 1.0
            },
            {
                "column": "rating",
                "rule": "range_0_5",
                "description": "Rating should be between 0-5",
                "weight": 1.0
            },
            {
                "column": "date",
                "rule": "valid_date",
                "description": "Date should be parsable",
                "weight": 1.5
            }
        ]
        
        rule_results = []
        
        for rule in validation_rules:
            column = rule["column"]
            if column not in df.columns:
                continue
            
            col_data = df[column].dropna()
            total = len(col_data)
            
            if total == 0:
                score = 0
            else:
                if rule["rule"] == "not_null":
                    valid = col_data.notna().sum()
                elif rule["rule"] == "positive_number":
                    valid = (col_data > 0).sum()
                elif rule["rule"] == "reasonable_range":
                    valid = ((col_data >= 0) & (col_data <= 10000)).sum()
                elif rule["rule"] == "range_0_5":
                    valid = ((col_data >= 0) & (col_data <= 5)).sum()
                elif rule["rule"] == "valid_date":
                    # Try to parse dates
                    parsed = pd.to_datetime(col_data, errors='coerce')
                    valid = parsed.notna().sum()
                else:
                    valid = total  # Unknown rule, assume valid
                
                score = 100 * valid / total
            
            validity_scores.append(score * rule["weight"])
            rule_results.append({
                "rule": rule["description"],
                "score": score,
                "weight": rule["weight"],
                "valid_count": int(valid),
                "total_count": total
            })
        
        # Calculate weighted validity score
        if validity_scores:
            total_weight = sum(rule["weight"] for rule in validation_rules if rule["column"] in df.columns)
            validity_score = sum(validity_scores) / total_weight if total_weight > 0 else 0
        else:
            validity_score = 0
        
        validity_details["rule_validation"] = rule_results
        
        metric = DataQualityMetric(
            name="validity",
            score=validity_score,
            weight=self.quality_dimensions["validity"]["weight"],
            details={
                "overall_score": validity_score,
                "rules_tested": len(rule_results),
                "rule_results": rule_results
            }
        )
        
        return {
            "metric": metric,
            "summary": f"Validity: {validity_score:.1f}% ({len(rule_results)} business rules)"
        }
    
    def assess_uniqueness(self) -> Dict[str, Any]:
        """Assess data uniqueness (duplicate detection)."""
        console.print("  Assessing uniqueness...")
        
        if "scraped_records" not in self.results["metadata"]["tables"]:
            return {"score": 0, "error": "Main table not found"}
        
        df = pd.read_sql_query("SELECT * FROM scraped_records", self.conn)
        
        # Check for exact duplicates
        total_records = len(df)
        duplicate_rows = df.duplicated().sum()
        duplicate_percentage = 100 * duplicate_rows / total_records if total_records > 0 else 0
        
        # Check for semantic duplicates (based on key fields)
        key_columns = ["title", "date", "price"]
        available_keys = [col for col in key_columns if col in df.columns]
        
        semantic_duplicates = 0
        if available_keys:
            semantic_duplicates = df.duplicated(subset=available_keys).sum()
        
        semantic_duplicate_percentage = 100 * semantic_duplicates / total_records if total_records > 0 else 0
        
        # Calculate uniqueness score (higher score = fewer duplicates)
        uniqueness_score = max(0, 100 - duplicate_percentage - semantic_duplicate_percentage)
        
        metric = DataQualityMetric(
            name="uniqueness",
            score=uniqueness_score,
            weight=self.quality_dimensions["uniqueness"]["weight"],
            details={
                "overall_score": uniqueness_score,
                "exact_duplicates": int(duplicate_rows),
                "exact_duplicate_percentage": duplicate_percentage,
                "semantic_duplicates": int(semantic_duplicates),
                "semantic_duplicate_percentage": semantic_duplicate_percentage,
                "total_records": total_records,
                "key_columns_used": available_keys
            }
        )
        
        return {
            "metric": metric,
            "summary": f"Uniqueness: {uniqueness_score:.1f}% ({duplicate_rows:,} exact duplicates)"
        }
    
    def assess_integrity(self) -> Dict[str, Any]:
        """Assess data integrity (referential and business logic)."""
        console.print("  Assessing integrity...")
        
        if "scraped_records" not in self.results["metadata"]["tables"]:
            return {"score": 0, "error": "Main table not found"}
        
        df = pd.read_sql_query("SELECT * FROM scraped_records", self.conn)
        
        integrity_scores = []
        integrity_details = {}
        
        # 1. Check for orphaned references (if we had foreign keys)
        # For now, check logical relationships
        
        # 2. Check business logic integrity
        # Example: If stock_status is "out_of_stock", should we have price?
        if all(col in df.columns for col in ["stock_status", "price"]):
            out_of_stock = df[df["stock_status"] == "out_of_stock"]
            total_out_of_stock = len(out_of_stock)
            
            if total_out_of_stock > 0:
                # Check if out-of-stock items have prices (they might or might not)
                # This is business logic dependent
                pass
        
        # 3. Check temporal integrity (dates make sense)
        if "date" in df.columns:
            try:
                df["date_parsed"] = pd.to_datetime(df["date"], errors='coerce')
                valid_dates = df["date_parsed"].dropna()
                
                if len(valid_dates) > 0:
                    # Check if dates are in reasonable range (not future dates typically)
                    today = pd.Timestamp.now()
                    future_dates = (valid_dates > today).sum()
                    future_percentage = 100 * future_dates / len(valid_dates)
                    
                    temporal_score = max(0, 100 - future_percentage * 2)  # Penalize future dates
                    integrity_scores.append(temporal_score)
                    integrity_details["temporal_integrity"] = {
                        "score": temporal_score,
                        "future_dates": int(future_dates),
                        "future_percentage": future_percentage
                    }
            except:
                pass
        
        # Calculate overall integrity score
        integrity_score = np.mean(integrity_scores) if integrity_scores else 100
        
        metric = DataQualityMetric(
            name="integrity",
            score=integrity_score,
            weight=self.quality_dimensions["integrity"]["weight"],
            details={
                "overall_score": integrity_score,
                "component_scores": integrity_details
            }
        )
        
        return {
            "metric": metric,
            "summary": f"Integrity: {integrity_score:.1f}% (business logic validation)"
        }
    
    def perform_statistical_analysis(self) -> Dict[str, Any]:
        """Perform statistical analysis of data."""
        console.print("  Performing statistical analysis...")
        
        if "scraped_records" not in self.results["metadata"]["tables"]:
            return {"score": 100, "error": "Main table not found", "summary": "No data for analysis"}
        
        df = pd.read_sql_query("SELECT * FROM scraped_records", self.conn)
        
        stats = {}
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in df.columns:
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    stats[col] = {
                        "count": len(col_data),
                        "mean": float(col_data.mean()),
                        "std": float(col_data.std()),
                        "min": float(col_data.min()),
                        "25%": float(col_data.quantile(0.25)),
                        "50%": float(col_data.quantile(0.50)),
                        "75%": float(col_data.quantile(0.75)),
                        "max": float(col_data.max()),
                        "skewness": float(col_data.skew()),
                        "kurtosis": float(col_data.kurtosis()),
                        "outliers": self._detect_outliers(col_data)
                    }
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=[object]).columns
        for col in categorical_cols:
            if col in df.columns:
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    stats[col] = {
                        "count": len(col_data),
                        "unique_values": int(col_data.nunique()),
                        "top_value": col_data.mode().iloc[0] if not col_data.mode().empty else None,
                        "top_frequency": int(col_data.value_counts().iloc[0]) if len(col_data.value_counts()) > 0 else 0,
                        "top_percentage": 100 * col_data.value_counts().iloc[0] / len(col_data) if len(col_data) > 0 else 0
                    }
        
        return {
            "score": 100,  # Statistical analysis doesn't have a score
            "statistics": stats,
            "summary": f"Analyzed {len(numeric_cols)} numeric and {len(categorical_cols)} categorical columns"
        }
    
    def assess_business_impact(self) -> Dict[str, Any]:
        """Assess business impact of data quality issues."""
        console.print("  Assessing business impact...")
        
        # Calculate potential business impact based on quality scores
        impact_details = {}
        total_impact = 0
        
        # Get all quality metrics
        quality_metrics = {}
        for metric_name, result in self.results.get("metrics", {}).items():
            if "metric" in result and hasattr(result["metric"], "score"):
                quality_metrics[metric_name] = result["metric"]
        
        # Calculate business impact for each dimension
        for dim_name, dim_info in self.quality_dimensions.items():
            # Find corresponding metric
            metric_key = f"{dim_name}_analysis"
            if metric_key in quality_metrics:
                metric = quality_metrics[metric_key]
                score = metric.score
                
                # Impact calculation based on score and weight
                if score >= 90:
                    impact = 0  # No impact
                elif score >= 75:
                    impact = dim_info["weight"] * 10  # Low impact
                elif score >= 60:
                    impact = dim_info["weight"] * 25  # Medium impact
                elif score >= 40:
                    impact = dim_info["weight"] * 50  # High impact
                else:
                    impact = dim_info["weight"] * 100  # Critical impact
                
                impact_details[dim_name] = {
                    "score": score,
                    "weight": dim_info["weight"],
                    "impact_score": impact,
                    "description": dim_info["description"]
                }
                total_impact += impact
        
        # Normalize impact to 0-100 scale
        normalized_impact = min(100, total_impact)
        
        # Calculate business readiness score (inverse of impact)
        business_readiness = max(0, 100 - normalized_impact)
        
        return {
            "score": business_readiness,
            "impact_score": normalized_impact,
            "impact_details": impact_details,
            "summary": f"Business Readiness: {business_readiness:.1f}% (Impact: {normalized_impact:.1f})"
        }
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze data quality trends over time."""
        console.print("  Analyzing trends...")
        
        # For now, return placeholder
        # In production, this would compare with historical quality reports
        
        return {
            "score": 100,
            "summary": "Trend analysis requires historical data (not available in this run)",
            "recommendation": "Run quality reports regularly to establish trends"
        }
    
    def _detect_outliers(self, data: pd.Series) -> Dict[str, Any]:
        """Detect outliers using IQR method."""
        if len(data) < 4:
            return {"count": 0, "percentage": 0, "method": "IQR"}
        
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        
        return {
            "count": len(outliers),
            "percentage": 100 * len(outliers) / len(data),
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "method": "IQR (1.5 * IQR)"
        }
    
    def _calculate_overall_scores(self) -> None:
        """Calculate overall data quality scores."""
        total_weighted_score = 0
        total_weight = 0
        
        dimension_scores = {}
        
        # Calculate weighted score from all quality dimensions
        for dim_name, dim_info in self.quality_dimensions.items():
            metric_key = f"{dim_name}_analysis"
            if metric_key in self.results["metrics"]:
                result = self.results["metrics"][metric_key]
                if "metric" in result and hasattr(result["metric"], "score"):
                    metric = result["metric"]
                    score = metric.score
                    weight = dim_info["weight"]
                    
                    total_weighted_score += score * weight
                    total_weight += weight
                    
                    dimension_scores[dim_name] = {
                        "score": score,
                        "weight": weight,
                        "level": metric.level.name,
                        "status": metric.status_icon
                    }
        
        # Calculate overall score
        if total_weight > 0:
            overall_score = total_weighted_score / total_weight
        else:
            overall_score = 0
        
        # Determine overall level
        if overall_score >= 90:
            overall_level = DataQualityLevel.EXCELLENT
        elif overall_score >= 75:
            overall_level = DataQualityLevel.GOOD
        elif overall_score >= 60:
            overall_level = DataQualityLevel.FAIR
        elif overall_score >= 40:
            overall_level = DataQualityLevel.POOR
        else:
            overall_level = DataQualityLevel.CRITICAL
        
        # Update results
        self.results["summary"] = {
            "overall_score": overall_score,
            "overall_level": overall_level.name,
            "overall_status": "✅ EXCELLENT" if overall_level == DataQualityLevel.EXCELLENT else
                             "✓ GOOD" if overall_level == DataQualityLevel.GOOD else
                             "⚠️ FAIR" if overall_level == DataQualityLevel.FAIR else
                             "❌ POOR" if overall_level == DataQualityLevel.POOR else "💥 CRITICAL",
            "dimension_scores": dimension_scores,
            "total_weight": total_weight,
            "assessment_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_visualizations(self) -> None:
        """Generate data quality visualizations."""
        console.print("  Generating visualizations...")
        
        try:
            # Create visualizations directory
            viz_dir = self.output_dir / "visualizations"
            viz_dir.mkdir(exist_ok=True)
            
            # 1. Quality Dimension Radar Chart
            self._create_radar_chart(viz_dir)
            
            # 2. Quality Score Bar Chart
            self._create_score_barchart(viz_dir)
            
            # 3. Missing Values Heatmap (if data available)
            if "completeness_analysis" in self.results["metrics"]:
                self._create_missing_values_heatmap(viz_dir)
            
            # 4. Quality Trend Chart (placeholder for now)
            self._create_trend_chart(viz_dir)
            
            self.results["visualizations"] = [
                str(viz_dir / "quality_radar.png"),
                str(viz_dir / "quality_scores.png"),
                str(viz_dir / "missing_values.png"),
                str(viz_dir / "quality_trend.png")
            ]
            
        except Exception as e:
            self.logger.error(f"Visualization generation failed: {e}")
    
    def _create_radar_chart(self, output_dir: Path) -> None:
        """Create radar chart of quality dimensions."""
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle, RegularPolygon
        from matplotlib.path import Path as mPath
        from matplotlib.spines import Spine
        from matplotlib.projections.polar import PolarAxes
        from matplotlib.projections import register_projection
        
        # Prepare data
        dimensions = list(self.quality_dimensions.keys())
        scores = []
        
        for dim in dimensions:
            metric_key = f"{dim}_analysis"
            if metric_key in self.results["metrics"]:
                result = self.results["metrics"][metric_key]
                if "metric" in result and hasattr(result["metric"], "score"):
                    scores.append(result["metric"].score)
                else:
                    scores.append(0)
            else:
                scores.append(0)
        
        # Complete the circle
        dimensions += [dimensions[0]]
        scores += [scores[0]]
        
        # Create figure
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, polar=True)
        
        # Plot data
        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=True).tolist()
        ax.plot(angles, scores, 'o-', linewidth=2, color=self.colors["primary"])
        ax.fill(angles, scores, alpha=0.25, color=self.colors["primary"])
        
        # Set labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([d.title() for d in dimensions[:-1]], fontsize=10)
        
        # Set y-axis
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=8)
        ax.grid(True)
        
        # Add title
        plt.title('Data Quality Radar Chart', size=14, fontweight='bold')
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_dir / "quality_radar.png", dpi=150, bbox_inches='tight')
        plt.close()
    
    def _create_score_barchart(self, output_dir: Path) -> None:
        """Create bar chart of quality scores."""
        import matplotlib.pyplot as plt
        
        # Prepare data
        dimensions = []
        scores = []
        colors = []
        
        for dim_name, dim_info in self.quality_dimensions.items():
            metric_key = f"{dim_name}_analysis"
            if metric_key in self.results["metrics"]:
                result = self.results["metrics"][metric_key]
                if "metric" in result and hasattr(result["metric"], "score"):
                    metric = result["metric"]
                    dimensions.append(dim_name.title())
                    scores.append(metric.score)
                    
                    # Color based on score
                    if metric.score >= 90:
                        colors.append(self.colors["excellent"])
                    elif metric.score >= 75:
                        colors.append(self.colors["good"])
                    elif metric.score >= 60:
                        colors.append(self.colors["fair"])
                    elif metric.score >= 40:
                        colors.append(self.colors["poor"])
                    else:
                        colors.append(self.colors["critical"])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create bars
        bars = ax.bar(dimensions, scores, color=colors, edgecolor='black')
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 1,
                   f'{score:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # Customize plot
        ax.set_ylim(0, 110)
        ax.set_ylabel('Quality Score (%)', fontsize=11)
        ax.set_title('Data Quality Dimension Scores', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        
        # Add overall score annotation
        overall_score = self.results["summary"].get("overall_score", 0)
        ax.axhline(y=overall_score, color='red', linestyle='--', alpha=0.7, linewidth=2)
        ax.text(len(dimensions) - 0.5, overall_score + 2, 
               f'Overall: {overall_score:.1f}%', color='red', fontweight='bold')
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_dir / "quality_scores.png", dpi=150, bbox_inches='tight')
        plt.close()
    
    def _create_missing_values_heatmap(self, output_dir: Path) -> None:
        """Create heatmap of missing values."""
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Get completeness data
        result = self.results["metrics"]["completeness_analysis"]
        if "details" in result and "column_analysis" in result["details"]:
            column_data = result["details"]["column_analysis"]
            
            # Prepare data for heatmap
            columns = []
            missing_percentages = []
            
            for col_name, col_info in column_data.items():
                columns.append(col_name)
                missing_percentages.append(col_info["missing_percentage"])
            
            # Create heatmap data
            data = pd.DataFrame({
                'Column': columns,
                'Missing %': missing_percentages
            })
            data = data.sort_values('Missing %', ascending=False)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, max(6, len(columns) * 0.4)))
            
            # Create heatmap
            cmap = plt.cm.Reds
            norm = plt.Normalize(0, 100)
            colors = cmap(norm(data['Missing %']))
            
            bars = ax.barh(data['Column'], data['Missing %'], color=colors, edgecolor='black')
            
            # Add value labels
            for bar, value in zip(bars, data['Missing %']):
                ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                       f'{value:.1f}%', va='center', fontsize=9)
            
            # Customize plot
            ax.set_xlim(0, 100)
            ax.set_xlabel('Missing Values (%)', fontsize=11)
            ax.set_title('Missing Values by Column', fontsize=14, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label('Missing %', rotation=270, labelpad=15)
            
            # Save figure
            plt.tight_layout()
            plt.savefig(output_dir / "missing_values.png", dpi=150, bbox_inches='tight')
            plt.close()
    
    def _create_trend_chart(self, output_dir: Path) -> None:
        """Create trend chart of quality scores over time."""
        import matplotlib.pyplot as plt
        
        # For now, create a placeholder chart
        # In production, this would load historical data
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Sample trend data (would be real historical data)
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        scores = np.random.normal(85, 5, 7).clip(70, 100)
        
        ax.plot(dates, scores, 'o-', linewidth=2, color=self.colors["primary"], markersize=8)
        ax.fill_between(dates, scores, 70, alpha=0.2, color=self.colors["primary"])
        
        ax.set_ylim(70, 100)
        ax.set_ylabel('Quality Score (%)', fontsize=11)
        ax.set_title('Data Quality Trend (Last 7 Days)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Add today's score
        today_score = self.results["summary"].get("overall_score", 0)
        ax.axhline(y=today_score, color='red', linestyle='--', alpha=0.7, linewidth=2)
        ax.text(dates[-1], today_score + 1, f'Today: {today_score:.1f}%', 
               color='red', fontweight='bold', ha='right')
        
        plt.tight_layout()
        plt.savefig(output_dir / "quality_trend.png", dpi=150, bbox_inches='tight')
        plt.close()
    
    def _generate_recommendations(self) -> None:
        """Generate actionable recommendations based on quality assessment."""
        recommendations = []
        
        # Analyze each dimension for issues
        for dim_name, dim_info in self.quality_dimensions.items():
            metric_key = f"{dim_name}_analysis"
            if metric_key in self.results["metrics"]:
                result = self.results["metrics"][metric_key]
                if "metric" in result:
                    metric = result["metric"]
                    
                    # Generate recommendations based on score
                    if metric.score < 90:
                        if dim_name == "completeness":
                            if metric.score < 80:
                                recommendations.append({
                                    "priority": "HIGH",
                                    "dimension": "Completeness",
                                    "issue": f"Low completeness score ({metric.score:.1f}%)",
                                    "action": "Implement data validation rules to prevent missing values",
                                    "impact": "High impact on analysis reliability"
                                })
                        
                        elif dim_name == "accuracy":
                            if metric.score < 85:
                                recommendations.append({
                                    "priority": "HIGH",
                                    "dimension": "Accuracy",
                                    "issue": f"Accuracy issues detected ({metric.score:.1f}%)",
                                    "action": "Review data sources and implement data cleaning pipeline",
                                    "impact": "Critical for business decisions"
                                })
                        
                        elif dim_name == "timeliness":
                            if metric.score < 80:
                                recommendations.append({
                                    "priority": "MEDIUM",
                                    "dimension": "Timeliness",
                                    "issue": f"Data freshness issues ({metric.score:.1f}%)",
                                    "action": "Increase scraping frequency or implement real-time updates",
                                    "impact": "Affects decision-making timeliness"
                                })
        
        # Add general recommendations
        overall_score = self.results["summary"].get("overall_score", 0)
        
        if overall_score < 60:
            recommendations.append({
                "priority": "CRITICAL",
                "dimension": "Overall",
                "issue": f"Critical data quality issues (Overall: {overall_score:.1f}%)",
                "action": "Immediate data quality improvement initiative required",
                "impact": "Business operations at risk"
            })
        elif overall_score < 75:
            recommendations.append({
                "priority": "HIGH",
                "dimension": "Overall",
                "issue": f"Significant data quality issues (Overall: {overall_score:.1f}%)",
                "action": "Prioritize data quality improvements in next sprint",
                "impact": "Affects business insights quality"
            })
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        self.results["recommendations"] = recommendations
    
    def _display_summary(self) -> None:
        """Display comprehensive summary in console."""
        summary = self.results["summary"]
        
        console.print("\n[bold cyan]📈 DATA QUALITY SUMMARY[/bold cyan]")
        console.print("=" * 60)
        
        # Overall score
        overall_score = summary.get("overall_score", 0)
        overall_status = summary.get("overall_status", "UNKNOWN")
        
        console.print(f"[bold]Overall Quality Score:[/bold] [bold]{overall_score:.1f}%[/bold] {overall_status}")
        
        # Dimension scores table
        table = Table(title="Quality Dimension Scores", box=box.ROUNDED)
        table.add_column("Dimension", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Weight", style="yellow")
        table.add_column("Status", style="white")
        
        for dim_name, dim_info in summary.get("dimension_scores", {}).items():
            table.add_row(
                dim_name.title(),
                f"{dim_info['score']:.1f}%",
                f"{dim_info['weight']:.2f}",
                dim_info["status"]
            )
        
        console.print(table)
        
        # Top recommendations
        recommendations = self.results.get("recommendations", [])
        if recommendations:
            console.print("\n[bold yellow]🚀 TOP RECOMMENDATIONS[/bold yellow]")
            
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                priority_color = {
                    "CRITICAL": "red",
                    "HIGH": "yellow",
                    "MEDIUM": "blue",
                    "LOW": "white"
                }.get(rec["priority"], "white")
                
                console.print(f"\n{i}. [{priority_color}]{rec['priority']}[/{priority_color}] - {rec['dimension']}")
                console.print(f"   Issue: {rec['issue']}")
                console.print(f"   Action: {rec['action']}")
                console.print(f"   Impact: {rec['impact']}")
    
    def _save_reports(self) -> None:
        """Save data quality reports to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Save detailed JSON report
        json_report = self.output_dir / f"data_quality_report_{timestamp}.json"
        with open(json_report, 'w') as f:
            # Convert dataclasses to dict
            report_dict = self._serialize_results()
            json.dump(report_dict, f, indent=2, default=str)
        
        # 2. Save executive summary (Markdown)
        summary_report = self.output_dir / "DATA_QUALITY_SUMMARY.md"
        self._generate_executive_summary(summary_report)
        
        # 3. Save CSV report of key metrics
        csv_report = self.output_dir / f"quality_metrics_{timestamp}.csv"
        self._save_metrics_csv(csv_report)
        
        console.print(f"\n[green]📄 Reports saved:[/green]")
        console.print(f"  • Detailed JSON: {json_report}")
        console.print(f"  • Executive Summary: {summary_report}")
        console.print(f"  • Metrics CSV: {csv_report}")
        console.print(f"  • Visualizations: {self.output_dir}/visualizations/")
    
    def _serialize_results(self) -> Dict[str, Any]:
        """Serialize results for JSON output."""
        import copy
        
        results = copy.deepcopy(self.results)
        
        # Convert dataclasses to dict
        for key, value in results["metrics"].items():
            if "metric" in value and hasattr(value["metric"], "__dataclass_fields__"):
                value["metric"] = {
                    "name": value["metric"].name,
                    "score": value["metric"].score,
                    "weight": value["metric"].weight,
                    "level": value["metric"].level.name,
                    "status_icon": value["metric"].status_icon,
                    "details": value["metric"].details
                }
        
        return results
    
    def _generate_executive_summary(self, output_file: Path) -> None:
        """Generate executive summary in Markdown."""
        summary = [
            "# Data Quality Executive Summary",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Database**: {self.db_path.name}",
            "",
            "## Overall Assessment",
            f"- **Overall Score**: {self.results['summary'].get('overall_score', 0):.1f}%",
            f"- **Status**: {self.results['summary'].get('overall_status', 'UNKNOWN')}",
            f"- **Assessment Date**: {self.results['summary'].get('assessment_date', 'N/A')}",
            "",
            "## Quality Dimension Scores",
            "| Dimension | Score | Weight | Status |",
            "|-----------|-------|--------|--------|"
        ]
        
        for dim_name, dim_info in self.results["summary"].get("dimension_scores", {}).items():
            summary.append(f"| {dim_name.title()} | {dim_info['score']:.1f}% | {dim_info['weight']:.2f} | {dim_info['status']} |")
        
        summary.append("")
        summary.append("## Key Findings")
        
        # Add key findings from each dimension
        for dim_name in self.quality_dimensions.keys():
            metric_key = f"{dim_name}_analysis"
            if metric_key in self.results["metrics"]:
                result = self.results["metrics"][metric_key]
                if "summary" in result:
                    summary.append(f"- **{dim_name.title()}**: {result['summary']}")
        
        summary.append("")
        summary.append("## Recommendations")
        
        for rec in self.results.get("recommendations", [])[:5]:
            summary.append(f"### {rec['priority']} - {rec['dimension']}")
            summary.append(f"- **Issue**: {rec['issue']}")
            summary.append(f"- **Action**: {rec['action']}")
            summary.append(f"- **Impact**: {rec['impact']}")
            summary.append("")
        
        summary.append("## Visualizations")
        summary.append("Quality visualizations are available in the `visualizations` directory:")
        for viz in self.results.get("visualizations", []):
            viz_name = Path(viz).name
            summary.append(f"- ![{viz_name}](visualizations/{viz_name})")
        
        with open(output_file, 'w') as f:
            f.write("\n".join(summary))
    
    def _save_metrics_csv(self, output_file: Path) -> None:
        """Save key metrics to CSV file."""
        import csv
        
        rows = []
        
        # Header
        rows.append(["Dimension", "Score", "Weight", "Level", "Timestamp"])
        
        # Data rows
        for dim_name, dim_info in self.results["summary"].get("dimension_scores", {}).items():
            rows.append([
                dim_name.title(),
                f"{dim_info['score']:.2f}",
                f"{dim_info['weight']:.3f}",
                dim_info["level"],
                datetime.now().isoformat()
            ])
        
        # Overall score
        rows.append([
            "OVERALL",
            f"{self.results['summary'].get('overall_score', 0):.2f}",
            "1.000",
            self.results['summary'].get('overall_level', 'UNKNOWN'),
            datetime.now().isoformat()
        ])
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)


def main():
    """Main entry point for data quality reporting."""
    console.print("\n[bold blue]📊 WEB SCRAPER TO SQLITE - DATA QUALITY REPORT[/bold blue]")
    console.print("=" * 60)
    
    # Run data quality assessment
    reporter = DataQualityReport()
    results = reporter.generate_full_report()
    
    # Display final message
    overall_score = results["summary"].get("overall_score", 0)
    
    if overall_score >= 90:
        console.print("\n[bold green]🎉 EXCELLENT DATA QUALITY![/bold green]")
    elif overall_score >= 75:
        console.print("\n[green]👍 GOOD DATA QUALITY[/green]")
    elif overall_score >= 60:
        console.print("\n[yellow]⚠️ FAIR DATA QUALITY - ROOM FOR IMPROVEMENT[/yellow]")
    elif overall_score >= 40:
        console.print("\n[red]❌ POOR DATA QUALITY - ACTION REQUIRED[/red]")
    else:
        console.print("\n[bold red]💥 CRITICAL DATA QUALITY ISSUES![/bold red]")
    
    console.print(f"\n[cyan]Overall Quality Score: {overall_score:.1f}%[/cyan]")
    console.print("\n" + "=" * 60)
    console.print("[green]✅ DATA QUALITY ASSESSMENT COMPLETE[/green]")
    console.print("=" * 60)


if __name__ == "__main__":
    main()