#!/usr/bin/env python3
"""
Ingest all missing J.Crew Men's Casual Shirts into the database
Fetches complete product data including all fits and colors
"""

import sys
import json
import time
import psycopg2
from datetime import datetime
import logging
from typing import Dict, List, Optional

# Add project root to path
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG
from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class JCrewProductIngestor:
    """Ingest J.Crew products into database with all variations"""
    
    def __init__(self):
        self.fetcher = JCrewProductFetcher()
        self.brand_id = 4  # J.Crew brand ID
        self.conn = None
        self.cur = None
        self.stats = {
            'total_products': 0,
            'successful': 0,
            'failed': 0,
            'already_exists': 0,
            'colors_added': 0,
            'fits_added': 0
        }
    
    def connect_db(self):
        """Connect to database"""
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()
        logger.info("Connected to database")
    
    def close_db(self):
        """Close database connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
    
    def product_exists(self, product_code: str) -> bool:
        """Check if product already exists in cache"""
        self.cur.execute("""
            SELECT COUNT(*) FROM jcrew_product_cache 
            WHERE product_code = %s
        """, (product_code,))
        return self.cur.fetchone()[0] > 0
    
    def fetch_product_details(self, product_code: str) -> Optional[Dict]:
        """Fetch complete product details from J.Crew"""
        # Try different URL patterns for the product
        url_patterns = [
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/corduroy/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/linen/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/chambray-and-denim-shirts/{product_code}",
            f"https://www.jcrew.com/p/mens/categories/clothing/shirts/{product_code}",
            f"https://www.jcrew.com/p/{product_code}"
        ]
        
        for url in url_patterns:
            logger.info(f"  Trying URL: {url}")
            try:
                product_data = self.fetcher.fetch_product(url)
                if product_data and product_data.get('product_name'):
                    logger.info(f"  ✅ Found product: {product_data['product_name']}")
                    return product_data
            except Exception as e:
                logger.debug(f"  Failed with {url}: {e}")
                continue
        
        logger.warning(f"  ❌ Could not fetch product {product_code}")
        return None
    
    def store_product(self, product_data: Dict) -> bool:
        """Store product in jcrew_product_cache table"""
        try:
            # Prepare data for insertion
            product_code = product_data.get('product_code', '')
            
            # Skip if already exists
            if self.product_exists(product_code):
                logger.info(f"  Product {product_code} already exists in cache")
                self.stats['already_exists'] += 1
                return True
            
            # Build metadata JSON
            metadata = {
                'original_url': product_data.get('product_url', ''),
                'scraped_at': datetime.now().isoformat(),
                'raw_data': product_data
            }
            
            # Insert into jcrew_product_cache
            self.cur.execute("""
                INSERT INTO jcrew_product_cache (
                    product_url, product_code, product_name, product_image,
                    category, subcategory, price, sizes_available, colors_available,
                    material, fit_type, description, metadata, created_at, updated_at,
                    fit_options, product_description, fit_details, cache_key,
                    brand_name, standard_category, standard_subcategory,
                    garment_type, fabric_primary, comparison_key
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                product_data.get('product_url', ''),
                product_code,
                product_data.get('product_name', ''),
                product_data.get('product_image', ''),
                product_data.get('category', 'Men'),
                product_data.get('subcategory', 'Shirts'),
                product_data.get('price'),
                product_data.get('sizes_available', []),
                product_data.get('colors_available', []),
                product_data.get('material', ''),
                product_data.get('fit_type', ''),
                product_data.get('description', ''),
                json.dumps(metadata),
                datetime.now(),
                datetime.now(),
                product_data.get('fit_options', []),
                product_data.get('product_description', ''),
                json.dumps(product_data.get('fit_details', {})),
                product_data.get('cache_key', product_code),
                'J.Crew',
                product_data.get('standard_category', 'tops'),
                product_data.get('standard_subcategory', 'shirts'),
                product_data.get('garment_type', 'shirt'),
                product_data.get('fabric_primary', ''),
                product_data.get('comparison_key', product_code)
            ))
            
            self.conn.commit()
            
            # Track stats
            colors = product_data.get('colors_available', [])
            fits = product_data.get('fit_options', [])
            self.stats['colors_added'] += len(colors)
            self.stats['fits_added'] += len(fits)
            
            logger.info(f"  ✅ Stored {product_code}: {product_data.get('product_name', '')} "
                       f"({len(colors)} colors, {len(fits)} fits)")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Failed to store product: {e}")
            self.conn.rollback()
            return False
    
    def ingest_products(self, product_codes: List[str]):
        """Main ingestion process for a list of product codes"""
        logger.info(f"Starting ingestion of {len(product_codes)} products")
        logger.info("="*60)
        
        self.connect_db()
        
        for i, product_code in enumerate(product_codes, 1):
            logger.info(f"\n[{i}/{len(product_codes)}] Processing {product_code}")
            self.stats['total_products'] += 1
            
            # Fetch product details
            product_data = self.fetch_product_details(product_code)
            
            if product_data:
                # Store in database
                if self.store_product(product_data):
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1
            else:
                self.stats['failed'] += 1
            
            # Rate limiting
            time.sleep(2)  # Be respectful to J.Crew servers
        
        self.close_db()
        self.print_summary()
    
    def print_summary(self):
        """Print ingestion summary"""
        logger.info("\n" + "="*60)
        logger.info("INGESTION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total products processed: {self.stats['total_products']}")
        logger.info(f"✅ Successfully added: {self.stats['successful']}")
        logger.info(f"⏭️  Already existed: {self.stats['already_exists']}")
        logger.info(f"❌ Failed: {self.stats['failed']}")
        logger.info(f"🎨 Total colors added: {self.stats['colors_added']}")
        logger.info(f"📏 Total fits added: {self.stats['fits_added']}")
        
        if self.stats['successful'] > 0:
            avg_colors = self.stats['colors_added'] / self.stats['successful']
            avg_fits = self.stats['fits_added'] / self.stats['successful']
            logger.info(f"📊 Avg colors per product: {avg_colors:.1f}")
            logger.info(f"📊 Avg fits per product: {avg_fits:.1f}")


def main():
    """Main execution"""
    # Missing product codes from our analysis
    MISSING_PRODUCTS = [
        'BE076', 'BE077', 'BE163', 'BE164', 'BE546', 'BE554', 'BE986', 'BE998', 
        'BE999', 'BJ705', 'BN126', 'BT549', 'BT743', 'BT744', 'BX291', 'BZ532', 
        'CC100', 'CC101', 'CJ508', 'CM237', 'CM390', 'CN406', 'ME053', 'ME183', 
        'MP235', 'MP600', 'MP653', 'MP712'
    ]
    
    import argparse
    parser = argparse.ArgumentParser(description='Ingest missing J.Crew products')
    parser.add_argument('--test', action='store_true', help='Test with first 3 products only')
    parser.add_argument('--codes', nargs='+', help='Specific product codes to ingest')
    
    args = parser.parse_args()
    
    if args.codes:
        products_to_ingest = args.codes
    elif args.test:
        products_to_ingest = MISSING_PRODUCTS[:3]
        logger.info("🧪 TEST MODE - Processing first 3 products only")
    else:
        products_to_ingest = MISSING_PRODUCTS
    
    # Create ingestor and run
    ingestor = JCrewProductIngestor()
    
    try:
        ingestor.ingest_products(products_to_ingest)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"jcrew_ingestion_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'products_processed': products_to_ingest,
                'stats': ingestor.stats
            }, f, indent=2)
        logger.info(f"\n💾 Results saved to {results_file}")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Ingestion interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Ingestion failed: {e}")
        raise


if __name__ == "__main__":
    main()

