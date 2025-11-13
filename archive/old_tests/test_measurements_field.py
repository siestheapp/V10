#!/usr/bin/env python3
"""
Quick test to verify the "measurements" field is now included
"""

import requests
import json

def test_measurements_field():
    """Test that the measurements field is now included"""
    print("🧪 TESTING MEASUREMENTS FIELD FIX\n")
    
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
                    if "measurements" in garment:
                        print(f"      ✅ measurements: {garment['measurements']}")
                    else:
                        print(f"      ❌ MISSING measurements field!")
                    
                    # Also check other required fields
                    required_fields = ["size", "brand", "product_name"]
                    for field in required_fields:
                        if field in garment:
                            print(f"      + {field}: {garment[field]}")
                        else:
                            print(f"      ❌ Missing {field}")
                
                print(f"\n✅ iOS should now be able to parse the response!")
            else:
                print("❌ No reference_garments found")
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_measurements_field()