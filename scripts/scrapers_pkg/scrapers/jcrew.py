"""J.Crew specific scraper implementation with anti-bot handling."""

from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
import re
import time
import json
from decimal import Decimal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from scrapers.base_scraper import BaseScraper
from models.product import ScrapedProduct
from utils.scraping_utils import make_absolute_url, ProductExtractor


class JCrewScraper(BaseScraper):
    """Scraper for J.Crew products with Selenium for anti-bot handling."""
    
    def __init__(self):
        # J.Crew configuration
        config = {
            'base_url': 'https://www.jcrew.com',
            'mens_tops_urls': [
                'https://www.jcrew.com/c/mens/shirts',
                'https://www.jcrew.com/c/mens/t-shirts-polos',
                'https://www.jcrew.com/c/mens/sweaters'
            ],
            'rate_limit_ms': 3000,  # Be respectful with rate limiting
            'use_selenium': True  # J.Crew requires JavaScript rendering
        }
        super().__init__("J.Crew", config)
        self.base_url = config['base_url']
        self.driver = None
    
    def _init_selenium_driver(self):
        """Initialize Selenium driver with anti-detection measures."""
        options = Options()
        
        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Stealth mode
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Performance optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Optional: Run headless for production
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        
        # Execute stealth scripts
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
    
    def _close_selenium_driver(self):
        """Close Selenium driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def scrape_products(self, max_pages: int = 5) -> List[ScrapedProduct]:
        """Scrape men's tops from J.Crew using Selenium."""
        all_products = []
        
        try:
            # Initialize Selenium driver
            self._init_selenium_driver()
            
            # Scrape each category
            for category_url in self.config.get('mens_tops_urls', []):
                print(f"Scraping category: {category_url}")
                category_products = self._scrape_category(category_url, max_pages)
                all_products.extend(category_products)
                
                # Rate limiting between categories
                time.sleep(self.config.get('rate_limit_ms', 3000) / 1000)
            
            print(f"Total products scraped: {len(all_products)}")
            
            # Get detailed information for each product
            detailed_products = []
            for i, product in enumerate(all_products[:20]):  # Limit to 20 for testing
                print(f"Getting details for product {i+1}/{min(len(all_products), 20)}: {product.name}")
                try:
                    detailed_product = self.parse_product_details(product)
                    detailed_products.append(detailed_product)
                    
                    # Rate limiting between products
                    time.sleep(self.config.get('rate_limit_ms', 3000) / 1000)
                except Exception as e:
                    print(f"Error getting details for {product.name}: {e}")
                    detailed_products.append(product)
            
            return detailed_products
            
        finally:
            # Always close the driver
            self._close_selenium_driver()
    
    def _scrape_category(self, category_url: str, max_pages: int) -> List[ScrapedProduct]:
        """Scrape products from a specific category."""
        products = []
        
        try:
            # Navigate to category page
            self.driver.get(category_url)
            
            # Wait for products to load
            wait = WebDriverWait(self.driver, 10)
            
            # Handle cookie consent if present
            try:
                cookie_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
                )
                cookie_button.click()
                time.sleep(1)
            except TimeoutException:
                pass  # No cookie banner
            
            # Scroll to load all products (J.Crew uses lazy loading)
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 5  # Limit scrolling to avoid infinite loops
            
            while scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for new products to load
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract products
            products = self.parse_product_listing(soup.prettify(), category_url)
            
        except Exception as e:
            print(f"Error scraping category {category_url}: {e}")
        
        return products
    
    def parse_product_listing(self, html: str, page_url: str) -> List[ScrapedProduct]:
        """Parse J.Crew product listing page."""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # J.Crew product selectors
        product_selectors = [
            'article[data-testid="product-card"]',
            'div[data-testid="product-tile"]',
            'div[class*="ProductCard"]',
            'div[class*="product-tile"]',
            'a[href*="/p/"]'  # Fallback to product links
        ]
        
        product_containers = []
        for selector in product_selectors:
            containers = soup.select(selector)
            if containers:
                product_containers = containers
                print(f"Found {len(containers)} products using selector: {selector}")
                break
        
        if not product_containers:
            print("No product containers found")
            return products
        
        # Extract products
        for container in product_containers[:50]:  # Limit to prevent too many products
            try:
                product = self._extract_product_from_container(container)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"Error extracting product: {e}")
                continue
        
        return products
    
    def _extract_product_from_container(self, container) -> Optional[ScrapedProduct]:
        """Extract product data from a container element."""
        try:
            # Product URL
            link = container if container.name == 'a' else container.select_one('a[href*="/p/"]')
            if not link or not link.get('href'):
                return None
            
            href = link['href']
            product_url = make_absolute_url(self.base_url, href)
            
            # Extract product ID from URL (last part is usually the product code)
            url_parts = href.strip('/').split('/')
            external_id = url_parts[-1] if url_parts else None
            
            # Product name
            name = ""
            name_selectors = [
                'h3', 'h2', 'h4',
                '[data-testid="product-name"]',
                '[class*="product-name"]',
                '[class*="title"]'
            ]
            
            for selector in name_selectors:
                name_elem = container.select_one(selector)
                if name_elem:
                    name = self.extractor.clean_text(name_elem.get_text())
                    break
            
            if not name:
                # Try to extract from link text
                name = self.extractor.clean_text(link.get_text())
            
            if not name:
                return None
            
            # Price
            price = None
            price_selectors = [
                '[data-testid="product-price"]',
                '[class*="price"]',
                'span[class*="price"]'
            ]
            
            for selector in price_selectors:
                price_elem = container.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self.extractor.extract_price(price_text)
                    if price:
                        break
            
            # Image URL
            image_url = ""
            img = container.select_one('img')
            if img:
                image_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if image_url:
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif image_url.startswith('/'):
                        image_url = make_absolute_url(self.base_url, image_url)
            
            # Determine category/subcategory from URL
            category = "Tops"
            subcategory = "Shirts"  # Default
            
            if 't-shirt' in product_url.lower() or 'polo' in product_url.lower():
                subcategory = "T-Shirts & Polos"
            elif 'sweater' in product_url.lower():
                subcategory = "Sweaters"
            elif 'oxford' in product_url.lower():
                subcategory = "Oxford Shirts"
            elif 'casual' in product_url.lower():
                subcategory = "Casual Shirts"
            
            return ScrapedProduct(
                name=name,
                product_url=product_url,
                external_id=external_id,
                brand_name=self.brand_name,
                price=price,
                primary_image_url=image_url,
                category=category,
                subcategory=subcategory,
                scraping_metadata={
                    'source_page': 'listing',
                    'extraction_method': 'selenium'
                }
            )
            
        except Exception as e:
            print(f"Error extracting product from container: {e}")
            return None
    
    def parse_product_details(self, product: ScrapedProduct) -> ScrapedProduct:
        """Get detailed product information including size guide."""
        if not product.product_url or not self.driver:
            return product
        
        try:
            # Navigate to product page
            self.driver.get(product.product_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            
            # Wait for product details to load
            try:
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product-name"], h1'))
                )
            except TimeoutException:
                print(f"Timeout waiting for product details: {product.product_url}")
                return product
            
            # Get page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Enhanced product name (might be more detailed on product page)
            name_elem = soup.select_one('[data-testid="product-name"], h1')
            if name_elem:
                product.name = self.extractor.clean_text(name_elem.get_text())
            
            # Description
            desc_selectors = [
                '[data-testid="product-description"]',
                '[class*="description"]',
                '[class*="product-details"]'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    product.description = self.extractor.clean_text(
                        desc_elem.get_text()
                    )[:500]
                    break
            
            # Material/fabric
            fabric_patterns = [
                r'(\d+%\s+\w+(?:\s+\w+)?)',  # Matches "100% cotton", "60% cotton 40% polyester"
                r'made (?:from|with|of) ([\w\s,]+)',
                r'(cotton|linen|wool|silk|polyester|nylon|cashmere|merino)'
            ]
            
            page_text = soup.get_text().lower()
            for pattern in fabric_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    product.material = match.group(1).strip()
                    break
            
            # Fit type
            fit_keywords = ['slim', 'regular', 'relaxed', 'classic', 'athletic', 'standard']
            for fit in fit_keywords:
                if fit in page_text:
                    product.fit_type = fit.title()
                    break
            
            # Sizes - Look for size selector
            sizes = []
            size_selectors = [
                'button[data-testid*="size"]',
                'input[name="size"]',
                'select[name="size"] option',
                '[class*="size-selector"] button'
            ]
            
            for selector in size_selectors:
                size_elements = soup.select(selector)
                if size_elements:
                    for elem in size_elements:
                        size_text = elem.get_text(strip=True)
                        if size_text and size_text not in ['Select Size', 'Size']:
                            sizes.append(size_text)
                    break
            
            if sizes:
                product.sizes_available = sizes
            
            # Colors
            colors = []
            color_selectors = [
                'button[data-testid*="color"]',
                '[class*="color-selector"] button',
                '[aria-label*="color"]'
            ]
            
            for selector in color_selectors:
                color_elements = soup.select(selector)
                if color_elements:
                    for elem in color_elements:
                        color_text = elem.get('aria-label') or elem.get_text(strip=True)
                        if color_text:
                            colors.append(color_text)
                    break
            
            if colors:
                product.colors_available = colors
            
            # Try to find size guide information
            size_guide_data = self._extract_size_guide(soup)
            if size_guide_data:
                product.scraping_metadata['size_guide'] = size_guide_data
            
            # Better image URL from product page
            img_selectors = [
                'img[data-testid="product-hero-image"]',
                'img[class*="hero"]',
                'img[class*="main-image"]',
                'meta[property="og:image"]'
            ]
            
            for selector in img_selectors:
                img_elem = soup.select_one(selector)
                if img_elem:
                    if img_elem.name == 'meta':
                        new_image_url = img_elem.get('content')
                    else:
                        new_image_url = img_elem.get('src') or img_elem.get('data-src')
                    
                    if new_image_url:
                        if new_image_url.startswith('//'):
                            new_image_url = 'https:' + new_image_url
                        elif new_image_url.startswith('/'):
                            new_image_url = make_absolute_url(self.base_url, new_image_url)
                        
                        product.primary_image_url = new_image_url
                        break
            
            # Update metadata
            product.scraping_metadata.update({
                'detail_page_scraped': True,
                'detail_page_url': product.product_url
            })
            
        except Exception as e:
            print(f"Error getting product details: {e}")
        
        return product
    
    def _extract_size_guide(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract size guide information if available."""
        try:
            # Look for size guide link/button
            size_guide_triggers = [
                'button[data-testid="size-guide"]',
                'a[href*="size-guide"]',
                'button:contains("Size Guide")',
                '[class*="size-guide"]'
            ]
            
            # This would need to click the size guide button and extract the modal content
            # For now, we'll look for any visible size chart on the page
            
            size_chart_selectors = [
                'table[class*="size"]',
                '[data-testid="size-chart"]',
                '[class*="size-chart"]'
            ]
            
            for selector in size_chart_selectors:
                size_chart = soup.select_one(selector)
                if size_chart:
                    # Extract table data
                    headers = []
                    rows = []
                    
                    # Get headers
                    header_row = size_chart.select_one('thead tr, tr:first-child')
                    if header_row:
                        headers = [th.get_text(strip=True) for th in header_row.select('th, td')]
                    
                    # Get data rows
                    data_rows = size_chart.select('tbody tr, tr')[1:]  # Skip header row
                    for row in data_rows:
                        cells = [td.get_text(strip=True) for td in row.select('td')]
                        if cells:
                            rows.append(cells)
                    
                    if headers and rows:
                        return {
                            'headers': headers,
                            'data': rows
                        }
            
            return None
            
        except Exception as e:
            print(f"Error extracting size guide: {e}")
            return None


# Testing function
def test_jcrew_scraper():
    """Test the J.Crew scraper with a few products."""
    scraper = JCrewScraper()
    
    # Test with just one category and limited products
    scraper.config['mens_tops_urls'] = [
        'https://www.jcrew.com/c/mens/shirts'
    ]
    
    products = scraper.scrape_products(max_pages=1)
    
    print(f"\n{'='*60}")
    print(f"Scraped {len(products)} products")
    print(f"{'='*60}\n")
    
    for i, product in enumerate(products[:5], 1):
        print(f"{i}. {product.name}")
        print(f"   URL: {product.product_url}")
        print(f"   Price: ${product.price}" if product.price else "   Price: N/A")
        print(f"   Image: {product.primary_image_url[:50]}..." if product.primary_image_url else "   Image: N/A")
        print(f"   Sizes: {', '.join(product.sizes_available) if product.sizes_available else 'N/A'}")
        print()
    
    return products


if __name__ == "__main__":
    test_jcrew_scraper()


