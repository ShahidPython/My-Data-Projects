from setuptools import setup, find_packages
from pathlib import Path
import re

# Read project metadata
def read_file(filename: str) -> str:
    """Read file contents."""
    return Path(__file__).parent.joinpath(filename).read_text(encoding='utf-8')

def get_version() -> str:
    """Extract version from __init__.py."""
    version_file = read_file('src/__init__.py')
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

def get_long_description() -> str:
    """Get long description from README."""
    try:
        return read_file('README.md')
    except FileNotFoundError:
        return "Web Scraper to SQLite - Production ETL Pipeline"

# Read requirements
def get_requirements() -> list:
    """Read requirements from requirements.txt."""
    requirements_file = Path(__file__).parent / 'requirements.txt'
    if requirements_file.exists():
        return [
            line.strip()
            for line in read_file('requirements.txt').splitlines()
            if line.strip() and not line.startswith('#')
        ]
    return []

# Package metadata
setup(
    # Basic Information
    name="web-scraper-to-sqlite",
    version=get_version(),
    author="Your Name",
    author_email="your.email@domain.com",
    description="Production-ready ETL pipeline for web scraping to SQLite database",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    
    # URLs
    url="https://github.com/yourusername/web-scraper-to-sqlite",
    project_urls={
        "Documentation": "https://github.com/yourusername/web-scraper-to-sqlite#readme",
        "Source Code": "https://github.com/yourusername/web-scraper-to-sqlite",
        "Bug Tracker": "https://github.com/yourusername/web-scraper-to-sqlite/issues",
        "Changelog": "https://github.com/yourusername/web-scraper-to-sqlite/releases",
    },
    
    # License
    license="MIT",
    
    # Classifiers (PyPI categories)
    classifiers=[
        # Development Status
        "Development Status :: 5 - Production/Stable",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        
        # Topic
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Python Versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # Operating Systems
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        
        # Frameworks
        "Framework :: Pytest",
        "Framework :: Jupyter",
        
        # Additional Metadata
        "Natural Language :: English",
        "Environment :: Console",
        "Typing :: Typed",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "web-scraping",
        "etl",
        "data-pipeline",
        "sqlite",
        "data-analysis",
        "data-engineering",
        "data-science",
        "beautifulsoup",
        "pandas",
        "async",
    ],
    
    # Package Structure
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    
    # Python Requirements
    python_requires=">=3.9",
    
    # Dependencies
    install_requires=get_requirements(),
    
    # Optional Dependencies (Extras)
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-xdist>=3.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "pre-commit>=3.0.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "performance": [
            "uvloop>=0.17.0; sys_platform != 'win32'",
            "orjson>=3.9.0",
            "psutil>=5.9.0",
        ],
        "security": [
            "bandit>=1.7.0",
            "safety>=2.3.0",
        ],
        "cloud": [
            "boto3>=1.28.0",
            "google-cloud-bigquery>=3.0.0",
            "azure-storage-blob>=12.0.0",
        ],
        "ml": [
            "scikit-learn>=1.3.0",
            "tensorflow>=2.13.0",
            "torch>=2.0.0",
        ],
        "viz": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "plotly>=5.15.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "sphinx>=7.0.0",
            "uvloop>=0.17.0; sys_platform != 'win32'",
            "boto3>=1.28.0",
            "scikit-learn>=1.3.0",
            "matplotlib>=3.7.0",
        ],
    },
    
    # Entry Points (CLI commands)
    entry_points={
        "console_scripts": [
            "web-scraper=src.cli:main",
            "ws-scrape=src.cli:main",
            "ws-dashboard=scripts.dashboard:main",
        ],
    },
    
    # Package Data (non-Python files)
    package_data={
        "web_scraper_sqlite": [
            "data/input/*.html",
            "data/input/*.csv",
            "config/*.yaml",
            "config/*.yml",
        ],
    },
    
    # Data Files (outside package)
    data_files=[
        ("share/web-scraper-sqlite/examples", [
            "data/input/example.html",
            "data/input/example_data.csv",
        ]),
        ("share/web-scraper-sqlite/config", [
            "config.yaml",
            "config.production.yaml.example",
        ]),
        ("share/web-scraper-sqlite/docs", [
            "README.md",
            "CONTRIBUTING.md",
            "CHANGELOG.md",
        ]),
    ],
    
    # Scripts (legacy, use entry_points instead)
    scripts=[
        "scripts/web-scraper-cli.py",
        "scripts/data-quality-report.py",
    ],
    
    # Options
    options={
        "bdist_wheel": {
            "universal": False,  # Pure Python but version specific
        },
        "egg_info": {
            "tag_build": "",
            "tag_date": 0,
        },
    },
    
    # Command Line Options
    cmdclass={},
    
    # Test Suite
    test_suite="tests",
    tests_require=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-asyncio>=0.21.0",
    ],
    
    # Performance Optimization
    setup_requires=[
        "setuptools>=65.0.0",
        "wheel>=0.38.0",
    ],
    
    # Build Backend
    backend="setuptools.build_meta",
    
    # Platform Support
    platforms=["any"],
    
    # Additional Metadata
    provides=["web_scraper_sqlite"],
    obsoletes=["old-web-scraper"],
    
    # Long-term Support
    maintainer="Your Name",
    maintainer_email="your.email@domain.com",
    
    # Download URL (legacy)
    download_url="https://github.com/yourusername/web-scraper-to-sqlite/archive/refs/tags/v1.0.0.tar.gz",
)

# Build instructions:
# python setup.py sdist bdist_wheel
# twine upload dist/*

# Install locally:
# pip install -e .

# Install with extras:
# pip install -e .[dev,performance,viz]