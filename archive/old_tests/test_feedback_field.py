#!/usr/bin/env python3
"""
Quick test to verify the "feedback" field is now included
"""

import requests
import json

def test_feedback_field():
    """Test that the feedback field is now included"""
    print("🧪 TESTING FEEDBACK FIELD FIX\n")
    
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
                    if "feedback" in garment:
                        print(f"      ✅ feedback: {garment['feedback']}")
                    else:
                        print(f"      ❌ MISSING feedback field!")
                    
                    # Also check if fit_feedback is still there
                    if "fit_feedback" in garment:
                        print(f"      + fit_feedback: {garment['fit_feedback']}")
                    
                    # List all other required fields that should be present
                    required_fields = ["size", "brand", "product_name", "measurements"]
                    for field in required_fields:
                        if field in garment:
                            if field == "measurements":
                                print(f"      + {field}: {type(garment[field]).__name__} object")
                            else:
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
    test_feedback_field()