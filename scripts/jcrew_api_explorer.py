#!/usr/bin/env python3
"""
J.Crew API Explorer - Discover and test J.Crew's internal APIs
Based on network traffic analysis
"""

import requests
import json
from typing import Dict, Optional
import re

class JCrewAPIExplorer:
    """Explore J.Crew's internal APIs to get complete product data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.jcrew.com/',
            'Origin': 'https://www.jcrew.com'
        })
    
    def test_product_api_endpoints(self, product_code: str = "BE996"):
        """
        Test various API endpoints we discovered from network traffic
        """
        print("🔍 Testing J.Crew API Endpoints...")
        print("=" * 80)
        
        results = {}
        
        # Based on the XHR requests you showed:
        endpoints = [
            # The UUID-style JSON endpoints (these might be product-specific)
            {
                'name': 'Product Details API (UUID style)',
                'url': 'https://www.jcrew.com/api/v1/products/{product_code}/details',
                'method': 'GET'
            },
            {
                'name': 'BlueCore Product API',
                'url': 'https://api.bluecore.com/api/track/jcrew_us.json',
                'method': 'GET',
                'params': {'product_id': product_code}
            },
            {
                'name': 'Product Data API',
                'url': f'https://www.jcrew.com/data/v1/US/products/{product_code}',
                'method': 'GET'
            },
            {
                'name': 'Product Search API',
                'url': f'https://www.jcrew.com/api/productsearch/products/{product_code}',
                'method': 'GET'
            },
            {
                'name': 'Product Catalog API',
                'url': f'https://www.jcrew.com/r/api/products/{product_code}',
                'method': 'GET'
            },
            {
                'name': 'GraphQL Product Query',
                'url': 'https://www.jcrew.com/api/graphql',
                'method': 'POST',
                'json': {
                    'query': '''
                    query GetProduct($productCode: String!) {
                        product(code: $productCode) {
                            name
                            description
                            materials
                            fabricContent
                            careInstructions
                            details
                            price {
                                regularPrice
                                salePrice
                            }
                            variants {
                                color
                                size
                                fit
                            }
                        }
                    }
                    ''',
                    'variables': {'productCode': product_code}
                }
            }
        ]
        
        for endpoint in endpoints:
            print(f"\n📡 Testing: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            try:
                if endpoint['method'] == 'GET':
                    url = endpoint['url'].format(product_code=product_code)
                    params = endpoint.get('params', {})
                    response = self.session.get(url, params=params, timeout=5)
                else:  # POST
                    response = self.session.post(
                        endpoint['url'],
                        json=endpoint.get('json', {}),
                        timeout=5
                    )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   ✅ Success! Got JSON response")
                        print(f"   Response size: {len(response.text)} bytes")
                        
                        # Check if response contains useful product data
                        useful_fields = ['material', 'fabric', 'description', 'care', 'detail', 'cotton', 'polyester']
                        response_text = json.dumps(data).lower()
                        found_fields = [field for field in useful_fields if field in response_text]
                        
                        if found_fields:
                            print(f"   🎯 Found product details: {', '.join(found_fields)}")
                            results[endpoint['name']] = data
                            
                            # Pretty print a sample
                            print(f"   Sample data:")
                            sample = json.dumps(data, indent=2)[:500]
                            for line in sample.split('\n')[:10]:
                                print(f"      {line}")
                    except:
                        print(f"   ⚠️ Got response but not valid JSON")
                elif response.status_code == 404:
                    print(f"   ❌ Not Found")
                elif response.status_code == 403:
                    print(f"   🔒 Forbidden (might need auth)")
                else:
                    print(f"   ❌ Failed")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏱️ Timeout")
            except requests.exceptions.ConnectionError:
                print(f"   🔌 Connection Error")
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
        
        return results
    
    def fetch_from_page_resources(self, product_url: str):
        """
        Fetch the product page and look for embedded JSON data
        """
        print("\n🌐 Fetching product page to find embedded data...")
        print("=" * 80)
        
        response = self.session.get(product_url)
        if response.status_code != 200:
            print(f"❌ Failed to fetch page: {response.status_code}")
            return None
        
        html = response.text
        print(f"✅ Got page ({len(html)} bytes)")
        
        # Look for embedded JSON in various formats
        patterns = [
            # Next.js data
            (r'<script id="__NEXT_DATA__"[^>]*>([^<]+)</script>', '__NEXT_DATA__'),
            # Window variables
            (r'window\.__INITIAL_STATE__\s*=\s*({[^;]+});', '__INITIAL_STATE__'),
            (r'window\.productData\s*=\s*({[^;]+});', 'productData'),
            (r'window\.jcrew\.product\s*=\s*({[^;]+});', 'jcrew.product'),
            # Data attributes
            (r'data-product-json=[\'"]([^\'"]+)[\'"]', 'data-product-json'),
            (r'data-product=[\'"]([^\'"]+)[\'"]', 'data-product'),
        ]
        
        found_data = {}
        
        for pattern, name in patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            if matches:
                print(f"\n📦 Found {name}:")
                for match in matches[:1]:  # Just first match
                    try:
                        # Try to parse as JSON
                        if match.startswith('{'):
                            data = json.loads(match)
                        else:
                            # Might be HTML-encoded
                            import html as html_module
                            decoded = html_module.unescape(match)
                            data = json.loads(decoded)
                        
                        print(f"   ✅ Valid JSON ({len(match)} bytes)")
                        
                        # Check for product details
                        data_str = json.dumps(data).lower()
                        if any(word in data_str for word in ['material', 'fabric', 'cotton', 'care']):
                            print(f"   🎯 Contains product details!")
                            found_data[name] = data
                            
                            # Show sample
                            sample = json.dumps(data, indent=2)[:400]
                            for line in sample.split('\n')[:8]:
                                print(f"      {line}")
                    except:
                        print(f"   ⚠️ Found but couldn't parse as JSON")
        
        # Also check for those UUID-style endpoints in the HTML
        uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\.json'
        uuid_matches = re.findall(uuid_pattern, html)
        if uuid_matches:
            print(f"\n🔑 Found UUID JSON endpoints in page:")
            for uuid_file in set(uuid_matches):
                print(f"   • {uuid_file}")
                
                # Try to fetch it
                uuid_url = f"https://www.jcrew.com/{uuid_file}"
                try:
                    uuid_response = self.session.get(uuid_url, timeout=5)
                    if uuid_response.status_code == 200:
                        uuid_data = uuid_response.json()
                        print(f"     ✅ Fetched successfully!")
                        
                        # Check contents
                        data_str = json.dumps(uuid_data).lower()
                        if any(word in data_str for word in ['material', 'fabric', 'cotton', 'description']):
                            print(f"     🎯 Contains product details!")
                            found_data[f'UUID_{uuid_file[:8]}'] = uuid_data
                except:
                    pass
        
        return found_data


def main():
    """Test the API explorer"""
    print("=" * 80)
    print("J.CREW API EXPLORER")
    print("=" * 80)
    
    explorer = JCrewAPIExplorer()
    
    # Test with the Broken-in Oxford shirt
    product_code = "BE996"
    product_url = f"https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/{product_code}"
    
    print(f"🎯 Testing product: {product_code}")
    print(f"   URL: {product_url}")
    
    # Test various API endpoints
    api_results = explorer.test_product_api_endpoints(product_code)
    
    # Try to get data from the page itself
    page_data = explorer.fetch_from_page_resources(product_url)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if api_results:
        print(f"✅ Found {len(api_results)} working API endpoints")
        for name in api_results.keys():
            print(f"   • {name}")
    
    if page_data:
        print(f"\n✅ Found {len(page_data)} embedded data sources")
        for name in page_data.keys():
            print(f"   • {name}")
    
    # Save all results
    all_results = {
        'api_endpoints': api_results,
        'embedded_data': page_data
    }
    
    output_file = 'jcrew_api_discovery.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Saved all findings to {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()

