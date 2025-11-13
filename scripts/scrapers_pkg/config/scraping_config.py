"""Scraping configuration and settings."""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ScrapingConfig:
    """Configuration for web scraping."""
    
    # Rate limiting
    default_delay_seconds: float = 2.0
    max_delay_seconds: float = 5.0
    
    # Request settings
    timeout_seconds: int = 30
    max_retries: int = 3
    
    # User agents for rotation
    user_agents: List[str] = None
    
    # Headers
    default_headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
            ]
        
        if self.default_headers is None:
            self.default_headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

# Brand-specific configurations
BRAND_CONFIGS = {
    "banana_republic": {
        "name": "Banana Republic",
        "base_url": "https://bananarepublic.gap.com",
        "mens_casual_shirts_url": "https://bananarepublic.gap.com/browse/men/casual-shirts?cid=44873",
        "selectors": {
            "product_container": "div[data-testid='product-tile']",
            "product_name": "h3[data-testid='product-title']",
            "product_link": "a[data-testid='product-link']",
            "product_price": "span[data-testid='price-current']",
            "product_original_price": "span[data-testid='price-original']",
            "product_image": "img[data-testid='product-image']",
            "pagination_next": "a[aria-label='Next page']"
        },
        "pagination": {
            "type": "url_param",
            "param": "page",
            "max_pages": 10
        },
        "rate_limit_ms": 2000
    }
}

# Global scraping config
scraping_config = ScrapingConfig()
