#!/usr/bin/env python3
"""
Test J.Crew integration end-to-end
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_jcrew_products():
    """Test various J.Crew product URLs"""
    
    test_cases = [
        {
            "name": "Men's Casual Shirt",
            "url": "https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/BH290",
            "should_work": True
        },
        {
            "name": "Men's Oxford Shirt", 
            "url": "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996",
            "should_work": True
        },
        {
            "name": "Men's T-Shirt",
            "url": "https://www.jcrew.com/p/mens/categories/clothing/t-shirts-polos/long-sleeve-t-shirts/long-sleeve-broken-in-t-shirt/AW939",
            "should_work": True
        },
        {
            "name": "Men's Sweater",
            "url": "https://www.jcrew.com/p/mens/categories/clothing/sweaters/pullover/cotton-crewneck-sweater/AY671",
            "should_work": True
        },
        {
            "name": "Men's Jacket (Outerwear)",
            "url": "https://www.jcrew.com/p/mens/categories/clothing/coats-and-jackets/quilted-jacket/BU292",
            "should_work": True
        },
        {
            "name": "Women's Dress (Should Fail)",
            "url": "https://www.jcrew.com/p/womens/categories/clothing/dresses/midi/BQ825",
            "should_work": False
        },
        {
            "name": "Men's Pants",
            "url": "https://www.jcrew.com/p/mens/categories/clothing/pants/chino/770-straight-fit-chino/E1589",
            "should_work": True
        }
    ]
    
    print("=" * 60)
    print("🧪 TESTING J.CREW INTEGRATION")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\n📦 Testing: {test['name']}")
        print(f"   URL: {test['url'][:60]}...")
        
        try:
            response = requests.post(f"{BASE_URL}/tryon/start", json={
                "product_url": test["url"],
                "user_id": "1"
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS: {data.get('product_name', 'Unknown')}")
                print(f"      Sizes: {data.get('size_options', [])[:5]}...")
                print(f"      Image: {'Yes' if data.get('product_image') else 'No'}")
                
                if not test["should_work"]:
                    print(f"   ⚠️  WARNING: This should have failed but didn't")
                    
            elif response.status_code == 400:
                error = response.json().get('detail', 'Unknown error')
                print(f"   ❌ REJECTED: {error}")
                
                if test["should_work"]:
                    print(f"   ⚠️  WARNING: This should have worked but didn't")
                    
            else:
                print(f"   ❌ ERROR: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Cannot connect to backend. Is it running?")
            print(f"      Run: cd src/ios_app/Backend && python app.py")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print("✅ Men's shirts, t-shirts, sweaters → Should work")
    print("✅ Men's outerwear (jackets, coats) → Should work")
    print("✅ Men's pants/chinos → Should work")
    print("❌ Women's products → Should be rejected")

if __name__ == "__main__":
    test_jcrew_products()
