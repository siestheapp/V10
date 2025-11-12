"""Base scraper class for all brand-specific scrapers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import time

from models.product import ScrapedProduct, ScrapingRun
from utils.scraping_utils import ScrapingSession, ProductExtractor
from utils.db_utils import db_manager

class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    def __init__(self, brand_name: str, config: Dict[str, Any]):
        self.brand_name = brand_name
        self.config = config
        self.session = ScrapingSession(rate_limit_ms=config.get('rate_limit_ms', 2000))
        self.extractor = ProductExtractor()
        self.db_manager = db_manager
    
    @abstractmethod
    def scrape_products(self, max_pages: int = 5) -> List[ScrapedProduct]:
        """Scrape products from the brand's website."""
        pass
    
    @abstractmethod
    def parse_product_listing(self, html: str, page_url: str) -> List[ScrapedProduct]:
        """Parse product listing page HTML."""
        pass
    
    @abstractmethod
    def parse_product_details(self, product: ScrapedProduct) -> ScrapedProduct:
        """Parse individual product page for detailed information."""
        pass
    
    def run_scraping_session(self, category: str, target_url: str, 
                           max_pages: int = 5) -> Dict[str, Any]:
        """Run a complete scraping session with database tracking."""
        
        # Create scraping run record
        run = ScrapingRun(
            brand_name=self.brand_name,
            category=category,
            target_url=target_url
        )
        
        run_id = self.db_manager.create_scraping_run(run)
        
        try:
            print(f"Starting scraping session for {self.brand_name} - {category}")
            print(f"Target URL: {target_url}")
            print(f"Max pages: {max_pages}")
            
            # Scrape products
            products = self.scrape_products(max_pages)
            
            run.products_found = len(products)
            
            # Save products to database
            products_added = 0
            products_updated = 0
            errors_count = 0
            
            for product in products:
                try:
                    product_id, action = self.db_manager.save_product(product)
                    
                    if action == 'created':
                        products_added += 1
                    elif action == 'updated':
                        products_updated += 1
                    
                    # Log successful product processing
                    self.db_manager.log_product_scraping(
                        run_id=run_id,
                        product_id=product_id,
                        external_id=product.external_id,
                        product_url=product.product_url,
                        action_type=action,
                        scraped_data=product.to_dict()
                    )
                    
                except Exception as e:
                    errors_count += 1
                    print(f"Error saving product {product.name}: {e}")
                    
                    # Log error
                    self.db_manager.log_product_scraping(
                        run_id=run_id,
                        product_id=None,
                        external_id=product.external_id,
                        product_url=product.product_url,
                        action_type='error',
                        error_message=str(e),
                        scraped_data=product.to_dict()
                    )
            
            # Update run statistics
            run.products_added = products_added
            run.products_updated = products_updated
            run.errors_count = errors_count
            run.mark_completed()
            
            # Update database
            self.db_manager.update_scraping_run(run_id, run)
            
            print(f"Scraping completed successfully!")
            print(f"Products found: {run.products_found}")
            print(f"Products added: {run.products_added}")
            print(f"Products updated: {run.products_updated}")
            print(f"Errors: {run.errors_count}")
            print(f"Duration: {run.run_duration_seconds} seconds")
            
            return {
                'status': 'success',
                'run_id': run_id,
                'products_found': run.products_found,
                'products_added': run.products_added,
                'products_updated': run.products_updated,
                'errors_count': run.errors_count,
                'duration_seconds': run.run_duration_seconds
            }
            
        except Exception as e:
            # Mark run as failed
            run.mark_failed({'error': str(e), 'type': type(e).__name__})
            self.db_manager.update_scraping_run(run_id, run)
            
            print(f"Scraping failed: {e}")
            
            return {
                'status': 'failed',
                'run_id': run_id,
                'error': str(e),
                'duration_seconds': run.run_duration_seconds
            }
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Get page content and parse with BeautifulSoup."""
        try:
            response = self.session.get(url)
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Failed to get page content from {url}: {e}")
            return None
    
    def extract_pagination_urls(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract pagination URLs from current page."""
        urls = []
        
        pagination_config = self.config.get('pagination', {})
        pagination_type = pagination_config.get('type', 'url_param')
        
        if pagination_type == 'url_param':
            # Generate URLs by incrementing page parameter
            param = pagination_config.get('param', 'page')
            max_pages = pagination_config.get('max_pages', 5)
            
            base_url = current_url.split('?')[0]
            
            for page in range(2, max_pages + 1):  # Start from page 2
                if '?' in current_url:
                    page_url = f"{current_url}&{param}={page}"
                else:
                    page_url = f"{current_url}?{param}={page}"
                urls.append(page_url)
        
        return urls
    
    def should_continue_pagination(self, soup: BeautifulSoup, page_num: int, 
                                 max_pages: int) -> bool:
        """Determine if pagination should continue."""
        if page_num >= max_pages:
            return False
        
        # Check if there are products on the page
        selectors = self.config.get('selectors', {})
        product_container = selectors.get('product_container', 'div')
        
        products = soup.select(product_container)
        return len(products) > 0
