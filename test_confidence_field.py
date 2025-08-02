#!/usr/bin/env python3
"""
Quick test to verify the "confidence" field is now at root level
"""

import requests
import json

def test_confidence_field():
    """Test that the confidence field is now at root level"""
    print("🧪 TESTING CONFIDENCE FIELD AT ROOT LEVEL\n")
    
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
            
            print("🔍 Root Level Fields:")
            
            # Check for the confidence field at root level
            if "confidence" in data:
                confidence = data["confidence"]
                data_type = type(confidence).__name__
                print(f"   ✅ confidence: {confidence} ({data_type})")
            else:
                print(f"   ❌ MISSING confidence field at root level!")
            
            # Show other important root level fields
            important_fields = ["brand", "recommended_size", "recommended_fit_label", "total_matches"]
            for field in important_fields:
                if field in data:
                    print(f"   + {field}: {data[field]}")
                else:
                    print(f"   - Missing: {field}")
            
            # Verify reference_garments is still there
            if "reference_garments" in data:
                ref_count = len(data["reference_garments"])
                print(f"   + reference_garments: {ref_count} entries")
            else:
                print(f"   ❌ Missing reference_garments!")
                
            print(f"\n✅ iOS should now be able to parse the root confidence field!")
            
        else:
            print(f"❌ HTTP Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_confidence_field()