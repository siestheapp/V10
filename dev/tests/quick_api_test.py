#!/usr/bin/env python3
"""
Quick API testing script for fast backend development
Run this to test API endpoints without iOS simulator
"""

import requests
import json
import time

BASE_URL = "http://localhost:8006"

def test_scan_recommendation():
    """Test the scan recommendation endpoint"""
    print("🧪 Testing scan recommendation...")
    
    test_url = "https://bananarepublic.gap.com/browse/product.do?pid=704275052"
    
    payload = {
        "product_url": test_url,
        "user_id": 1,
        "fit_preference": "Standard"
    }
    
    try:
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/garment/size-recommendation", json=payload)
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"   Brand: {result.get('brand')}")
            print(f"   Recommended Size: {result.get('recommended_size')}")
            print(f"   Confidence: {result.get('confidence')}")
            print(f"   Product Name: {result.get('product_name', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")

def test_scan_history():
    """Test the scan history endpoint"""
    print("\n🧪 Testing scan history...")
    
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/scan_history?user_id=1")
        end_time = time.time()
        
        print(f"⏱️  Response time: {end_time - start_time:.2f}s")
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ Success! Found {len(history)} items")
            for item in history[:3]:  # Show first 3
                print(f"   - {item.get('name')} ({item.get('brand')}) - Size: {item.get('scannedSize')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")

def test_product_name_extraction():
    """Test product name extraction directly"""
    print("\n🧪 Testing product name extraction...")
    
    import sys
    sys.path.append('src/ios_app/Backend')
    from app import extract_product_name_from_url
    
    test_url = "https://bananarepublic.gap.com/browse/product.do?pid=704275052"
    
    start_time = time.time()
    product_name = extract_product_name_from_url(test_url)
    end_time = time.time()
    
    print(f"⏱️  Extraction time: {end_time - start_time:.2f}s")
    print(f"✅ Product name: '{product_name}'")

if __name__ == "__main__":
    print("🚀 Quick API Testing")
    print("=" * 50)
    
    test_scan_recommendation()
    test_scan_history()
    test_product_name_extraction()
    
    print("\n✅ Testing completed!")
