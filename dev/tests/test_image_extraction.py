#!/usr/bin/env python3
"""
Test script to verify product image extraction from URLs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'ios_app', 'Backend'))

from app import extract_product_image_from_url

def test_image_extraction():
    """Test product image extraction with real URLs"""
    
    test_urls = [
        "https://bananarepublic.gap.com/browse/product.do?pid=704275052&vid=1&pcid=80117&cid=80117&nav=meganav%3AMen%3AMEN%27S+CLOTHING%3AT-Shirts#pdp-page-content",
        "https://www.jcrew.com/m/mens/categories/clothing/shirts/broken-in-oxford/short-sleeve-broken-in-organic-cotton-oxford-shirt/MP235?display=standard&fit=Classic&colorProductCode=BE986"
    ]
    
    print("🖼️  Testing Product Image Extraction")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🧪 Test {i}: {url}")
        
        try:
            image_url = extract_product_image_from_url(url)
            print(f"✅ Extracted image URL: {image_url}")
            
            # Check if it's a valid image URL
            if image_url.startswith('http') and any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                print("✅ Valid image URL format")
            elif 'placeholder' in image_url:
                print("⚠️  Using placeholder image (extraction failed)")
            else:
                print("❌ Invalid image URL format")
                
        except Exception as e:
            print(f"❌ Error extracting image: {str(e)}")
    
    print("\n✅ Image extraction testing completed!")

if __name__ == "__main__":
    test_image_extraction()
