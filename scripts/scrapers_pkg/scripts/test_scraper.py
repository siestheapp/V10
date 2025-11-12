#!/usr/bin/env python3
"""
Test script for scraper functionality.
"""

import sys
from pathlib import Path

# Add the scrapers directory to Python path
scrapers_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scrapers_dir))

sys.path.append(str(scrapers_dir))

from config.database import db_config
from scrapers.banana_republic import BananaRepublicScraper

def test_database_connection():
    """Test database connectivity."""
    print("🔍 Testing database connection...")
    
    try:
        if db_config.test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_scraper_initialization():
    """Test scraper initialization."""
    print("\n🔍 Testing scraper initialization...")
    
    try:
        scraper = BananaRepublicScraper()
        print(f"✅ Scraper initialized successfully!")
        print(f"   Brand: {scraper.brand_name}")
        print(f"   Base URL: {scraper.base_url}")
        return True
    except Exception as e:
        print(f"❌ Scraper initialization failed: {e}")
        return False

def test_page_fetch():
    """Test fetching a single page."""
    print("\n🔍 Testing page fetch...")
    
    try:
        scraper = BananaRepublicScraper()
        test_url = "https://bananarepublic.gap.com/browse/men/casual-shirts?cid=44873"
        
        soup = scraper.get_page_content(test_url)
        
        if soup:
            print("✅ Page fetch successful!")
            print(f"   Page title: {soup.title.string if soup.title else 'No title'}")
            print(f"   Page length: {len(str(soup))} characters")
            return True
        else:
            print("❌ Page fetch failed!")
            return False
            
    except Exception as e:
        print(f"❌ Page fetch error: {e}")
        return False

def test_product_parsing():
    """Test parsing products from a page."""
    print("\n🔍 Testing product parsing...")
    
    try:
        scraper = BananaRepublicScraper()
        test_url = "https://bananarepublic.gap.com/browse/men/casual-shirts?cid=44873"
        
        soup = scraper.get_page_content(test_url)
        if not soup:
            print("❌ Could not fetch page for parsing test")
            return False
        
        products = scraper.parse_product_listing(str(soup), test_url)
        
        print(f"✅ Product parsing successful!")
        print(f"   Products found: {len(products)}")
        
        if products:
            sample_product = products[0]
            print(f"   Sample product:")
            print(f"     Name: {sample_product.name}")
            print(f"     URL: {sample_product.product_url}")
            print(f"     Price: ${sample_product.price}" if sample_product.price else "     Price: Not found")
            print(f"     External ID: {sample_product.external_id}")
        
        return len(products) > 0
        
    except Exception as e:
        print(f"❌ Product parsing error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_operations():
    """Test database operations."""
    print("\n🔍 Testing database operations...")
    
    try:
        from utils.db_utils import db_manager
        
        # Test getting brand ID
        brand_id = db_manager.get_brand_id("Banana Republic")
        if brand_id:
            print(f"✅ Found Banana Republic brand ID: {brand_id}")
        else:
            print("❌ Could not find Banana Republic brand")
            return False
        
        # Test getting category ID
        category_id = db_manager.get_category_id("Shirts")
        if category_id:
            print(f"✅ Found Shirts category ID: {category_id}")
        else:
            print("⚠️  Could not find Shirts category (this is okay)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 SCRAPER TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Scraper Initialization", test_scraper_initialization),
        ("Page Fetch", test_page_fetch),
        ("Product Parsing", test_product_parsing),
        ("Database Operations", test_database_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! The scraper is ready to use.")
        print("\nNext steps:")
        print("1. Run: python scripts/run_banana_republic_scraper.py --test")
        print("2. If successful, run: python scripts/run_banana_republic_scraper.py --pages 3")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix issues before running the scraper.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
