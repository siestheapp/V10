#!/usr/bin/env python3
"""
Simple script to update J.Crew product fit options directly
Processes one product at a time with immediate updates
"""

import sys
sys.path.append('/Users/seandavey/projects/V10')
sys.path.append('/Users/seandavey/projects/V10/scripts')

import psycopg2
from db_config import DB_CONFIG
from jcrew_fit_crawler import JCrewFitCrawler
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_single_product(product_code, product_url, crawler):
    """Update a single product's fit options"""
    try:
        # Extract fit options
        fits = crawler.extract_fit_options(product_url, product_code)
        
        # Create a new connection for each update
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
        
        try:
            if fits:
                cur.execute("""
                    UPDATE jcrew_product_cache 
                    SET fit_options = %s, updated_at = NOW()
                    WHERE product_code = %s
                """, (fits, product_code))
                logger.info(f"   ✅ Updated {product_code} with fits: {fits}")
                return 'has_fits'
            else:
                cur.execute("""
                    UPDATE jcrew_product_cache 
                    SET fit_options = NULL, updated_at = NOW()
                    WHERE product_code = %s
                """, (product_code,))
                logger.info(f"   ✅ Updated {product_code}: No fits (single fit product)")
                return 'no_fits'
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"   ❌ Error processing {product_code}: {e}")
        return 'error'

def main():
    """Process J.Crew products and update fit options"""
    
    print("\n" + "="*70)
    print("J.CREW FIT OPTIONS UPDATE")
    print("="*70 + "\n")
    
    # Get products to process
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Get products without fit data
    cur.execute("""
        SELECT product_code, product_name, product_url
        FROM jcrew_product_cache
        WHERE product_url IS NOT NULL
        AND fit_options IS NULL
        ORDER BY product_code
        LIMIT 20
    """)
    
    products = cur.fetchall()
    cur.close()
    conn.close()
    
    if not products:
        print("No products to process!")
        return
    
    print(f"Processing {len(products)} products...\n")
    
    # Initialize crawler
    crawler = JCrewFitCrawler(headless=True)
    
    # Statistics
    stats = {
        'has_fits': 0,
        'no_fits': 0,
        'error': 0
    }
    
    try:
        for idx, (code, name, url) in enumerate(products, 1):
            print(f"[{idx}/{len(products)}] {code}: {name[:40]}...")
            
            result = update_single_product(code, url, crawler)
            stats[result] += 1
            
            # Rate limiting
            time.sleep(2)
            
            # Progress update
            if idx % 5 == 0:
                print(f"\nProgress: {idx}/{len(products)} processed")
                print(f"  With fits: {stats['has_fits']}, Without fits: {stats['no_fits']}, Errors: {stats['error']}\n")
    
    finally:
        crawler.cleanup()
    
    # Final report
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total processed: {len(products)}")
    print(f"Products with fit options: {stats['has_fits']}")
    print(f"Products without fit options: {stats['no_fits']}")
    print(f"Errors: {stats['error']}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

