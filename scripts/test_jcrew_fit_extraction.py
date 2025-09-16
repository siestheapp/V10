#!/usr/bin/env python3
"""
Quick test of J.Crew fit extraction for specific products
"""

import sys
sys.path.append('/Users/seandavey/projects/V10')
sys.path.append('/Users/seandavey/projects/V10/scripts')

from jcrew_fit_crawler import JCrewFitCrawler
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_extraction():
    """Test fit extraction on known products"""
    
    # Test cases
    test_products = [
        {
            'name': 'Broken-in Oxford (Multiple Fits)',
            'code': 'BE996',
            'url': 'https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996',
            'expected': 'Should have multiple fit options (Classic, Slim, etc.)'
        },
        {
            'name': 'Ludlow Dress Shirt (Single Fit)',
            'code': 'BM493',
            'url': 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/ludlow/BM493',
            'expected': 'Should have no fit options (single fit only)'
        },
        {
            'name': 'Secret Wash Shirt',
            'code': 'H7182',
            'url': 'https://www.jcrew.com/p/H7182',
            'expected': 'Testing another product'
        }
    ]
    
    print("\n" + "="*70)
    print("J.CREW FIT EXTRACTION TEST")
    print("="*70 + "\n")
    
    # Initialize crawler (visible browser for testing)
    crawler = JCrewFitCrawler(headless=False)
    
    try:
        for idx, product in enumerate(test_products, 1):
            print(f"\nTest {idx}: {product['name']}")
            print(f"URL: {product['url']}")
            print(f"Expected: {product['expected']}")
            print("-" * 50)
            
            # Extract fits
            fits = crawler.extract_fit_options(product['url'], product['code'])
            
            # Report results
            if fits:
                print(f"✅ FOUND {len(fits)} FIT OPTIONS: {fits}")
            else:
                print(f"⚠️ NO FIT OPTIONS FOUND (single fit product)")
            
            print("-" * 50)
            
            # Wait between products
            import time
            time.sleep(3)
    
    finally:
        crawler.cleanup()
        print("\n" + "="*70)
        print("TEST COMPLETE")
        print("="*70 + "\n")

if __name__ == "__main__":
    test_extraction()
