#!/usr/bin/env python3
"""
Test script to verify product name extraction from URLs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'ios_app', 'Backend'))

from app import extract_product_name_from_url

def test_product_name_extraction():
    """Test product name extraction with the actual Banana Republic URL"""
    
    # The actual URL from the most recent scan
    test_url = "https://bananarepublic.gap.com/browse/product.do?pid=704275052&vid=1&pcid=80117&cid=80117&nav=meganav%3AMen%3AMEN%27S+CLOTHING%3AT-Shirts#pdp-page-content"
    
    print("🧪 Testing product name extraction...")
    print(f"URL: {test_url}")
    
    try:
        product_name = extract_product_name_from_url(test_url)
        print(f"✅ Extracted product name: '{product_name}'")
        
        # Check if it's better than the hardcoded name
        expected_name = "BOXY LINEN-COTTON T-SHIRT"  # From the webpage
        hardcoded_name = "Organic Cotton Oxford Shirt"  # What we were using before
        
        print(f"\n📊 Comparison:")
        print(f"   Expected (from webpage): '{expected_name}'")
        print(f"   Extracted: '{product_name}'")
        print(f"   Old hardcoded: '{hardcoded_name}'")
        
        if product_name.lower() != hardcoded_name.lower():
            print("✅ SUCCESS: Extracted name is different from hardcoded name!")
        else:
            print("⚠️  WARNING: Extracted name matches hardcoded name")
            
        if "linen" in product_name.lower() or "boxy" in product_name.lower():
            print("✅ SUCCESS: Extracted name contains expected keywords!")
        else:
            print("⚠️  WARNING: Extracted name doesn't contain expected keywords")
            
    except Exception as e:
        print(f"❌ Error testing product name extraction: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing Product Name Extraction")
    print("=" * 50)
    
    test_product_name_extraction()
    
    print("\n✅ Test completed!")
