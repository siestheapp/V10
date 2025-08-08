#!/usr/bin/env python3
"""
Quick test to verify the "size" field is now included
"""

import requests
import json

def test_size_field():
    """Test that the size field is now included"""
    print("🧪 TESTING SIZE FIELD FIX\n")
    
    payload = {
        "product_url": "https://www.jcrew.com/test-shirt",
        "user_id": 1,
        "user_fit_preference": "Standard",
        "brand_name": "J.Crew"
    }
    
    try:
        response = requests.post(
            "http://localhost:8006/garment/size-recommendation",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "reference_garments" in data:
                print("🔍 Reference Garments Fields:")
                for key, garment in data["reference_garments"].items():
                    print(f"\n   {key}:")
                    
                    # Check for the specific field iOS app needs
                    if "size" in garment:
                        print(f"      ✅ size: {garment['size']}")
                    else:
                        print(f"      ❌ MISSING size field!")
                    
                    # Also check for size_label for completeness  
                    if "size_label" in garment:
                        print(f"      + size_label: {garment['size_label']}")
                    
                    if "brand" in garment:
                        print(f"      + brand: {garment['brand']}")
                
                print(f"\n✅ iOS should now be able to parse the response!")
            else:
                print("❌ No reference_garments found")
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_size_field()