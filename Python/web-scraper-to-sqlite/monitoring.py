import time
import json
import sqlite3
import psutil
import logging
import threading
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import hashlib
import socket
import requests
from prometheus_client import start_http_server, Gauge, Counter, Histogram, Summary, Info
from rich.console import Console
from rich.table import Table
from rich import box
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
import warnings
warnings.filterwarnings('ignore')

# Setup console
console = Console()


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SystemStatus(Enum):
    """System status levels."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    OFFLINE = "OFFLINE"


@dataclass
class Alert:
    """Monitoring alert."""
    id: str
    severity: AlertSeverity
    message: str
    component: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Generate ID if not provided."""
        if not self.id:
            content = f"{self.severity.value}-{self.component}-{self.message}-{self.timestamp.isoformat()}"
            self.id = hashlib.md5(content.encode()).hexdigest()[:8]
        
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Metric:
    """System metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}


class MonitoringSystem:
    """Production monitoring and observability system."""
    
    def __init__(self, config_path: str = "monitoring_config.yaml", port: int = 9090):
        """Initialize monitoring system."""
        self.config = self._load_config(config_path)
        self.port = port
        
        # Setup directories
        self.data_dir = Path("monitoring_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # State management
        self.alerts = deque(maxlen=1000)  # Store last 1000 alerts
        self.metrics = deque(maxlen=5000)  # Store last 5000 metrics
        self.system_status = SystemStatus.HEALTHY
        self.last_check = datetime.now()
        
        # Alert thresholds
        self.thresholds = {
            "cpu_percent": 80.0,      # Alert if > 80%
            "memory_percent": 85.0,   # Alert if > 85%
            "disk_percent": 90.0,     # Alert if > 90%
            "error_rate": 5.0,        # Alert if > 5%
            "latency_ms": 1000.0,     # Alert if > 1 second
            "scrape_failure_rate": 10.0,  # Alert if > 10%
            "data_freshness_hours": 24.0,  # Alert if data > 24 hours old
        }
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Start monitoring threads
        self.running = False
        self.threads = []
        
        console.print("\n[bold blue]🔍 PRODUCTION MONITORING SYSTEM[/bold blue]")
        console.print("=" * 60)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load monitoring configuration."""
        config_file = Path(config_path)
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f)
            except:
                pass
        
        # Default configuration
        return {
            "monitoring": {
                "interval_seconds": 30,
                "retention_days": 30,
                "alert_channels": {
                    "console": True,
                    "log_file": True,
                    "email": False,
                    "slack": False
                }
            },
            "endpoints": {
                "health": "/health",
                "metrics": "/metrics",
                "alerts": "/alerts"
            }
        }
    
    def _setup_logging(self) -> None:
        """Setup monitoring logging."""
        log_file = self.data_dir / "monitoring.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def _init_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        # System metrics
        self.cpu_usage = Gauge('system_cpu_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('system_memory_percent', 'Memory usage percentage')
        self.disk_usage = Gauge('system_disk_percent', 'Disk usage percentage')
        self.process_count = Gauge('system_process_count', 'Number of running processes')
        
        # Application metrics
        self.scrape_requests = Counter('scrape_requests_total', 'Total scrape requests')
        self.scrape_errors = Counter('scrape_errors_total', 'Total scrape errors')
        self.scrape_duration = Histogram('scrape_duration_seconds', 'Scrape duration in seconds')
        self.data_records = Gauge('data_records_total', 'Total data records in database')
        self.data_freshness = Gauge('data_freshness_hours', 'Data freshness in hours')
        
        # Quality metrics
        self.data_quality_score = Gauge('data_quality_score', 'Overall data quality score (0-100)')
        self.completeness_score = Gauge('data_completeness_score', 'Data completeness score (0-100)')
        self.accuracy_score = Gauge('data_accuracy_score', 'Data accuracy score (0-100)')
        
        # Alert metrics
        self.active_alerts = Gauge('active_alerts_total', 'Number of active alerts')
        self.alert_events = Counter('alert_events_total', 'Total alert events')
        
        # System info
        self.system_info = Info('system_info', 'System information')
        self.system_info.info({
            'version': '1.0.0',
            'monitoring_enabled': 'true'
        })
    
    def start(self) -> None:
        """Start the monitoring system."""
        self.running = True
        
        # Start Prometheus metrics server
        console.print(f"[cyan]Starting metrics server on port {self.port}...[/cyan]")
        start_http_server(self.port)
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self._monitor_system_resources, daemon=True),
            threading.Thread(target=self._monitor_database, daemon=True),
            threading.Thread(target=self._monitor_data_quality, daemon=True),
            threading.Thread(target=self._monitor_scraping_pipeline, daemon=True),
            threading.Thread(target=self._check_alert_thresholds, daemon=True),
            threading.Thread(target=self._cleanup_old_data, daemon=True),
        ]
        
        for thread in threads:
            thread.start()
            self.threads.append(thread)
        
        console.print("[green]✅ Monitoring system started[/green]")
        console.print(f"[yellow]📊 Metrics available at: http://localhost:{self.port}/metrics[/yellow]")
        
        # Start dashboard if requested
        if self.config.get("monitoring", {}).get("dashboard", True):
            threading.Thread(target=self._start_dashboard, daemon=True).start()
    
    def stop(self) -> None:
        """Stop the monitoring system."""
        self.running = False
        console.print("\n[cyan]Stopping monitoring system...[/cyan]")
        
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        console.print("[green]✅ Monitoring system stopped[/green]")
    
    def _monitor_system_resources(self) -> None:
        """Monitor system resources (CPU, memory, disk)."""
        console.print("[white]Monitoring system resources...[/white]")
        
        while self.running:
            try:
                timestamp = datetime.now()
                
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_usage.set(cpu_percent)
                self._record_metric("system.cpu.percent", cpu_percent, "%", timestamp)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self.memory_usage.set(memory_percent)
                self._record_metric("system.memory.percent", memory_percent, "%", timestamp)
                self._record_metric("system.memory.used", memory.used / (1024**3), "GB", timestamp)
                self._record_metric("system.memory.total", memory.total / (1024**3), "GB", timestamp)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                self.disk_usage.set(disk_percent)
                self._record_metric("system.disk.percent", disk_percent, "%", timestamp)
                self._record_metric("system.disk.used", disk.used / (1024**9), "GB", timestamp)
                self._record_metric("system.disk.total", disk.total / (1024**9), "GB", timestamp)
                
                # Process count
                process_count = len(list(psutil.process_iter()))
                self.process_count.set(process_count)
                self._record_metric("system.processes.count", process_count, "count", timestamp)
                
                # Network connections
                connections = len(psutil.net_connections())
                self._record_metric("system.network.connections", connections, "count", timestamp)
                
                # Check thresholds
                if cpu_percent > self.thresholds["cpu_percent"]:
                    self._create_alert(
                        severity=AlertSeverity.WARNING,
                        message=f"High CPU usage: {cpu_percent:.1f}%",
                        component="system"
                    )
                
                if memory_percent > self.thresholds["memory_percent"]:
                    self._create_alert(
                        severity=AlertSeverity.WARNING,
                        message=f"High memory usage: {memory_percent:.1f}%",
                        component="system"
                    )
                
                if disk_percent > self.thresholds["disk_percent"]:
                    self._create_alert(
                        severity=AlertSeverity.WARNING,
                        message=f"High disk usage: {disk_percent:.1f}%",
                        component="system"
                    )
                
            except Exception as e:
                self.logger.error(f"System monitoring error: {e}")
            
            time.sleep(self.config.get("monitoring", {}).get("interval_seconds", 30))
    
    def _monitor_database(self) -> None:
        """Monitor database health and metrics."""
        console.print("[white]Monitoring database...[/white]")
        
        db_path = Path("data/scraped_data.db")
        
        while self.running:
            try:
                if not db_path.exists():
                    time.sleep(30)
                    continue
                
                timestamp = datetime.now()
                
                # Connect to database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get table counts
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                total_records = 0
                for table in tables:
                    table_name = table[0]
                    if not table_name.startswith('sqlite_'):
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                        count = cursor.fetchone()[0]
                        total_records += count
                        
                        # Record table-specific metric
                        self._record_metric(
                            f"database.table.{table_name}.records",
                            count,
                            "count",
                            timestamp,
                            {"table": table_name}
                        )
                
                # Update Prometheus metric
                self.data_records.set(total_records)
                self._record_metric("database.records.total", total_records, "count", timestamp)
                
                # Check data freshness
                if "scraped_records" in [t[0] for t in tables]:
                    cursor.execute("""
                        SELECT MAX(scraped_at) FROM scraped_records 
                        WHERE scraped_at IS NOT NULL;
                    """)
                    result = cursor.fetchone()[0]
                    
                    if result:
                        try:
                            latest_scrape = datetime.fromisoformat(result.replace('Z', '+00:00'))
                            freshness_hours = (datetime.now() - latest_scrape).total_seconds() / 3600
                            self.data_freshness.set(freshness_hours)
                            self._record_metric("database.data.freshness", freshness_hours, "hours", timestamp)
                            
                            # Check freshness threshold
                            if freshness_hours > self.thresholds["data_freshness_hours"]:
                                self._create_alert(
                                    severity=AlertSeverity.WARNING,
                                    message=f"Data is stale: {freshness_hours:.1f} hours old",
                                    component="database"
                                )
                        except:
                            pass
                
                # Get database size
                db_size_mb = db_path.stat().st_size / (1024 * 1024)
                self._record_metric("database.size", db_size_mb, "MB", timestamp)
                
                # Check for database errors
                try:
                    cursor.execute("PRAGMA integrity_check;")
                    integrity_check = cursor.fetchone()[0]
                    if integrity_check != "ok":
                        self._create_alert(
                            severity=AlertSeverity.CRITICAL,
                            message=f"Database integrity check failed: {integrity_check}",
                            component="database"
                        )
                except:
                    pass
                
                conn.close()
                
            except Exception as e:
                self.logger.error(f"Database monitoring error: {e}")
                self._create_alert(
                    severity=AlertSeverity.ERROR,
                    message=f"Database monitoring failed: {str(e)}",
                    component="database"
                )
            
            time.sleep(60)  # Check database every minute
    
    def _monitor_data_quality(self) -> None:
        """Monitor data quality metrics."""
        console.print("[white]Monitoring data quality...[/white]")
        
        while self.running:
            try:
                timestamp = datetime.now()
                db_path = Path("data/scraped_data.db")
                
                if not db_path.exists():
                    time.sleep(60)
                    continue
                
                conn = sqlite3.connect(db_path)
                
                # Calculate basic quality metrics
                quality_metrics = self._calculate_quality_metrics(conn)
                
                # Update Prometheus metrics
                if "overall_score" in quality_metrics:
                    self.data_quality_score.set(quality_metrics["overall_score"])
                
                if "completeness" in quality_metrics:
                    self.completeness_score.set(quality_metrics["completeness"])
                
                if "accuracy" in quality_metrics:
                    self.accuracy_score.set(quality_metrics["accuracy"])
                
                # Record all metrics
                for metric_name, value in quality_metrics.items():
                    self._record_metric(f"data.quality.{metric_name}", value, "percent", timestamp)
                
                # Check quality thresholds
                if quality_metrics.get("overall_score", 100) < 70:
                    self._create_alert(
                        severity=AlertSeverity.WARNING,
                        message=f"Low data quality score: {quality_metrics['overall_score']:.1f}%",
                        component="data_quality"
                    )
                
                conn.close()
                
            except Exception as e:
                self.logger.error(f"Data quality monitoring error: {e}")
            
            time.sleep(300)  # Check data quality every 5 minutes
    
    def _calculate_quality_metrics(self, conn: sqlite3.Connection) -> Dict[str, float]:
        """Calculate data quality metrics."""
        metrics = {}
        
        try:
            # Check if main table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scraped_records';")
            if not cursor.fetchone():
                return {"overall_score": 0, "completeness": 0, "accuracy": 0}
            
            # Load data
            df = pd.read_sql_query("SELECT * FROM scraped_records LIMIT 1000", conn)
            
            if len(df) == 0:
                return {"overall_score": 0, "completeness": 0, "accuracy": 0}
            
            # 1. Completeness (missing values)
            total_cells = df.size
            missing_cells = df.isna().sum().sum()
            completeness = 100 * (1 - missing_cells / total_cells) if total_cells > 0 else 0
            metrics["completeness"] = completeness
            
            # 2. Accuracy (valid values)
            accuracy_scores = []
            
            # Price accuracy
            if "price" in df.columns:
                valid_prices = ((df["price"] >= 0) & (df["price"] <= 100000)).sum()
                total_prices = len(df["price"].dropna())
                if total_prices > 0:
                    accuracy_scores.append(100 * valid_prices / total_prices)
            
            # Date accuracy
            if "date" in df.columns:
                valid_dates = pd.to_datetime(df["date"], errors='coerce').notna().sum()
                total_dates = len(df["date"].dropna())
                if total_dates > 0:
                    accuracy_scores.append(100 * valid_dates / total_dates)
            
            accuracy = np.mean(accuracy_scores) if accuracy_scores else 100
            metrics["accuracy"] = accuracy
            
            # 3. Uniqueness (duplicates)
            total_records = len(df)
            duplicates = df.duplicated().sum()
            uniqueness = 100 * (1 - duplicates / total_records) if total_records > 0 else 100
            metrics["uniqueness"] = uniqueness
            
            # Calculate overall score (weighted)
            weights = {"completeness": 0.4, "accuracy": 0.4, "uniqueness": 0.2}
            overall_score = sum(metrics.get(k, 0) * weights.get(k, 0) for k in weights.keys())
            metrics["overall_score"] = overall_score
            
        except Exception as e:
            self.logger.error(f"Quality calculation error: {e}")
            metrics = {"overall_score": 0, "completeness": 0, "accuracy": 0, "error": str(e)}
        
        return metrics
    
    def _monitor_scraping_pipeline(self) -> None:
        """Monitor scraping pipeline performance."""
        console.print("[white]Monitoring scraping pipeline...[/white]")
        
        log_file = Path("logs/scraper.log")
        last_position = 0
        
        while self.running:
            try:
                if log_file.exists():
                    # Read new log entries
                    with open(log_file, 'r') as f:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        last_position = f.tell()
                    
                    # Parse log entries for scraping metrics
                    scrape_success = 0
                    scrape_errors = 0
                    scrape_durations = []
                    
                    for line in new_lines:
                        if "Scraping" in line or "scrape" in line.lower():
                            self.scrape_requests.inc()
                        
                        if "ERROR" in line and ("scrape" in line.lower() or "Scraping" in line):
                            scrape_errors += 1
                            self.scrape_errors.inc()
                        
                        if "successfully extracted" in line.lower():
                            scrape_success += 1
                        
                        if "execution time" in line.lower():
                            # Extract duration from log
                            import re
                            match = re.search(r'(\d+\.\d+) seconds', line)
                            if match:
                                duration = float(match.group(1))
                                scrape_durations.append(duration)
                                self.scrape_duration.observe(duration)
                    
                    # Calculate error rate
                    total_scrapes = scrape_success + scrape_errors
                    if total_scrapes > 0:
                        error_rate = 100 * scrape_errors / total_scrapes
                        self._record_metric("scraping.error_rate", error_rate, "percent", datetime.now())
                        
                        # Check error rate threshold
                        if error_rate > self.thresholds["error_rate"]:
                            self._create_alert(
                                severity=AlertSeverity.ERROR,
                                message=f"High scraping error rate: {error_rate:.1f}%",
                                component="scraping_pipeline"
                            )
                    
                    # Record average duration
                    if scrape_durations:
                        avg_duration = np.mean(scrape_durations)
                        self._record_metric("scraping.duration.avg", avg_duration * 1000, "ms", datetime.now())
                        
                        if avg_duration > self.thresholds["latency_ms"] / 1000:
                            self._create_alert(
                                severity=AlertSeverity.WARNING,
                                message=f"High scraping latency: {avg_duration:.1f}s",
                                component="scraping_pipeline"
                            )
                
            except Exception as e:
                self.logger.error(f"Scraping pipeline monitoring error: {e}")
            
            time.sleep(30)
    
    def _check_alert_thresholds(self) -> None:
        """Check all alert thresholds periodically."""
        console.print("[white]Monitoring alert thresholds...[/white]")
        
        while self.running:
            try:
                # Check for unresolved critical alerts
                critical_alerts = [
                    alert for alert in self.alerts 
                    if alert.severity == AlertSeverity.CRITICAL and not alert.resolved
                ]
                
                if len(critical_alerts) > 3:
                    self._create_alert(
                        severity=AlertSeverity.CRITICAL,
                        message=f"Too many critical alerts: {len(critical_alerts)}",
                        component="monitoring"
                    )
                
                # Update system status based on alerts
                self._update_system_status()
                
            except Exception as e:
                self.logger.error(f"Alert threshold check error: {e}")
            
            time.sleep(60)
    
    def _cleanup_old_data(self) -> None:
        """Cleanup old monitoring data."""
        console.print("[white]Cleaning up old monitoring data...[/white]")
        
        retention_days = self.config.get("monitoring", {}).get("retention_days", 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        while self.running:
            try:
                # Cleanup old metrics
                self.metrics = deque(
                    [m for m in self.metrics if m.timestamp > cutoff_date],
                    maxlen=5000
                )
                
                # Cleanup old alerts (keep resolved alerts for 7 days)
                alert_cutoff = datetime.now() - timedelta(days=7)
                self.alerts = deque(
                    [a for a in self.alerts if not (a.resolved and a.timestamp < alert_cutoff)],
                    maxlen=1000
                )
                
                # Save current state
                self._save_state()
                
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
            
            time.sleep(3600)  # Run cleanup every hour
    
    def _create_alert(self, severity: AlertSeverity, message: str, component: str, 
                     metadata: Dict[str, Any] = None) -> None:
        """Create and store a new alert."""
        alert = Alert(
            id="",
            severity=severity,
            message=message,
            component=component,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        self.alert_events.inc()
        self.active_alerts.set(len([a for a in self.alerts if not a.resolved]))
        
        # Log alert based on severity
        if severity == AlertSeverity.CRITICAL:
            self.logger.critical(f"🚨 CRITICAL ALERT [{component}]: {message}")
        elif severity == AlertSeverity.ERROR:
            self.logger.error(f"❌ ERROR ALERT [{component}]: {message}")
        elif severity == AlertSeverity.WARNING:
            self.logger.warning(f"⚠️  WARNING ALERT [{component}]: {message}")
        else:
            self.logger.info(f"ℹ️  INFO ALERT [{component}]: {message}")
        
        # Send to alert channels
        self._send_alert_notification(alert)
    
    def _send_alert_notification(self, alert: Alert) -> None:
        """Send alert notification through configured channels."""
        channels = self.config.get("monitoring", {}).get("alert_channels", {})
        
        # Console notification
        if channels.get("console", True):
            severity_colors = {
                AlertSeverity.CRITICAL: "red",
                AlertSeverity.ERROR: "red",
                AlertSeverity.WARNING: "yellow",
                AlertSeverity.INFO: "blue"
            }
            
            color = severity_colors.get(alert.severity, "white")
            console.print(f"[{color}]{alert.severity.value}[/{color}] [{alert.component}] {alert.message}")
        
        # Email notification (placeholder)
        if channels.get("email", False):
            # In production, integrate with email service
            pass
        
        # Slack notification (placeholder)
        if channels.get("slack", False):
            # In production, integrate with Slack webhook
            pass
    
    def _record_metric(self, name: str, value: float, unit: str, 
                      timestamp: datetime, labels: Dict[str, str] = None) -> None:
        """Record a new metric."""
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            timestamp=timestamp,
            labels=labels or {}
        )
        
        self.metrics.append(metric)
        
        # Save to time-series database (simplified)
        self._save_metric_to_tsdb(metric)
    
    def _save_metric_to_tsdb(self, metric: Metric) -> None:
        """Save metric to time-series database (simplified file-based)."""
        try:
            # Group metrics by hour for efficiency
            hour_key = metric.timestamp.strftime("%Y%m%d%H")
            tsdb_file = self.data_dir / f"tsdb_{hour_key}.jsonl"
            
            # Append metric to file
            with open(tsdb_file, 'a') as f:
                f.write(json.dumps({
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat(),
                    "labels": metric.labels
                }) + "\n")
                
        except Exception as e:
            self.logger.error(f"Failed to save metric to TSDB: {e}")
    
    def _update_system_status(self) -> None:
        """Update overall system status based on active alerts."""
        active_alerts = [a for a in self.alerts if not a.resolved]
        
        # Count alerts by severity
        critical_count = len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL])
        error_count = len([a for a in active_alerts if a.severity == AlertSeverity.ERROR])
        warning_count = len([a for a in active_alerts if a.severity == AlertSeverity.WARNING])
        
        # Determine system status
        if critical_count > 0:
            new_status = SystemStatus.UNHEALTHY
        elif error_count > 3 or warning_count > 10:
            new_status = SystemStatus.DEGRADED
        else:
            new_status = SystemStatus.HEALTHY
        
        # Update if status changed
        if new_status != self.system_status:
            old_status = self.system_status
            self.system_status = new_status
            
            self.logger.info(f"System status changed: {old_status.value} → {new_status.value}")
            
            # Create alert for status degradation
            if new_status in [SystemStatus.DEGRADED, SystemStatus.UNHEALTHY]:
                self._create_alert(
                    severity=AlertSeverity.WARNING,
                    message=f"System status changed to {new_status.value}",
                    component="system",
                    metadata={"old_status": old_status.value, "new_status": new_status.value}
                )
    
    def _save_state(self) -> None:
        """Save monitoring system state."""
        try:
            state_file = self.data_dir / "monitoring_state.json"
            
            state = {
                "system_status": self.system_status.value,
                "last_check": self.last_check.isoformat(),
                "active_alert_count": len([a for a in self.alerts if not a.resolved]),
                "total_metric_count": len(self.metrics),
                "thresholds": self.thresholds
            }
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def _start_dashboard(self) -> None:
        """Start real-time monitoring dashboard."""
        console.print("\n[yellow]📊 Starting real-time dashboard...[/yellow]")
        console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")
        
        try:
            with Live(refresh_per_second=1, screen=True) as live:
                while self.running:
                    live.update(self._create_dashboard())
                    time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Dashboard stopped[/yellow]")
        except Exception as e:
            console.print(f"[red]Dashboard error: {e}[/red]")
    
    def _create_dashboard(self) -> Panel:
        """Create real-time monitoring dashboard."""
        layout = Layout()
        
        # Split into sections
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Header
        header_content = f"[bold blue]📈 PRODUCTION MONITORING DASHBOARD[/bold blue] | Status: [{self._get_status_color()}]{self.system_status.value}[/{self._get_status_color()}] | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        layout["header"].update(Panel(header_content, border_style="blue"))
        
        # Main content
        main_layout = Layout()
        main_layout.split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        # Left panel: System metrics
        left_content = self._create_system_metrics_panel()
        main_layout["left"].update(Panel(left_content, title="System Metrics", border_style="green"))
        
        # Right panel: Alerts
        right_content = self._create_alerts_panel()
        main_layout["right"].update(Panel(right_content, title="Recent Alerts", border_style="yellow"))
        
        layout["main"].update(main_layout)
        
        # Footer
        active_alerts = len([a for a in self.alerts if not a.resolved])
        total_metrics = len(self.metrics)
        footer_content = f"Active Alerts: [red]{active_alerts}[/red] | Total Metrics: [cyan]{total_metrics}[/cyan] | Metrics Endpoint: [yellow]http://localhost:{self.port}/metrics[/yellow]"
        layout["footer"].update(Panel(footer_content, border_style="blue"))
        
        return Panel(layout, title="Web Scraper Monitoring", border_style="blue")
    
    def _create_system_metrics_panel(self) -> str:
        """Create system metrics panel content."""
        try:
            # Get current metrics (last 5 minutes)
            cutoff = datetime.now() - timedelta(minutes=5)
            recent_metrics = [m for m in self.metrics if m.timestamp > cutoff]
            
            # Group metrics by type
            metrics_by_name = {}
            for metric in recent_metrics:
                if metric.name not in metrics_by_name:
                    metrics_by_name[metric.name] = []
                metrics_by_name[metric.name].append(metric.value)
            
            # Create table
            table = Table(show_header=False, box=None)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Trend", style="yellow")
            
            # Add key metrics
            key_metrics = {
                "system.cpu.percent": "CPU",
                "system.memory.percent": "Memory",
                "system.disk.percent": "Disk",
                "database.records.total": "DB Records",
                "scraping.error_rate": "Error Rate",
                "data.quality.overall_score": "Data Quality"
            }
            
            for metric_key, display_name in key_metrics.items():
                if metric_key in metrics_by_name:
                    values = metrics_by_name[metric_key]
                    current = values[-1] if values else 0
                    avg = np.mean(values) if values else 0
                    
                    # Format value based on metric type
                    if "percent" in metric_key:
                        value_str = f"{current:.1f}%"
                        trend = "↗️" if current > avg + 5 else "↘️" if current < avg - 5 else "➡️"
                    elif "records" in metric_key:
                        value_str = f"{int(current):,}"
                        trend = "↗️" if current > avg else "↘️" if current < avg else "➡️"
                    else:
                        value_str = f"{current:.2f}"
                        trend = "↗️" if current > avg else "↘️" if current < avg else "➡️"
                    
                    table.add_row(display_name, value_str, trend)
            
            return table
            
        except Exception as e:
            return f"[red]Error: {e}[/red]"
    
    def _create_alerts_panel(self) -> str:
        """Create alerts panel content."""
        # Get recent unresolved alerts
        unresolved_alerts = [a for a in self.alerts if not a.resolved]
        recent_alerts = list(unresolved_alerts)[-5:]  # Last 5 alerts
        
        if not recent_alerts:
            return "[green]✅ No active alerts[/green]"
        
        # Create table
        table = Table(show_header=True, box=None)
        table.add_column("Time", style="dim", width=8)
        table.add_column("Severity", style="white")
        table.add_column("Component", style="cyan")
        table.add_column("Message", style="white")
        
        for alert in recent_alerts:
            time_str = alert.timestamp.strftime("%H:%M:%S")
            
            # Color code severity
            if alert.severity == AlertSeverity.CRITICAL:
                severity_str = "[red]CRIT[/red]"
            elif alert.severity == AlertSeverity.ERROR:
                severity_str = "[red]ERROR[/red]"
            elif alert.severity == AlertSeverity.WARNING:
                severity_str = "[yellow]WARN[/yellow]"
            else:
                severity_str = "[blue]INFO[/blue]"
            
            # Truncate message if too long
            message = alert.message
            if len(message) > 30:
                message = message[:27] + "..."
            
            table.add_row(time_str, severity_str, alert.component, message)
        
        return table
    
    def _get_status_color(self) -> str:
        """Get color for system status."""
        colors = {
            SystemStatus.HEALTHY: "green",
            SystemStatus.DEGRADED: "yellow",
            SystemStatus.UNHEALTHY: "red",
            SystemStatus.OFFLINE: "grey"
        }
        return colors.get(self.system_status, "white")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status for health checks."""
        active_alerts = [a for a in self.alerts if not a.resolved]
        critical_alerts = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        
        is_healthy = len(critical_alerts) == 0 and self.system_status != SystemStatus.UNHEALTHY
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "system_status": self.system_status.value,
            "active_alerts": len(active_alerts),
            "critical_alerts": len(critical_alerts),
            "checks": {
                "monitoring_system": "running",
                "database_connection": "connected" if Path("data/scraped_data.db").exists() else "disconnected",
                "metrics_endpoint": f"http://localhost:{self.port}/metrics"
            }
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for API."""
        # Get last hour of metrics
        cutoff = datetime.now() - timedelta(hours=1)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff]
        
        # Group and aggregate
        summary = {}
        for metric in recent_metrics:
            if metric.name not in summary:
                summary[metric.name] = {
                    "values": [],
                    "unit": metric.unit,
                    "labels": metric.labels
                }
            summary[metric.name]["values"].append(metric.value)
        
        # Calculate statistics
        for name, data in summary.items():
            values = data["values"]
            if values:
                data["count"] = len(values)
                data["min"] = min(values)
                data["max"] = max(values)
                data["avg"] = np.mean(values)
                data["latest"] = values[-1]
                del data["values"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics_count": len(recent_metrics),
            "summary": summary,
            "system_status": self.system_status.value
        }


def start_monitoring(port: int = 9090) -> MonitoringSystem:
    """Start the monitoring system."""
    monitor = MonitoringSystem(port=port)
    monitor.start()
    return monitor


def main():
    """Main entry point for monitoring system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Monitoring System")
    parser.add_argument("--port", type=int, default=9090, help="Metrics server port")
    parser.add_argument("--dashboard", action="store_true", help="Start dashboard")
    parser.add_argument("--health", action="store_true", help="Check system health")
    parser.add_argument("--metrics", action="store_true", help="Get metrics summary")
    
    args = parser.parse_args()
    
    if args.health:
        # Quick health check
        monitor = MonitoringSystem(port=args.port)
        health = monitor.get_health_status()
        console.print(json.dumps(health, indent=2))
        return
    
    if args.metrics:
        # Get metrics summary
        monitor = MonitoringSystem(port=args.port)
        metrics = monitor.get_metrics_summary()
        console.print(json.dumps(metrics, indent=2))
        return
    
    # Start full monitoring system
    monitor = start_monitoring(args.port)
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down monitoring system...[/yellow]")
        monitor.stop()


if __name__ == "__main__":
    # Import pandas and numpy for data quality monitoring
    import pandas as pd
    import numpy as np
    
    main()