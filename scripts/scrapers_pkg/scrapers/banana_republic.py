"""Banana Republic specific scraper implementation."""

from typing import List, Optional
from bs4 import BeautifulSoup
import re
from decimal import Decimal

from scrapers.base_scraper import BaseScraper
from models.product import ScrapedProduct
from utils.scraping_utils import make_absolute_url, ProductExtractor
from config.scraping_config import BRAND_CONFIGS

class BananaRepublicScraper(BaseScraper):
    """Scraper for Banana Republic products."""
    
    def __init__(self):
        config = BRAND_CONFIGS['banana_republic']
        super().__init__("Banana Republic", config)
        self.base_url = config['base_url']
    
    def scrape_products(self, max_pages: int = 5) -> List[ScrapedProduct]:
        """Scrape men's casual shirts from Banana Republic."""
        all_products = []
        
        # Start with the main category page
        start_url = self.config['mens_casual_shirts_url']
        
        for page_num in range(1, max_pages + 1):
            print(f"Scraping page {page_num}...")
            
            # Construct page URL
            if page_num == 1:
                page_url = start_url
            else:
                page_url = f"{start_url}&page={page_num}"
            
            # Get page content
            soup = self.get_page_content(page_url)
            if not soup:
                print(f"Failed to get content for page {page_num}")
                continue
            
            # Parse products from this page
            page_products = self.parse_product_listing(soup.prettify(), page_url)
            
            if not page_products:
                print(f"No products found on page {page_num}, stopping pagination")
                break
            
            print(f"Found {len(page_products)} products on page {page_num}")
            all_products.extend(page_products)
            
            # Check if we should continue
            if not self.should_continue_pagination(soup, page_num, max_pages):
                break
        
        print(f"Total products scraped: {len(all_products)}")
        
        # Get detailed information for each product
        detailed_products = []
        for i, product in enumerate(all_products):
            print(f"Getting details for product {i+1}/{len(all_products)}: {product.name}")
            try:
                detailed_product = self.parse_product_details(product)
                detailed_products.append(detailed_product)
            except Exception as e:
                print(f"Error getting details for {product.name}: {e}")
                # Add the basic product anyway
                detailed_products.append(product)
        
        return detailed_products
    
    def parse_product_listing(self, html: str, page_url: str) -> List[ScrapedProduct]:
        """Parse Banana Republic product listing page."""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Banana Republic uses various selectors, try multiple approaches
        product_selectors = [
            'div[data-testid="product-tile"]',
            'div[class*="ProductTile"]',
            'article[class*="product"]',
            'div[class*="product-card"]',
            '.product-tile',
            '.ProductCard'
        ]
        
        product_containers = []
        for selector in product_selectors:
            containers = soup.select(selector)
            if containers:
                product_containers = containers
                print(f"Found {len(containers)} products using selector: {selector}")
                break
        
        if not product_containers:
            print("No product containers found, trying fallback approach")
            # Fallback: look for links that might be product links
            product_links = soup.select('a[href*="/p/"]')
            if product_links:
                print(f"Found {len(product_links)} product links as fallback")
                for link in product_links[:20]:  # Limit to prevent duplicates
                    try:
                        product = self._extract_product_from_link(link)
                        if product:
                            products.append(product)
                    except Exception as e:
                        print(f"Error extracting product from link: {e}")
        else:
            # Extract products from containers
            for container in product_containers:
                try:
                    product = self._extract_product_from_container(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"Error extracting product from container: {e}")
                    continue
        
        return products
    
    def _extract_product_from_container(self, container) -> Optional[ScrapedProduct]:
        """Extract product data from a product container element."""
        try:
            # Product name - try multiple selectors
            name_selectors = [
                'h3[data-testid="product-title"]',
                '[data-testid="product-title"]',
                'h3',
                'h2',
                '.product-title',
                '[class*="title"]'
            ]
            
            name = ""
            for selector in name_selectors:
                name_elem = container.select_one(selector)
                if name_elem:
                    name = self.extractor.clean_text(name_elem.get_text())
                    break
            
            if not name:
                return None
            
            # Product URL - try multiple selectors
            url_selectors = [
                'a[data-testid="product-link"]',
                'a[href*="/p/"]',
                'a'
            ]
            
            product_url = ""
            for selector in url_selectors:
                link_elem = container.select_one(selector)
                if link_elem and link_elem.get('href'):
                    href = link_elem['href']
                    product_url = make_absolute_url(self.base_url, href)
                    break
            
            if not product_url:
                return None
            
            # Extract product ID from URL
            external_id = self.extractor.extract_product_id(product_url)
            
            # Price information
            price = None
            original_price = None
            
            # Try multiple price selectors
            price_selectors = [
                'span[data-testid="price-current"]',
                '[data-testid="price-current"]',
                '.price-current',
                '.price',
                '[class*="price"]'
            ]
            
            for selector in price_selectors:
                price_elem = container.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self.extractor.extract_price(price_text)
                    break
            
            # Original price (if on sale)
            original_price_selectors = [
                'span[data-testid="price-original"]',
                '[data-testid="price-original"]',
                '.price-original',
                '.price-was',
                '[class*="original"]'
            ]
            
            for selector in original_price_selectors:
                orig_price_elem = container.select_one(selector)
                if orig_price_elem:
                    orig_price_text = orig_price_elem.get_text(strip=True)
                    original_price = self.extractor.extract_price(orig_price_text)
                    break
            
            # Image URL
            image_url = ""
            img_selectors = [
                'img[data-testid="product-image"]',
                'img[src*="bananarepublic"]',
                'img'
            ]
            
            for selector in img_selectors:
                img_elem = container.select_one(selector)
                if img_elem and img_elem.get('src'):
                    src = img_elem['src']
                    if src.startswith('//'):
                        image_url = 'https:' + src
                    elif src.startswith('/'):
                        image_url = make_absolute_url(self.base_url, src)
                    else:
                        image_url = src
                    break
            
            # Extract sizes and colors if available
            sizes = self.extractor.extract_sizes(container)
            colors = self.extractor.extract_colors(container)
            
            return ScrapedProduct(
                name=name,
                product_url=product_url,
                external_id=external_id,
                brand_name=self.brand_name,
                price=price,
                original_price=original_price,
                primary_image_url=image_url,
                sizes_available=sizes,
                colors_available=colors,
                category="Shirts",
                subcategory="Casual Shirts",
                scraping_metadata={
                    'source_page': 'listing',
                    'container_html': str(container)[:500]  # First 500 chars for debugging
                }
            )
            
        except Exception as e:
            print(f"Error extracting product from container: {e}")
            return None
    
    def _extract_product_from_link(self, link) -> Optional[ScrapedProduct]:
        """Extract basic product data from a product link (fallback method)."""
        try:
            href = link.get('href')
            if not href:
                return None
            
            product_url = make_absolute_url(self.base_url, href)
            external_id = self.extractor.extract_product_id(product_url)
            
            # Try to get name from link text or nearby elements
            name = link.get_text(strip=True)
            if not name:
                # Look for name in parent or sibling elements
                parent = link.parent
                if parent:
                    name = parent.get_text(strip=True)
            
            if not name or len(name) < 3:
                return None
            
            name = self.extractor.clean_text(name)
            
            return ScrapedProduct(
                name=name,
                product_url=product_url,
                external_id=external_id,
                brand_name=self.brand_name,
                category="Shirts",
                subcategory="Casual Shirts",
                scraping_metadata={
                    'source_page': 'listing',
                    'extraction_method': 'link_fallback'
                }
            )
            
        except Exception as e:
            print(f"Error extracting product from link: {e}")
            return None
    
    def parse_product_details(self, product: ScrapedProduct) -> ScrapedProduct:
        """Get detailed product information from individual product page."""
        if not product.product_url:
            return product
        
        try:
            soup = self.get_page_content(product.product_url)
            if not soup:
                return product
            
            # Enhanced description
            desc_selectors = [
                '[data-testid="product-description"]',
                '.product-description',
                '.product-details',
                '[class*="description"]'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    product.description = self.extractor.clean_text(
                        desc_elem.get_text()
                    )[:500]  # Limit length
                    break
            
            # Material information
            material_keywords = ['cotton', 'polyester', 'wool', 'silk', 'linen', 'fabric']
            material_text = soup.get_text().lower()
            
            for keyword in material_keywords:
                if keyword in material_text:
                    # Find the sentence containing the material
                    sentences = material_text.split('.')
                    for sentence in sentences:
                        if keyword in sentence:
                            product.material = sentence.strip()[:200]
                            break
                    if product.material:
                        break
            
            # Fit type
            fit_keywords = ['slim', 'regular', 'relaxed', 'tailored', 'classic']
            page_text = soup.get_text().lower()
            
            for fit in fit_keywords:
                if fit in page_text:
                    product.fit_type = fit.title()
                    break
            
            # Enhanced size and color extraction
            if not product.sizes_available:
                product.sizes_available = self.extractor.extract_sizes(soup)
            
            if not product.colors_available:
                product.colors_available = self.extractor.extract_colors(soup)
            
            # Additional images
            img_elements = soup.select('img[src*="bananarepublic"]')
            additional_images = []
            
            for img in img_elements:
                src = img.get('src', '')
                if src and src != product.primary_image_url:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = make_absolute_url(self.base_url, src)
                    additional_images.append(src)
            
            product.additional_images = additional_images[:5]  # Limit to 5 images
            
            # Update metadata
            product.scraping_metadata.update({
                'detail_page_scraped': True,
                'detail_page_url': product.product_url
            })
            
        except Exception as e:
            print(f"Error getting product details: {e}")
        
        return product
