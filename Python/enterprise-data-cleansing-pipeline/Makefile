.PHONY: help install test lint clean docker-build docker-run deploy

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests with coverage"
	@echo "  lint        Run code formatting and linting"
	@echo "  clean       Remove cache and build files"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run  Run Docker container"
	@echo "  deploy      Deploy to production"

install:
	pip install -e .[dev]

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	black src/ tests/
	flake8 src/ tests/
	mypy src/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/

docker-build:
	docker build -t data-cleaning-pipeline:latest .

docker-run:
	docker run --rm -v $(PWD)/data:/app/data data-cleaning-pipeline:latest

deploy:
	@echo "Deploying to production..."
	git push origin main
	# Add your deployment commands here

setup-hooks:
	cp scripts/pre-commit .git/hooks/
	chmod +x .git/hooks/pre-commit

run-pipeline:
	python main.py --input data/input/ --output data/output/

profile:
	python -m cProfile -o profile.stats main.py

benchmark:
	hyperfine --warmup 3 'python main.py --input data/input/sample.csv'