import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pytest
import pandas as pd
import requests

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.scraper import WebScraper


class TestWebScraper:
    """Comprehensive test suite for WebScraper class."""
    
    @pytest.fixture
    def sample_config(self):
        """Provide sample configuration for testing."""
        return {
            'scraping': {
                'target_url': 'https://example.com',
                'user_agent': 'test-agent',
                'timeout': 30,
                'retry_attempts': 3
            },
            'selectors': {
                'container': 'div.data-item',
                'fields': {
                    'title': 'h2::text',
                    'price': 'span.price::text',
                    'description': 'p.desc::text'
                }
            }
        }
    
    @pytest.fixture
    def mock_html_content(self):
        """Provide sample HTML content for testing."""
        return """
        <html>
            <body>
                <div class="data-item">
                    <h2>Product One</h2>
                    <span class="price">$29.99</span>
                    <p class="desc">First product description</p>
                </div>
                <div class="data-item">
                    <h2>Product Two</h2>
                    <span class="price">$39.99</span>
                    <p class="desc">Second product description</p>
                </div>
            </body>
        </html>
        """
    
    @pytest.fixture
    def scraper(self, sample_config):
        """Create WebScraper instance with mocked config."""
        with patch('src.scraper.WebScraper._load_config', return_value=sample_config):
            return WebScraper()
    
    def test_initialization(self, scraper, sample_config):
        """Test scraper initializes with correct configuration."""
        assert scraper.target_url == sample_config['scraping']['target_url']
        assert scraper.session.headers['User-Agent'] == sample_config['scraping']['user_agent']
        assert scraper.logger is not None
    
    def test_initialization_with_custom_url(self, sample_config):
        """Test scraper initializes with custom URL."""
        custom_url = "https://custom-site.com"
        with patch('src.scraper.WebScraper._load_config', return_value=sample_config):
            scraper = WebScraper(target_url=custom_url)
            assert scraper.target_url == custom_url
    
    def test_invalid_url_validation(self, sample_config):
        """Test URL validation rejects invalid URLs."""
        with patch('src.scraper.WebScraper._load_config', return_value=sample_config):
            with pytest.raises(ValueError):
                WebScraper(target_url="invalid-url")
    
    @patch('src.scraper.requests.Session')
    def test_session_creation(self, mock_session, sample_config):
        """Test HTTP session is created with proper headers."""
        with patch('src.scraper.WebScraper._load_config', return_value=sample_config):
            WebScraper()
            mock_session.assert_called_once()
    
    @patch('src.scraper.BeautifulSoup')
    @patch('src.scraper.requests.Session')
    def test_successful_request(self, mock_session, mock_bs, scraper, mock_html_content):
        """Test successful HTTP request handling."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_html_content.encode()
        mock_response.headers = {'content-type': 'text/html'}
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        mock_bs.return_value = Mock()
        
        result = scraper._make_request("https://example.com")
        
        assert result is not None
        mock_session_instance.get.assert_called_once()
    
    @patch('src.scraper.requests.Session')
    def test_failed_request_retry(self, mock_session, scraper):
        """Test request retry logic on failure."""
        mock_session_instance = Mock()
        mock_session_instance.get.side_effect = requests.exceptions.RequestException("Timeout")
        mock_session.return_value = mock_session_instance
        
        result = scraper._make_request("https://example.com")
        
        assert result is None
        assert mock_session_instance.get.call_count == 3  # 3 retry attempts
    
    @patch('src.scraper.requests.Session')
    def test_non_html_content_rejection(self, mock_session, scraper):
        """Test non-HTML content is properly rejected."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.content = b'{"json": "data"}'
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        result = scraper._make_request("https://example.com")
        
        assert result is None
    
    def test_data_extraction_from_element(self, scraper, mock_html_content):
        """Test data extraction from HTML elements."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(mock_html_content, 'lxml')
        element = soup.find('div', class_='data-item')
        
        # Update selectors to match HTML structure
        scraper.config['selectors']['fields'] = {
            'title': 'h2::text',
            'price': 'span.price::text',
            'description': 'p.desc::text'
        }
        
        extracted_data = scraper._extract_element_data(element)
        
        assert extracted_data['title'] == 'Product One'
        assert extracted_data['price'] == '$29.99'
        assert extracted_data['description'] == 'First product description'
    
    def test_data_extraction_with_missing_fields(self, scraper):
        """Test data extraction handles missing fields gracefully."""
        from bs4 import BeautifulSoup
        
        html = "<div class='data-item'><h2>Only Title</h2></div>"
        soup = BeautifulSoup(html, 'lxml')
        element = soup.find('div', class_='data-item')
        
        extracted_data = scraper._extract_element_data(element)
        
        assert extracted_data['title'] == 'Only Title'
        assert extracted_data['price'] is None
        assert extracted_data['description'] is None
    
    @patch('src.scraper.WebScraper._make_request')
    def test_successful_scrape_data(self, mock_make_request, scraper, mock_html_content):
        """Test complete data scraping workflow."""
        from bs4 import BeautifulSoup
        
        mock_soup = BeautifulSoup(mock_html_content, 'lxml')
        mock_make_request.return_value = mock_soup
        
        result = scraper.scrape_data()
        
        assert len(result) == 2
        assert result[0]['title'] == 'Product One'
        assert result[1]['title'] == 'Product Two'
    
    @patch('src.scraper.WebScraper._make_request')
    def test_scrape_data_with_limit(self, mock_make_request, scraper, mock_html_content):
        """Test data scraping respects record limit."""
        from bs4 import BeautifulSoup
        
        mock_soup = BeautifulSoup(mock_html_content, 'lxml')
        mock_make_request.return_value = mock_soup
        
        result = scraper.scrape_data(limit=1)
        
        assert len(result) == 1
    
    @patch('src.scraper.WebScraper._make_request')
    def test_scrape_data_empty_results(self, mock_make_request, scraper):
        """Test scraping handles empty results properly."""
        from bs4 import BeautifulSoup
        
        empty_html = "<html><body></body></html>"
        mock_soup = BeautifulSoup(empty_html, 'lxml')
        mock_make_request.return_value = mock_soup
        
        result = scraper.scrape_data()
        
        assert result == []
    
    @patch('src.scraper.WebScraper._make_request')
    def test_scrape_to_dataframe(self, mock_make_request, scraper, mock_html_content):
        """Test scraping directly to DataFrame."""
        from bs4 import BeautifulSoup
        
        mock_soup = BeautifulSoup(mock_html_content, 'lxml')
        mock_make_request.return_value = mock_soup
        
        df = scraper.scrape_to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert 'title' in df.columns
    
    @patch('src.scraper.WebScraper._make_request')
    def test_selector_validation(self, mock_make_request, scraper, mock_html_content):
        """Test CSS selector validation functionality."""
        from bs4 import BeautifulSoup
        
        mock_soup = BeautifulSoup(mock_html_content, 'lxml')
        mock_make_request.return_value = mock_soup
        
        result = scraper.test_selectors()
        
        assert 'container_count' in result
        assert 'field_samples' in result
        assert 'page_title' in result
        assert result['container_count'] == 2
    
    def test_config_file_not_found(self):
        """Test proper error handling when config file is missing."""
        with patch('src.scraper.open', side_effect=FileNotFoundError()):
            with pytest.raises(Exception, match="Configuration file 'config.yaml' not found"):
                WebScraper()
    
    @patch('src.scraper.time.sleep')  # Mock sleep to speed up tests
    @patch('src.scraper.requests.Session')
    def test_respectful_scraping_delay(self, mock_session, mock_sleep, scraper, mock_html_content):
        """Test respectful scraping with delays between requests."""
        from bs4 import BeautifulSoup
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_html_content.encode()
        mock_response.headers = {'content-type': 'text/html'}
        
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        mock_soup = BeautifulSoup(mock_html_content, 'lxml')
        with patch('src.scraper.BeautifulSoup', return_value=mock_soup):
            scraper.scrape_data()
            
            # Verify sleep was called between element processing
            mock_sleep.assert_called()