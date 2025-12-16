import os
from datetime import datetime, timedelta
from pathlib import Path

# ========== PROJECT PATHS ==========
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUT_CHARTS = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_REPORTS = PROJECT_ROOT / "outputs" / "reports"
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for directory in [DATA_RAW, DATA_PROCESSED, OUTPUT_CHARTS, OUTPUT_REPORTS, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ========== API CONFIGURATION ==========
# Free Financial APIs - No keys required for basic data.
YFINANCE_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]  # Equity tickers
FRED_SERIES = {
    "DGS10": "10-Year Treasury Constant Maturity Rate",
    "UNRATE": "Unemployment Rate",
    "CPIAUCSL": "Consumer Price Index"
}

# ========== ANALYSIS PARAMETERS ==========
ANALYSIS_START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
ANALYSIS_END_DATE = datetime.now().strftime('%Y-%m-%d')
MOVING_AVERAGE_WINDOW = 20  # Days for trend calculation
PRIMARY_CURRENCY = "USD"

# ========== REPORT CONFIGURATION ==========
REPORT_TITLE = "Financial Market Analysis Report"
REPORT_AUTHOR = "Data Analytics Team"
COMPANY_NAME = "Quantitative Insights"
REPORT_FOOTER_TEXT = f"Confidential - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# ========== VISUALIZATION STYLING ==========
CHART_STYLE = "seaborn-v0_8-darkgrid"
COLOR_PALETTE = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#6A994E"]
FIG_SIZE = (10, 6)
DPI = 300

# ========== LOGGING CONFIGURATION ==========
LOG_FILE = LOG_DIR / "execution.log"
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"