import asyncio
import aiohttp
import json
import re
import time
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import pickle
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    """Container for scrape results with statistics."""
    data: List[Dict[str, Any]]
    stats: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert scraped data to pandas DataFrame."""
        return pd.DataFrame(self.data)
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps({
            'data': self.data,
            'stats': self.stats,
            'metadata': self.metadata
        }, default=str)
    
    @property
    def success(self) -> bool:
        """Check if scrape was successful."""
        return self.stats.get('success', False)


class CacheHandler:
    """Handle caching of scraped content."""
    
    def __init__(self, cache_dir: str = 'data/cache', ttl_hours: int = 24):
        """Initialize cache handler."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"{url_hash}.pkl"
    
    def _get_cache_path(self, url: str) -> Path:
        """Get full cache path."""
        return self.cache_dir / self._get_cache_key(url)
    
    def is_cached(self, url: str) -> bool:
        """Check if URL is cached and valid."""
        cache_path = self._get_cache_path(url)
        
        if not cache_path.exists():
            return False
        
        # Check TTL
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - mtime > self.ttl:
            cache_path.unlink()  # Remove expired cache
            return False
        
        return True
    
    def get_cached(self, url: str) -> Optional[Any]:
        """Get cached content."""
        if not self.is_cached(url):
            return None
        
        cache_path = self._get_cache_path(url)
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning(f"Cache read error for {url}: {str(e)}")
            cache_path.unlink()
            return None
    
    def set_cache(self, url: str, data: Any) -> None:
        """Cache content."""
        cache_path = self._get_cache_path(url)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.warning(f"Cache write error for {url}: {str(e)}")


class WebScraper:
    """Production web scraper with async support."""
    
    DEFAULT_SELECTORS = {
        'container': '.product-card',
        'title': '.product-title',
        'price': '.product-price',
        'category': '.product-category',
        'rating': '.product-rating',
        'stock': '.product-stock',
        'description': '.product-description',
        'sku': '.product-meta span:first-child',
        'date_added': '.product-meta span:last-child'
    }
    
    def __init__(
        self,
        target_url: Optional[str] = None,
        selectors: Optional[Dict[str, str]] = None,
        cache_enabled: bool = True,
        max_concurrent: int = 5,
        timeout: int = 30,
        user_agent: str = None
    ):
        """Initialize scraper with configuration."""
        self.target_url = target_url
        self.selectors = selectors or self.DEFAULT_SELECTORS
        self.cache_enabled = cache_enabled
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        self.cache = CacheHandler() if cache_enabled else None
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Statistics
        self.scrape_stats = {
            'start_time': None,
            'end_time': None,
            'records_extracted': 0,
            'success_rate': 0.0,
            'errors_count': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'extraction_rate': 0.0,
            'status': 'initialized'
        }
    
    def _is_local_file(self, url: str) -> bool:
        """Check if URL points to a local file."""
        parsed = urlparse(url)
        return parsed.scheme in ['file', ''] or url.startswith('./')
    
    def _read_local_file(self, file_path: str) -> Optional[str]:
        """Read content from local file."""
        try:
            # Remove file:// prefix if present
            if file_path.startswith('file://'):
                file_path = file_path[7:]
            
            # Handle relative paths
            if not Path(file_path).is_absolute():
                file_path = str(Path.cwd() / file_path)
            
            logger.info(f"Loading local file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except FileNotFoundError:
            logger.error(f"Local file not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading local file {file_path}: {str(e)}")
            return None
    
    async def _fetch_url(self, url: str) -> Optional[str]:
        """Fetch content from URL (async)."""
        if self._is_local_file(url):
            # Use thread pool for file I/O
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                content = await loop.run_in_executor(
                    pool, self._read_local_file, url
                )
            return content
        
        # Check cache first
        if self.cache_enabled and self.cache:
            cached = self.cache.get_cached(url)
            if cached is not None:
                self.scrape_stats['cache_hits'] += 1
                logger.debug(f"Cache hit for: {url}")
                return cached
        
        # Fetch from web
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {'User-Agent': self.user_agent}
                    
                    async with session.get(
                        url, 
                        headers=headers, 
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as response:
                        response.raise_for_status()
                        content = await response.text()
                        
                        # Cache the result
                        if self.cache_enabled and self.cache:
                            self.cache.set_cache(url, content)
                            self.scrape_stats['cache_misses'] += 1
                        
                        return content
                        
            except asyncio.TimeoutError:
                logger.error(f"Timeout fetching {url}")
            except aiohttp.ClientError as e:
                logger.error(f"HTTP error fetching {url}: {str(e)}")
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
            
            return None
    
    def _parse_html(self, html_content: str, base_url: str = None) -> BeautifulSoup:
        """Parse HTML content."""
        if not html_content:
            return None
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup
        except Exception as e:
            logger.error(f"Error parsing HTML from {base_url or 'unknown'}: {str(e)}")
            return None
    
    def _extract_product_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract product data from parsed HTML."""
        if not soup:
            return []
        
        products = []
        container_selector = self.selectors.get('container', '.product-card')
        containers = soup.select(container_selector)
        
        logger.info(f"Found {len(containers)} container elements")
        
        for i, container in enumerate(containers):
            try:
                product_data = {}
                
                # Extract each field
                for field, selector in self.selectors.items():
                    if field == 'container':
                        continue  # Skip container selector
                    
                    element = container.select_one(selector)
                    if element:
                        text = element.get_text(strip=True)
                        
                        # Special processing for different fields
                        if field == 'price':
                            # Extract numeric value from price
                            text = self._extract_price(text)
                        elif field == 'rating':
                            # Extract numeric rating
                            text = self._extract_rating(text)
                        elif field == 'stock':
                            # Parse stock information - FIXED: returns string now
                            text = self._parse_stock_status(text)
                        elif field == 'sku':
                            # Clean SKU
                            text = text.replace('🆔 SKU:', '').strip()
                        elif field == 'date_added':
                            # Extract date
                            text = text.replace('📅 Added:', '').strip()
                        
                        product_data[field] = text
                    else:
                        product_data[field] = None
                
                # Add metadata
                product_data['_container_index'] = i
                product_data['_scrape_timestamp'] = datetime.now().isoformat()
                
                # Check if product has special classes
                if 'discounted' in container.get('class', []):
                    product_data['discounted'] = True
                if 'featured' in container.get('class', []):
                    product_data['featured'] = True
                if 'product-card' in container.get('class', []):
                    product_data['card_type'] = 'product-card'
                
                products.append(product_data)
                
            except Exception as e:
                logger.warning(f"Error extracting product {i}: {str(e)}")
                continue
        
        return products
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text."""
        if not price_text:
            return None
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.]', '', price_text)
            if cleaned:
                return float(cleaned)
        except Exception:
            pass
        
        return None
    
    def _extract_rating(self, rating_text: str) -> Optional[float]:
        """Extract numeric rating from text."""
        if not rating_text:
            return None
        
        try:
            # Look for patterns like "4.2" or "⭐⭐⭐⭐ (4.2)"
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match:
                return float(match.group(1))
        except Exception:
            pass
        
        return None
    
    def _parse_stock_status(self, stock_text: str) -> str:  # FIXED: returns string
        """Parse stock status text."""
        if not stock_text:
            return "unknown"
        
        stock_text_lower = stock_text.lower()
        
        if 'in stock' in stock_text_lower:
            return "in_stock"
        elif 'low stock' in stock_text_lower:
            return "low_stock"
        elif 'out of stock' in stock_text_lower:
            return "out_of_stock"
        else:
            return "unknown"
    
    def _calculate_stats(self, products: List[Dict], start_time: float) -> Dict[str, Any]:
        """Calculate scraping statistics."""
        end_time = time.time()
        duration = end_time - start_time
        
        successful = len(products)
        total_attempts = successful + self.scrape_stats['errors_count']
        success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0
        
        extraction_rate = successful / duration if duration > 0 else 0
        
        return {
            'success': successful > 0,
            'records_extracted': successful,
            'duration_seconds': round(duration, 2),
            'success_rate': round(success_rate, 1),
            'errors_count': self.scrape_stats['errors_count'],
            'cache_hits': self.scrape_stats.get('cache_hits', 0),
            'cache_misses': self.scrape_stats.get('cache_misses', 0),
            'cache_ratio': round(
                self.scrape_stats.get('cache_hits', 0) / 
                max(self.scrape_stats.get('cache_hits', 0) + self.scrape_stats.get('cache_misses', 0), 1) * 100, 
                1
            ),
            'extraction_rate': round(extraction_rate, 1),
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'end_time': datetime.fromtimestamp(end_time).isoformat()
        }
    
    async def scrape_data(self, limit: Optional[int] = None, use_async: bool = True) -> ScrapeResult:
        """Main method to scrape data."""
        if not self.target_url:
            logger.error("No target URL provided")
            return ScrapeResult([], {'success': False, 'error': 'No URL provided'})
        
        logger.info(f"Starting scrape of {self.target_url} (async: {use_async})")
        
        start_time = time.time()
        self.scrape_stats['start_time'] = start_time
        self.scrape_stats['status'] = 'running'
        
        try:
            # Fetch content
            html_content = await self._fetch_url(self.target_url)
            
            if not html_content:
                self.scrape_stats['errors_count'] += 1
                error_msg = f"Failed to retrieve page content from {self.target_url}"
                logger.error(error_msg)
                return ScrapeResult([], {
                    'success': False, 
                    'error': error_msg,
                    'duration_seconds': round(time.time() - start_time, 2)
                })
            
            # Parse HTML
            soup = self._parse_html(html_content, self.target_url)
            if not soup:
                self.scrape_stats['errors_count'] += 1
                return ScrapeResult([], {
                    'success': False, 
                    'error': 'Failed to parse HTML',
                    'duration_seconds': round(time.time() - start_time, 2)
                })
            
            # Extract data
            products = self._extract_product_data(soup)
            
            # Apply limit if specified
            if limit and limit > 0:
                products = products[:limit]
                logger.info(f"Limited to {limit} records")
            
            # Calculate statistics
            stats = self._calculate_stats(products, start_time)
            
            # Create metadata
            metadata = {
                'source_url': self.target_url,
                'selectors_used': self.selectors,
                'limit_applied': limit if limit else None,
                'async_mode': use_async,
                'user_agent': self.user_agent,
                'cache_enabled': self.cache_enabled
            }
            
            # Update scraper stats
            self.scrape_stats.update(stats)
            self.scrape_stats['status'] = 'completed' if stats['success'] else 'failed'
            
            logger.info(f"Scrape completed: {stats['records_extracted']} records extracted")
            logger.info(f"Success rate: {stats['success_rate']}%, "
                       f"Duration: {stats['duration_seconds']}s, "
                       f"Rate: {stats['extraction_rate']} rec/s")
            
            return ScrapeResult(products, stats, metadata)
            
        except Exception as e:
            self.scrape_stats['errors_count'] += 1
            self.scrape_stats['status'] = 'error'
            logger.error(f"Scrape failed: {str(e)}")
            
            return ScrapeResult([], {
                'success': False,
                'error': str(e),
                'duration_seconds': round(time.time() - start_time, 2)
            })
    
    def test_selectors(self) -> Dict[str, Any]:
        """Test selectors against target URL."""
        if not self.target_url:
            return {'valid': False, 'error': 'No URL provided'}
        
        logger.info(f"Testing selectors on {self.target_url}")
        
        result = {
            'valid': False,
            'selectors': self.selectors,
            'warnings': [],
            'container_count': 0,
            'field_coverage': {}
        }
        
        try:
            # Run a quick scrape
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                scrape_result = loop.run_until_complete(
                    self.scrape_data(limit=1, use_async=False)
                )
                
                if scrape_result.success and scrape_result.data:
                    result['valid'] = True
                    result['container_count'] = scrape_result.stats['records_extracted']
                    
                    # Check field coverage
                    sample_product = scrape_result.data[0] if scrape_result.data else {}
                    for field in self.selectors.keys():
                        if field == 'container':
                            continue
                        result['field_coverage'][field] = sample_product.get(field) is not None
                    
                    # Generate warnings for missing fields
                    missing_fields = [
                        field for field, covered in result['field_coverage'].items()
                        if not covered
                    ]
                    if missing_fields:
                        result['warnings'].append(
                            f"Missing fields: {', '.join(missing_fields)}"
                        )
                
            finally:
                loop.close()
            
        except Exception as e:
            result['error'] = str(e)
            result['warnings'].append(f"Test failed: {str(e)}")
        
        return result
    
    def scrape_sync(self, limit: Optional[int] = None) -> ScrapeResult:
        """Synchronous wrapper for scrape_data."""
        try:
            # Create new event loop for synchronous call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                return loop.run_until_complete(
                    self.scrape_data(limit=limit, use_async=False)
                )
            finally:
                loop.close()
                
        except RuntimeError as e:
            # If there's already an event loop running
            if "running loop" in str(e):
                return asyncio.run(self.scrape_data(limit=limit, use_async=False))
            raise


# Example usage
if __name__ == "__main__":
    # Test the scraper
    async def test_scraper():
        scraper = WebScraper(
            target_url="./data/input/example.html",
            cache_enabled=True,
            max_concurrent=3
        )
        
        # Test selectors
        selector_test = scraper.test_selectors()
        print("Selector test:", json.dumps(selector_test, indent=2))
        
        # Scrape data
        result = await scraper.scrape_data(limit=5)
        
        if result.success:
            print(f"\n✅ Successfully scraped {len(result.data)} products")
            print("\nSample product:")
            print(json.dumps(result.data[0] if result.data else {}, indent=2))
            
            # Convert to DataFrame
            df = result.to_dataframe()
            print(f"\nDataFrame shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Save to CSV
            df.to_csv('data/output/scraped_products.csv', index=False)
            print("\n✅ Data saved to data/output/scraped_products.csv")
        else:
            print(f"\n❌ Scrape failed: {result.stats.get('error', 'Unknown error')}")
    
    # Run the test
    asyncio.run(test_scraper())
