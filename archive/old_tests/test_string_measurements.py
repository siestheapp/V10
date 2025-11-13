#!/usr/bin/env python3
"""
Quick test to verify the measurements are now strings
"""

import requests
import json

def test_string_measurements():
    """Test that the measurements field contains strings, not numbers"""
    print("🧪 TESTING MEASUREMENTS AS STRINGS\n")
    
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
                print("🔍 Reference Garments Measurements:")
                for key, garment in data["reference_garments"].items():
                    print(f"\n   {key}:")
                    
                    if "measurements" in garment:
                        measurements = garment["measurements"]
                        print(f"      measurements object: {measurements}")
                        
                        # Check data types
                        for meas_key, meas_value in measurements.items():
                            data_type = type(meas_value).__name__
                            print(f"        {meas_key}: {meas_value} ({data_type})")
                            
                            if data_type == 'str':
                                print(f"          ✅ String type as expected")
                            else:
                                print(f"          ❌ Not string! iOS will fail to decode")
                    else:
                        print(f"      ❌ No measurements field")
                
                print(f"\n✅ Check if all measurement values are strings!")
            else:
                print("❌ No reference_garments found")
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_string_measurements()