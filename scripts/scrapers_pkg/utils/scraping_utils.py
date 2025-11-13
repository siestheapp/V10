"""Scraping utilities and helper functions."""

import time
import random
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse
import re
from decimal import Decimal

from config.scraping_config import scraping_config

class ScrapingSession:
    """Manages HTTP sessions with rate limiting and error handling."""
    
    def __init__(self, rate_limit_ms: int = 2000):
        self.session = requests.Session()
        self.rate_limit_ms = rate_limit_ms
        self.last_request_time = 0
        
        # Set default headers
        self.session.headers.update(scraping_config.default_headers)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make a GET request with rate limiting."""
        self._apply_rate_limit()
        self._rotate_user_agent()
        
        try:
            response = self.session.get(
                url, 
                timeout=scraping_config.timeout_seconds,
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            raise
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = (current_time - self.last_request_time) * 1000
        
        if time_since_last < self.rate_limit_ms:
            sleep_time = (self.rate_limit_ms - time_since_last) / 1000
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _rotate_user_agent(self):
        """Rotate user agent for each request."""
        user_agent = random.choice(scraping_config.user_agents)
        self.session.headers['User-Agent'] = user_agent

class ProductExtractor:
    """Extracts product data from HTML using CSS selectors."""
    
    @staticmethod
    def extract_text(element, selector: str, default: str = "") -> str:
        """Extract text from element using CSS selector."""
        if not element:
            return default
        
        found = element.select_one(selector)
        return found.get_text(strip=True) if found else default
    
    @staticmethod
    def extract_attribute(element, selector: str, attribute: str, default: str = "") -> str:
        """Extract attribute from element using CSS selector."""
        if not element:
            return default
        
        found = element.select_one(selector)
        return found.get(attribute, default) if found else default
    
    @staticmethod
    def extract_price(price_text: str) -> Optional[Decimal]:
        """Extract price from text string."""
        if not price_text:
            return None
        
        # Remove currency symbols and extract numbers
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return Decimal(price_match.group())
            except:
                return None
        return None
    
    @staticmethod
    def extract_product_id(url: str) -> str:
        """Extract product ID from URL."""
        # Try different patterns for product ID extraction
        patterns = [
            r'/p/[^/]+/(\w+)',  # /p/product-name/ID
            r'/(\w+)/?$',       # ID at end of URL
            r'product[_-]?id[=:](\w+)',  # product_id= or product-id:
            r'/(\d+)/?$'        # Numeric ID at end
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Fallback: use last part of path
        path_parts = urlparse(url).path.strip('/').split('/')
        return path_parts[-1] if path_parts else url
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common unwanted characters
        text = text.replace('\u00a0', ' ')  # Non-breaking space
        text = text.replace('\u2019', "'")  # Smart apostrophe
        text = text.replace('\u201c', '"')  # Smart quote
        text = text.replace('\u201d', '"')  # Smart quote
        
        return text.strip()
    
    @staticmethod
    def normalize_size(size: str) -> str:
        """Normalize size strings."""
        if not size:
            return ""
        
        size = size.upper().strip()
        
        # Common size normalizations
        size_map = {
            'EXTRA SMALL': 'XS',
            'SMALL': 'S',
            'MEDIUM': 'M',
            'LARGE': 'L',
            'EXTRA LARGE': 'XL',
            'XXL': 'XXL',
            'XXXL': 'XXXL'
        }
        
        return size_map.get(size, size)
    
    @staticmethod
    def extract_sizes(container) -> List[str]:
        """Extract available sizes from product container."""
        sizes = []
        
        # Common size selectors
        size_selectors = [
            '[data-testid*="size"]',
            '.size-option',
            '.size-selector',
            '[class*="size"]'
        ]
        
        for selector in size_selectors:
            size_elements = container.select(selector)
            for elem in size_elements:
                size_text = elem.get_text(strip=True)
                if size_text and len(size_text) <= 10:  # Reasonable size length
                    normalized = ProductExtractor.normalize_size(size_text)
                    if normalized and normalized not in sizes:
                        sizes.append(normalized)
        
        return sizes
    
    @staticmethod
    def extract_colors(container) -> List[str]:
        """Extract available colors from product container."""
        colors = []
        
        # Common color selectors
        color_selectors = [
            '[data-testid*="color"]',
            '.color-option',
            '.color-selector',
            '[class*="color"]',
            '[alt*="color"]'
        ]
        
        for selector in color_selectors:
            color_elements = container.select(selector)
            for elem in color_elements:
                # Try to get color from text or alt attribute
                color_text = elem.get_text(strip=True) or elem.get('alt', '')
                if color_text and len(color_text) <= 50:  # Reasonable color name length
                    color_text = ProductExtractor.clean_text(color_text)
                    if color_text and color_text not in colors:
                        colors.append(color_text)
        
        return colors

def make_absolute_url(base_url: str, relative_url: str) -> str:
    """Convert relative URL to absolute URL."""
    return urljoin(base_url, relative_url)

def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
