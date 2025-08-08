#!/usr/bin/env python3
"""
Main script to run Banana Republic scraper.

Usage:
    python run_banana_republic_scraper.py [--pages N] [--test]
"""

import sys
import argparse
from pathlib import Path

# Add the scrapers directory to Python path
scrapers_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scrapers_dir))

sys.path.append(str(scrapers_dir))

from scrapers.banana_republic import BananaRepublicScraper
from config.database import db_config

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Run Banana Republic scraper')
    parser.add_argument('--pages', type=int, default=3, 
                       help='Maximum pages to scrape (default: 3)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode - only scrape first page')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Test database connection first
    print("Testing database connection...")
    if not db_config.test_connection():
        print("❌ Database connection failed!")
        print("Please check your database configuration in .env file")
        return 1
    
    print("✅ Database connection successful!")
    
    # Set parameters based on arguments
    max_pages = 1 if args.test else args.pages
    
    print(f"\n🚀 Starting Banana Republic scraper...")
    print(f"📄 Max pages: {max_pages}")
    print(f"🧪 Test mode: {args.test}")
    print("-" * 50)
    
    try:
        # Initialize scraper
        scraper = BananaRepublicScraper()
        
        # Run scraping session
        result = scraper.run_scraping_session(
            category="Casual Shirts",
            target_url="https://bananarepublic.gap.com/browse/men/casual-shirts?cid=44873",
            max_pages=max_pages
        )
        
        # Print results
        print("\n" + "=" * 50)
        print("📊 SCRAPING RESULTS")
        print("=" * 50)
        
        if result['status'] == 'success':
            print(f"✅ Status: {result['status'].upper()}")
            print(f"🔍 Products found: {result['products_found']}")
            print(f"➕ Products added: {result['products_added']}")
            print(f"🔄 Products updated: {result['products_updated']}")
            print(f"❌ Errors: {result['errors_count']}")
            print(f"⏱️  Duration: {result['duration_seconds']} seconds")
            print(f"🆔 Run ID: {result['run_id']}")
            
            if args.test:
                print("\n🧪 Test completed successfully!")
                print("Run without --test flag to scrape all pages.")
            
            return 0
            
        else:
            print(f"❌ Status: {result['status'].upper()}")
            print(f"🔍 Error: {result['error']}")
            print(f"⏱️  Duration: {result['duration_seconds']} seconds")
            print(f"🆔 Run ID: {result['run_id']}")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Scraping interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
