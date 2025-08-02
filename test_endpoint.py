#!/usr/bin/env python3
"""
Test the actual HTTP endpoint to ensure complete iOS compatibility
"""

import requests
import json

def test_endpoint():
    """Test the /garment/size-recommendation endpoint"""
    print("🧪 TESTING ACTUAL HTTP ENDPOINT\n")
    
    # Test payload
    payload = {
        "product_url": "https://www.jcrew.com/test-shirt",
        "user_id": 1,
        "user_fit_preference": "Standard",
        "brand_name": "J.Crew"
    }
    
    try:
        # Make request to local endpoint
        response = requests.post(
            "http://localhost:5001/garment/size-recommendation",
            json=payload,
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - JSON Response received")
            
            # Check for reference_garments field
            if "reference_garments" in data:
                print(f"\n🔍 Reference Garments Found:")
                ref_garments = data["reference_garments"]
                
                for key, garment in ref_garments.items():
                    print(f"   {key}:")
                    if "brand" in garment:
                        print(f"      ✓ brand: {garment['brand']}")
                    else:
                        print(f"      ❌ Missing brand field!")
                    
                    print(f"      + product_name: {garment.get('product_name', 'MISSING')}")
                    print(f"      + dimension: {garment.get('dimension', 'MISSING')}")
                
                print(f"\n✅ iOS compatibility should be fixed!")
            else:
                print(f"❌ No reference_garments field found!")
            
            # Show key response fields
            print(f"\n📊 Key Response Fields:")
            key_fields = ['brand', 'recommended_size', 'recommended_fit_label', 'total_matches']
            for field in key_fields:
                if field in data:
                    print(f"   ✓ {field}: {data[field]}")
                else:
                    print(f"   ❌ Missing: {field}")
                    
        else:
            print(f"❌ ERROR - Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Is the backend running on port 5001?")
        print(f"   Try: cd src/ios_app/Backend && python app.py")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_endpoint()