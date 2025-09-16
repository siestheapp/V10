#!/usr/bin/env python3
"""
J.Crew Direct Product Testing Script
Tests J.Crew URLs directly using the JCrewProductFetcher to verify product data extraction
"""

import sys
import os
import json
import time
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the backend directory to Python path
sys.path.append('/Users/seandavey/projects/V10/src/ios_app/Backend')

# Test URLs - Real J.Crew URLs provided by user
TEST_URLS = [
    "https://www.jcrew.com/m/mens/categories/clothing/polos/cotton-pique/MP133?display=standard&fit=Classic&colorProductCode=BJ304&colorCode=BL8133",
    "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/somelos/portuguese-cotton-poplin-shirt/CM238?display=standard&fit=Classic&color_name=perry-stripe-white-blue&colorProductCode=CM238",
    "https://www.jcrew.com/p/mens/categories/clothing/sweaters/polo/CJ379?display=standard&fit=Classic&colorProductCode=CJ379&colorCode=HT2984",
    "https://www.jcrew.com/p/mens/categories/clothing/coats-and-jackets/bomber-jacket/BJ059?display=standard&fit=Classic&colorProductCode=BJ059&colorCode=WZ7393",
    "https://www.jcrew.com/m/mens/categories/clothing/sweaters/crewneck/ME681?display=standard&fit=Classic&colorProductCode=BE895&colorCode=BL8133"
]

def test_single_url(url: str, fetcher) -> Dict:
    """Test a single J.Crew URL using the fetcher directly"""
    print(f"\n🔍 Testing: {url}")
    
    start_time = time.time()
    
    try:
        # Use the J.Crew fetcher directly
        product_data = fetcher.fetch_product(url)
        
        response_time = time.time() - start_time
        
        if product_data:
            result = {
                "url": url,
                "status": "✅ SUCCESS",
                "product_name": product_data.get("product_name", "N/A"),
                "product_code": product_data.get("product_code", "N/A"),
                "image_url": product_data.get("product_image", "N/A"),
                "sizes": product_data.get("sizes_available", []),
                "colors": product_data.get("colors_available", []),
                "fit_options": product_data.get("fit_options", []),
                "price": product_data.get("price", "N/A"),
                "category": product_data.get("category", "N/A"),
                "subcategory": product_data.get("subcategory", "N/A"),
                "material": product_data.get("material", "N/A"),
                "fit_type": product_data.get("fit_type", "N/A"),
                "response_time": response_time,
                "raw_data": product_data  # Include full data for debugging
            }
            
            # Print summary
            print(f"  ✅ {result['product_name']}")
            print(f"  📦 Code: {result['product_code']}")
            print(f"  🏷️  Category: {result['category']} > {result['subcategory']}")
            print(f"  📏 Sizes: {result['sizes']}")
            print(f"  🎨 Colors: {len(result['colors'])} colors - {result['colors'][:3]}{'...' if len(result['colors']) > 3 else ''}")
            print(f"  👔 Fit Options: {result['fit_options']}")
            print(f"  💰 Price: ${result['price']}" if result['price'] and result['price'] != "N/A" else "  💰 Price: Not found")
            print(f"  🧵 Material: {result['material'][:50]}{'...' if len(result['material']) > 50 else result['material']}")
            print(f"  📐 Fit Type: {result['fit_type']}")
            print(f"  🖼️  Image: {'✅ Found' if result['image_url'] and result['image_url'] != 'N/A' else '❌ Missing'}")
            print(f"  ⏱️  Response Time: {result['response_time']:.2f}s")
            
            return result
            
        else:
            result = {
                "url": url,
                "status": "❌ FAILED - No product data returned",
                "error": "Fetcher returned None",
                "response_time": response_time
            }
            
            print(f"  ❌ No product data returned")
            return result
            
    except Exception as e:
        response_time = time.time() - start_time
        result = {
            "url": url,
            "status": f"❌ ERROR - {str(e)}",
            "error": str(e),
            "response_time": response_time
        }
        print(f"  ❌ Error: {e}")
        return result

def test_batch_sequential(urls: List[str], fetcher) -> List[Dict]:
    """Test URLs one by one (sequential)"""
    print(f"\n🚀 Testing {len(urls)} URLs sequentially...")
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] ", end="")
        result = test_single_url(url, fetcher)
        results.append(result)
        
        # Small delay to be nice to J.Crew's servers
        time.sleep(2)
    
    return results

def test_batch_parallel(urls: List[str], fetcher, max_workers: int = 2) -> List[Dict]:
    """Test URLs in parallel (faster but more intensive)"""
    print(f"\n🚀 Testing {len(urls)} URLs in parallel (max {max_workers} concurrent)...")
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_url = {
            executor.submit(test_single_url, url, fetcher): url 
            for url in urls
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            result = future.result()
            results.append(result)
    
    # Sort results by original URL order
    url_order = {url: i for i, url in enumerate(urls)}
    results.sort(key=lambda r: url_order.get(r['url'], 999))
    
    return results

def print_summary(results: List[Dict]):
    """Print a detailed summary of all test results"""
    print(f"\n{'='*80}")
    print(f"📊 J.CREW PRODUCT DATA EXTRACTION SUMMARY")
    print(f"{'='*80}")
    
    successful = [r for r in results if r['status'].startswith('✅')]
    failed = [r for r in results if not r['status'].startswith('✅')]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if results:
        avg_time = sum(r.get('response_time', 0) for r in results) / len(results)
        print(f"⏱️  Average Response Time: {avg_time:.2f}s")
    
    # Success details
    if successful:
        print(f"\n✅ SUCCESSFUL PRODUCTS:")
        for result in successful:
            print(f"\n  📦 {result['product_name']} ({result.get('product_code', 'No code')})")
            print(f"      Category: {result.get('category', 'N/A')} > {result.get('subcategory', 'N/A')}")
            print(f"      Sizes: {result.get('sizes', [])}")
            print(f"      Fit Options: {result.get('fit_options', [])}")
            print(f"      Colors: {len(result.get('colors', []))} available")
            print(f"      Price: ${result.get('price', 'N/A')}" if result.get('price') and result.get('price') != 'N/A' else f"      Price: Not found")
            print(f"      Image: {'✅' if result.get('image_url') and result.get('image_url') != 'N/A' else '❌'}")
    
    # Failure details
    if failed:
        print(f"\n❌ FAILED PRODUCTS:")
        for result in failed:
            print(f"  • {result['url']}")
            print(f"    Error: {result.get('error', 'Unknown error')}")
    
    # Product categories found
    categories = {}
    for result in successful:
        cat = result.get('category', 'Unknown')
        subcat = result.get('subcategory', 'Unknown')
        key = f"{cat} > {subcat}"
        categories[key] = categories.get(key, 0) + 1
    
    if categories:
        print(f"\n📦 CATEGORIES DETECTED:")
        for category, count in categories.items():
            print(f"  • {category}: {count} products")
    
    # Fit options analysis
    all_fit_options = set()
    for result in successful:
        fit_options = result.get('fit_options', [])
        all_fit_options.update(fit_options)
    
    if all_fit_options:
        print(f"\n👔 FIT OPTIONS FOUND:")
        for fit_option in sorted(all_fit_options):
            print(f"  • {fit_option}")
    
    # Image extraction success rate
    images_found = sum(1 for r in successful if r.get('image_url') and r.get('image_url') != 'N/A')
    if successful:
        image_success_rate = (images_found / len(successful)) * 100
        print(f"\n🖼️  IMAGE EXTRACTION: {images_found}/{len(successful)} ({image_success_rate:.1f}% success rate)")

def main():
    """Main function"""
    print("🧪 J.Crew Direct Product Data Tester")
    print("="*50)
    
    # Import and initialize the J.Crew fetcher
    try:
        from jcrew_fetcher import JCrewProductFetcher
        fetcher = JCrewProductFetcher()
        print("✅ J.Crew fetcher initialized successfully")
    except ImportError as e:
        print(f"❌ Could not import JCrewProductFetcher: {e}")
        print("Make sure you're running this from the correct directory")
        return
    except Exception as e:
        print(f"❌ Error initializing fetcher: {e}")
        return
    
    # Get URLs to test
    urls_to_test = TEST_URLS
    
    if len(sys.argv) > 1:
        # URLs provided as command line arguments
        urls_to_test = sys.argv[1:]
        print(f"\n📝 Testing {len(urls_to_test)} URLs from command line")
    else:
        print(f"\n📝 Testing {len(urls_to_test)} default URLs")
    
    # Show URLs being tested
    print(f"\n🔗 URLs to test:")
    for i, url in enumerate(urls_to_test, 1):
        print(f"  {i}. {url}")
    
    # Ask for test mode
    print(f"\nChoose test mode:")
    print(f"1. Sequential (slower, easier on J.Crew servers)")
    print(f"2. Parallel (faster, more intensive)")
    
    try:
        choice = input("Enter choice (1 or 2, default=1): ").strip()
        if choice == "2":
            results = test_batch_parallel(urls_to_test, fetcher, max_workers=2)
        else:
            results = test_batch_sequential(urls_to_test, fetcher)
        
        # Print summary
        print_summary(results)
        
        # Save results to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"jcrew_direct_test_results_{timestamp}.json"
        
        # Clean up results for JSON serialization (remove raw_data for cleaner output)
        clean_results = []
        for result in results:
            clean_result = {k: v for k, v in result.items() if k != 'raw_data'}
            clean_results.append(clean_result)
        
        with open(filename, 'w') as f:
            json.dump(clean_results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        
        # Also save detailed results with raw data
        detailed_filename = f"jcrew_detailed_results_{timestamp}.json"
        with open(detailed_filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Detailed results (with raw data) saved to: {detailed_filename}")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

