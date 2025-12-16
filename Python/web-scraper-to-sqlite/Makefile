# Web Scraper to SQLite - Makefile for Development & Production
# =============================================================

# Variables
PYTHON = python3
PIP = pip3
VENV = venv
PYTEST = pytest
DOCKER = docker
DOCKER_COMPOSE = docker-compose
PROJECT_NAME = web-scraper-sqlite
PYTHONPATH = $(shell pwd)

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

# Help - Default target
.PHONY: help
help:
	@echo "$(GREEN)Web Scraper to SQLite - Available commands:$(NC)"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make install          Install dependencies in virtual environment"
	@echo "  make venv             Create virtual environment"
	@echo "  make test             Run all tests with coverage"
	@echo "  make lint             Run linting and code formatting"
	@echo "  make clean            Clean temporary files"
	@echo ""
	@echo "$(YELLOW)Running:$(NC)"
	@echo "  make run              Run the scraper with example data"
	@echo "  make run-dry          Dry run (no database changes)"
	@echo "  make run-prod         Run with production settings"
	@echo "  make scrape URL=...   Run scraper with custom URL"
	@echo ""
	@echo "$(YELLOW)Docker:$(NC)"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run in Docker container"
	@echo "  make compose-up       Start Docker Compose services"
	@echo "  make compose-down     Stop Docker Compose services"
	@echo ""
	@echo "$(YELLOW)Data & Analysis:$(NC)"
	@echo "  make data-clean       Clean all generated data"
	@echo "  make db-shell         Open SQLite shell"
	@echo "  make report           Generate data quality report"
	@echo ""
	@echo "$(YELLOW)Deployment:$(NC)"
	@echo "  make requirements     Freeze requirements"
	@echo "  make security         Run security checks"
	@echo "  make benchmark        Run performance benchmarks"
	@echo ""

# ====================
# DEVELOPMENT
# ====================

.PHONY: install
install: venv
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@$(VENV)/bin/pip install --upgrade pip
	@$(VENV)/bin/pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

.PHONY: venv
venv:
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created$(NC)"

.PHONY: test
test:
	@echo "$(GREEN)Running tests...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/$(PYTEST) tests/ -v --cov=src --cov-report=term --cov-report=html
	@echo "$(GREEN)✓ Tests completed$(NC)"

.PHONY: test-watch
test-watch:
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/$(PYTEST) tests/ -v --cov=src -f

.PHONY: lint
lint:
	@echo "$(GREEN)Running code formatting...$(NC)"
	@$(VENV)/bin/black src/ tests/ --check
	@echo "$(GREEN)Running linting...$(NC)"
	@$(VENV)/bin/flake8 src/ --max-line-length=88 --extend-ignore=E203
	@echo "$(GREEN)Running type checking...$(NC)"
	@$(VENV)/bin/mypy src/
	@echo "$(GREEN)✓ Code quality checks passed$(NC)"

.PHONY: format
format:
	@echo "$(GREEN)Formatting code...$(NC)"
	@$(VENV)/bin/black src/ tests/
	@$(VENV)/bin/isort src/ tests/
	@echo "$(GREEN)✓ Code formatted$(NC)"

.PHONY: clean
clean:
	@echo "$(GREEN)Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .benchmarks || true
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

# ====================
# RUNNING THE SCRAPER
# ====================

.PHONY: run
run:
	@echo "$(GREEN)Running scraper with example data...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/$(PYTHON) main.py --url file://./data/input/example.html --verbose
	@echo "$(GREEN)✓ Scraping completed$(NC)"

.PHONY: run-dry
run-dry:
	@echo "$(GREEN)Running dry run...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/$(PYTHON) main.py --url file://./data/input/example.html --dry-run --verbose

.PHONY: run-prod
run-prod:
	@echo "$(GREEN)Running with production settings...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/$(PYTHON) main.py --url https://example.com --output data/production.db --verbose

.PHONY: scrape
scrape:
ifndef URL
	$(error URL is not set. Usage: make scrape URL=https://example.com)
endif
	@echo "$(GREEN)Scraping $(URL)...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/$(PYTHON) main.py --url $(URL) --verbose

# ====================
# DOCKER COMMANDS
# ====================

.PHONY: docker-build
docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	@$(DOCKER) build -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)✓ Docker image built: $(PROJECT_NAME):latest$(NC)"

.PHONY: docker-run
docker-run:
	@echo "$(GREEN)Running in Docker...$(NC)"
	@$(DOCKER) run --rm -v $(shell pwd)/data:/app/data $(PROJECT_NAME):latest

.PHONY: docker-test
docker-test:
	@echo "$(GREEN)Running tests in Docker...$(NC)"
	@$(DOCKER) run --rm $(PROJECT_NAME):latest $(PYTEST) tests/ -v

.PHONY: compose-up
compose-up:
	@echo "$(GREEN)Starting Docker Compose services...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Services started. Run 'make compose-logs' to view logs.$(NC)"

.PHONY: compose-down
compose-down:
	@echo "$(GREEN)Stopping Docker Compose services...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

.PHONY: compose-logs
compose-logs:
	@$(DOCKER_COMPOSE) logs -f scraper

.PHONY: compose-restart
compose-restart:
	@$(DOCKER_COMPOSE) restart scraper

# ====================
# DATA & ANALYSIS
# ====================

.PHONY: data-clean
data-clean:
	@echo "$(GREEN)Cleaning generated data...$(NC)"
	@rm -rf data/scraped_data.db data/cache/* data/output/* logs/* 2>/dev/null || true
	@echo "$(GREEN)✓ Data cleaned$(NC)"

.PHONY: db-shell
db-shell:
	@echo "$(GREEN)Opening SQLite shell...$(NC)"
	@sqlite3 data/scraped_data.db

.PHONY: db-backup
db-backup:
	@echo "$(GREEN)Creating database backup...$(NC)"
	@cp data/scraped_data.db "data/backup_$(shell date +%Y%m%d_%H%M%S).db"
	@echo "$(GREEN)✓ Backup created$(NC)"

.PHONY: report
report:
	@echo "$(GREEN)Generating data quality report...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/$(PYTHON) -c "
import sqlite3
import pandas as pd
conn = sqlite3.connect('data/scraped_data.db')
df = pd.read_sql_query('SELECT * FROM scraped_records', conn)
print('📊 DATA QUALITY REPORT')
print('=' * 40)
print(f'Total records: {len(df)}')
print(f'Columns: {len(df.columns)}')
print(f'Date range: {df[\"date\"].min()} to {df[\"date\"].max()}')
print()
print('Missing values per column:')
for col in df.columns:
    missing = df[col].isna().sum()
    if missing > 0:
        print(f'  {col}: {missing} ({missing/len(df)*100:.1f}%)')
print()
print('Column data types:')
for col in df.columns:
    print(f'  {col}: {df[col].dtype}')
conn.close()
"

# ====================
# DEPLOYMENT & QUALITY
# ====================

.PHONY: requirements
requirements: venv
	@echo "$(GREEN)Freezing requirements...$(NC)"
	@$(VENV)/bin/pip freeze > requirements.txt
	@echo "$(GREEN)✓ Requirements frozen$(NC)"

.PHONY: security
security:
	@echo "$(GREEN)Running security checks...$(NC)"
	@$(VENV)/bin/bandit -r src/ -f json -o bandit-report.json
	@$(VENV)/bin/safety check
	@echo "$(GREEN)✓ Security checks completed$(NC)"

.PHONY: benchmark
benchmark:
	@echo "$(GREEN)Running performance benchmarks...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/$(PYTEST) tests/ --benchmark-only --benchmark-json benchmark.json
	@echo "$(GREEN)✓ Benchmarks completed. See benchmark.json$(NC)"

.PHONY: ci
ci: install lint test security
	@echo "$(GREEN)✓ CI pipeline passed$(NC)"

.PHONY: setup
setup: venv install
	@echo "$(GREEN)✓ Project setup complete$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  make run      - Run the scraper"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Check code quality"
	@echo ""

# ====================
# UTILITIES
# ====================

.PHONY: check-env
check-env:
	@echo "$(GREEN)Checking environment...$(NC)"
	@which $(PYTHON) || (echo "$(RED)✗ Python not found$(NC)" && exit 1)
	@which $(PIP) || (echo "$(RED)✗ pip not found$(NC)" && exit 1)
	@$(PYTHON) --version
	@echo "$(GREEN)✓ Environment OK$(NC)"

.PHONY: version
version:
	@echo "$(GREEN)Project Version: 1.0.0$(NC)"
	@echo "$(GREEN)Python: $(shell $(PYTHON) --version)$(NC)"
	@echo "$(GREEN)Pandas: $(shell $(VENV)/bin/$(PYTHON) -c 'import pandas; print(pandas.__version__)' 2>/dev/null || echo 'Not installed')$(NC)"

# ====================
# SHORTCUTS
# ====================

.PHONY: all
all: clean install lint test run

.PHONY: dev
dev: install
	@echo "$(GREEN)Starting development environment...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/$(PYTHON) -m ipython

.PHONY: notebook
notebook:
	@echo "$(GREEN)Starting Jupyter notebook...$(NC)"
	@PYTHONPATH=$(PYTHONPATH) $(VENV)/bin/jupyter notebook