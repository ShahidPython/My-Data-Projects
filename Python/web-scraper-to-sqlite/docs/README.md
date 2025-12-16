Web Scraper to SQLite - Professional ETL Pipeline

https://img.shields.io/badge/Python-3.9+-blue.svg
https://img.shields.io/badge/License-MIT-yellow.svg
https://img.shields.io/badge/code%2520style-black-000000.svg

A production-ready ETL pipeline that extracts e-commerce data from HTML, transforms it with data cleaning/validation, and loads it into SQLite database for analytics. Built with enterprise-grade architecture and best practices.
🚀 Features

    Professional Web Scraping: Async/await support, caching, rate limiting, error handling

    Data Cleaning Pipeline: Automated data validation, outlier detection, type conversion

    SQLite Database: Schema management, indexing, backup/restore, query optimization

    Production Monitoring: Comprehensive logging, performance metrics, pipeline statistics

    CLI Interface: Command-line arguments, dry-run mode, verbose output

    Extensible Architecture: Modular design, configuration management, test coverage

📁 Project Structure
text

web-scraper-to-sqlite/
├── src/
│   ├── scraper.py          # Web scraper with async support
│   ├── data_cleaner.py     # Data transformation & validation
│   ├── database_handler.py # SQLite database operations
│   ├── cli.py             # Command-line interface
│   └── __init__.py
├── data/
│   ├── input/             # Sample HTML files
│   ├── output/            # Exported CSV files
│   ├── cache/             # Cached web content
│   └── scraped_data.db    # SQLite database
├── logs/
│   ├── scraper.log
│   └── pipeline_stats.json
├── tests/
│   ├── test_scraper.py
│   ├── test_data_cleaner.py
│   └── test_database_handler.py
├── config.yaml           # Configuration file
├── main.py              # Main pipeline entry point
├── requirements.txt     # Dependencies
├── Dockerfile          # Containerization
├── Makefile           # Build automation
└── README.md          # This file

🛠️ Installation
bash

# Clone repository
git clone https://github.com/yourusername/web-scraper-to-sqlite.git
cd web-scraper-to-sqlite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

📊 Quick Start
bash

# Run pipeline with sample data
python main.py

# With custom options
python main.py --url ./data/input/example.html --output data/products.db --limit 20 --verbose

⚙️ Configuration
Command Line Options
bash

python main.py --help

Option	Description	Default
--url	Target URL or file path	./data/input/example.html
--output	Output SQLite database path	data/scraped_data.db
--table	Target table name	scraped_records
--limit	Limit records to scrape	No limit
--verbose	Enable verbose logging	False
--dry-run	Run without saving to database	False
--config	Configuration file path	config.yaml
Sample HTML Structure

The scraper expects this HTML structure (see data/input/example.html):
html

<div class="product-card">
    <h3 class="product-title">Product Name</h3>
    <p class="product-price">$29.99</p>
    <span class="product-category">Electronics</span>
    <div class="product-rating">⭐⭐⭐⭐ (4.2)</div>
    <span class="product-stock">In Stock (45 units)</span>
    <p class="product-description">Product description...</p>
</div>

🔧 Advanced Usage
1. Custom Scraping Selectors

Create custom_config.yaml:
yaml

scraping:
  selectors:
    container: '.product-item'
    title: '.item-title'
    price: '.item-price'
    category: '.item-category'
  cache_enabled: true
  max_concurrent: 10

bash

python main.py --config custom_config.yaml --url https://example.com/products

2. Database Query Examples
bash

# Export to CSV
sqlite3 -header -csv data/scraped_data.db \
  "SELECT title, price, category FROM scraped_records WHERE price > 100" \
  > data/output/expensive_products.csv

# Run SQL queries
python -c "
from src.database_handler import DatabaseHandler
db = DatabaseHandler()
query = 'SELECT AVG(price) as avg_price, COUNT(*) as count FROM scraped_records'
result = db.execute_query(query)
print(result)
db.close_connection()
"

3. Performance Testing
bash

# Run performance tests
python performance_test.py

# Generate data quality report
python data_quality_report.py

📈 Pipeline Architecture
text

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EXTRACTION    │    │ TRANSFORMATION  │    │     LOADING     │
│                 │    │                 │    │                 │
│  • HTML Parsing ├───►• Data Cleaning  ├───►• Schema Creation │
│  • CSS Selectors│    • Type Conversion│    • Bulk Insert     │
│  • Async Fetch  │    • Outlier Detect │    • Index Creation  │
│  • Caching      │    • Validation     │    • Query Execution │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MONITORING & LOGGING                         │
│              • Performance Metrics • Error Tracking              │
│              • Pipeline Statistics • Audit Logs                  │
└─────────────────────────────────────────────────────────────────┘

🧪 Testing
bash

# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_scraper.py -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html

🐳 Docker Support
bash

# Build Docker image
docker build -t web-scraper-sqlite .

# Run container
docker run -v $(pwd)/data:/app/data web-scraper-sqlite \
  python main.py --url ./data/input/example.html

# Use Docker Compose
docker-compose up

📊 Output Schema

The database table includes:
Column	Type	Description
id	INTEGER PRIMARY KEY	Auto-increment ID
title	TEXT NOT NULL	Product name
price	REAL	Product price
category	TEXT	Product category
rating	REAL	Customer rating (1-5)
stock	TEXT	Stock status
description	TEXT	Product description
sku	TEXT	Stock keeping unit
date_added	TEXT	Date added to catalog
_container_index	INTEGER	HTML container index
_scrape_timestamp	TEXT	When data was scraped
featured	INTEGER	Is featured product (0/1)
card_type	TEXT	HTML card class
discounted	INTEGER	Is discounted (0/1)
created_at	TIMESTAMP	Record creation timestamp
📈 Performance Metrics

Typical performance on consumer hardware:

    Extraction Rate: 200-300 records/second

    Memory Usage: < 100 MB for 10,000 records

    Database Insert: 1000 records/second

    Cache Hit Rate: 60-80% (with TTL enabled)

🔍 Troubleshooting
Issue	Solution
"No such table" error	Delete data/scraped_data.db and rerun
Column mismatch error	Update schema in database_handler.py
HTML parsing fails	Check selectors in config.yaml
Memory issues	Use --limit to reduce batch size
Slow performance	Enable caching in config
🤝 Contributing

    Fork the repository

    Create feature branch: git checkout -b feature-name

    Commit changes: git commit -am 'Add feature'

    Push to branch: git push origin feature-name

    Submit Pull Request

📄 License

MIT License - see LICENSE file for details.
🙏 Acknowledgments

    Built with BeautifulSoup for HTML parsing

    Pandas for data manipulation

    SQLite for embedded database

    Pytest for testing framework

📞 Support

For issues, questions, or contributions:

    Check Troubleshooting section

    Open a GitHub Issue

    Review example configurations in docs/

⭐ Star this repo if you found it useful!

Last updated: December 2024 | Version: 1.0.0