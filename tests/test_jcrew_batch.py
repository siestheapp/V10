#!/usr/bin/env python3
"""
J.Crew Batch URL Testing Script
Tests multiple J.Crew product URLs to verify product data extraction
"""

import requests
import json
import time
import sys
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Backend server URL
BACKEND_URL = "http://localhost:8006"

# Test URLs - Real J.Crew URLs provided by user
TEST_URLS = [
    "https://www.jcrew.com/m/mens/categories/clothing/polos/cotton-pique/MP133?display=standard&fit=Classic&colorProductCode=BJ304&colorCode=BL8133",
    "https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/somelos/portuguese-cotton-poplin-shirt/CM238?display=standard&fit=Classic&color_name=perry-stripe-white-blue&colorProductCode=CM238",
    "https://www.jcrew.com/p/mens/categories/clothing/sweaters/polo/CJ379?display=standard&fit=Classic&colorProductCode=CJ379&colorCode=HT2984",
    "https://www.jcrew.com/p/mens/categories/clothing/coats-and-jackets/bomber-jacket/BJ059?display=standard&fit=Classic&colorProductCode=BJ059&colorCode=WZ7393",
    "https://www.jcrew.com/m/mens/categories/clothing/sweaters/crewneck/ME681?display=standard&fit=Classic&colorProductCode=BE895&colorCode=BL8133"
]

def test_single_url(url: str, user_id: int = 1) -> Dict:
    """Test a single J.Crew URL"""
    print(f"\n🔍 Testing: {url}")
    
    try:
        # Call the process-url endpoint
        response = requests.post(
            f"{BACKEND_URL}/garment/process-url",
            json={
                "product_url": url,
                "user_id": user_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract key information
            result = {
                "url": url,
                "status": "✅ SUCCESS",
                "product_name": data.get("product_name", "N/A"),
                "brand": data.get("brand_name", "N/A"),
                "product_code": data.get("product_code", "N/A"),
                "image_url": data.get("product_image", "N/A"),
                "sizes": data.get("sizes_available", []),
                "colors": data.get("colors_available", []),
                "fit_options": data.get("fit_options", []),
                "price": data.get("price", "N/A"),
                "category": data.get("category", "N/A"),
                "subcategory": data.get("subcategory", "N/A"),
                "response_time": response.elapsed.total_seconds()
            }
            
            # Print summary
            print(f"  ✅ {result['product_name']}")
            print(f"  📦 Code: {result['product_code']}")
            print(f"  🏷️  Category: {result['category']} > {result['subcategory']}")
            print(f"  📏 Sizes: {result['sizes']}")
            print(f"  🎨 Colors: {len(result['colors'])} available")
            print(f"  👔 Fit Options: {result['fit_options']}")
            print(f"  💰 Price: ${result['price']}" if result['price'] != "N/A" else "  💰 Price: Not found")
            print(f"  🖼️  Image: {'✅ Found' if result['image_url'] and result['image_url'] != 'N/A' else '❌ Missing'}")
            print(f"  ⏱️  Response Time: {result['response_time']:.2f}s")
            
            return result
            
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f": {error_data.get('detail', 'Unknown error')}"
            except:
                error_msg += f": {response.text[:100]}"
            
            result = {
                "url": url,
                "status": f"❌ FAILED - {error_msg}",
                "error": error_msg,
                "response_time": response.elapsed.total_seconds()
            }
            
            print(f"  ❌ {error_msg}")
            return result
            
    except requests.exceptions.Timeout:
        result = {
            "url": url,
            "status": "❌ TIMEOUT",
            "error": "Request timed out after 30 seconds"
        }
        print(f"  ❌ Timeout after 30 seconds")
        return result
        
    except Exception as e:
        result = {
            "url": url,
            "status": f"❌ ERROR - {str(e)}",
            "error": str(e)
        }
        print(f"  ❌ Error: {e}")
        return result

def test_batch_sequential(urls: List[str], user_id: int = 1) -> List[Dict]:
    """Test URLs one by one (sequential)"""
    print(f"\n🚀 Testing {len(urls)} URLs sequentially...")
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] ", end="")
        result = test_single_url(url, user_id)
        results.append(result)
        
        # Small delay to be nice to the server
        time.sleep(1)
    
    return results

def test_batch_parallel(urls: List[str], user_id: int = 1, max_workers: int = 3) -> List[Dict]:
    """Test URLs in parallel (faster but more intensive)"""
    print(f"\n🚀 Testing {len(urls)} URLs in parallel (max {max_workers} concurrent)...")
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_url = {
            executor.submit(test_single_url, url, user_id): url 
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
    """Print a summary of all test results"""
    print(f"\n{'='*80}")
    print(f"📊 BATCH TEST SUMMARY")
    print(f"{'='*80}")
    
    successful = [r for r in results if r['status'].startswith('✅')]
    failed = [r for r in results if not r['status'].startswith('✅')]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if 'response_time' in results[0]:
        avg_time = sum(r.get('response_time', 0) for r in results) / len(results)
        print(f"⏱️  Average Response Time: {avg_time:.2f}s")
    
    # Success details
    if successful:
        print(f"\n✅ SUCCESSFUL PRODUCTS:")
        for result in successful:
            print(f"  • {result['product_name']} ({result.get('product_code', 'No code')})")
            if result.get('fit_options'):
                print(f"    Fit Options: {result['fit_options']}")
    
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
        print(f"\n📦 CATEGORIES FOUND:")
        for category, count in categories.items():
            print(f"  • {category}: {count} products")

def check_backend_status():
    """Check if the backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/brands", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend is running at {BACKEND_URL}")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend at {BACKEND_URL}: {e}")
        return False

def main():
    """Main function"""
    print("🧪 J.Crew Batch URL Tester")
    print("="*50)
    
    # Check backend
    if not check_backend_status():
        print("\n💡 Make sure the backend is running:")
        print("   cd /Users/seandavey/projects/V10")
        print("   ./start_backend.sh")
        return
    
    # Get URLs to test
    urls_to_test = TEST_URLS
    
    if len(sys.argv) > 1:
        # URLs provided as command line arguments
        urls_to_test = sys.argv[1:]
        print(f"\n📝 Testing {len(urls_to_test)} URLs from command line")
    else:
        print(f"\n📝 Testing {len(urls_to_test)} default URLs")
    
    # Ask for test mode
    print(f"\nChoose test mode:")
    print(f"1. Sequential (slower, easier on server)")
    print(f"2. Parallel (faster, more intensive)")
    
    try:
        choice = input("Enter choice (1 or 2, default=1): ").strip()
        if choice == "2":
            results = test_batch_parallel(urls_to_test, max_workers=3)
        else:
            results = test_batch_sequential(urls_to_test)
        
        # Print summary
        print_summary(results)
        
        # Save results to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"jcrew_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
