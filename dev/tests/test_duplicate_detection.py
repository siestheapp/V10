#!/usr/bin/env python3
"""
Test script to verify duplicate detection in scan history
"""

import requests
import json
from datetime import datetime, timedelta

def test_scan_history_duplicate_detection():
    """Test that the scan history endpoint properly filters duplicates"""
    
    base_url = "http://localhost:8006"
    user_id = 1
    
    print("🧪 Testing scan history duplicate detection...")
    
    try:
        # Test the scan history endpoint
        response = requests.get(f"{base_url}/scan_history?user_id={user_id}")
        
        if response.status_code == 200:
            history_items = response.json()
            print(f"✅ Successfully loaded {len(history_items)} history items")
            
            # Check for duplicates by product URL and size
            seen_combinations = set()
            duplicates_found = []
            
            for item in history_items:
                product_url = item.get('productUrl', '')
                size = item.get('scannedSize', 'unknown')
                combination = f"{product_url}|{size}"
                
                if combination in seen_combinations:
                    duplicates_found.append({
                        'name': item.get('name'),
                        'brand': item.get('brand'),
                        'size': size,
                        'url': product_url
                    })
                else:
                    seen_combinations.add(combination)
            
            if duplicates_found:
                print(f"❌ Found {len(duplicates_found)} duplicates in scan history:")
                for dup in duplicates_found:
                    print(f"   - {dup['name']} ({dup['brand']}) - Size: {dup['size']}")
            else:
                print("✅ No duplicates found - duplicate detection is working!")
            
            # Show unique items
            print(f"\n📋 Unique items in scan history:")
            for item in history_items:
                print(f"   - {item.get('name')} ({item.get('brand')}) - Size: {item.get('scannedSize')}")
                
        else:
            print(f"❌ Failed to load scan history: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on port 8006.")
    except Exception as e:
        print(f"❌ Error testing duplicate detection: {str(e)}")

def test_scan_action_creation():
    """Test that scan actions are still being created (for tracking purposes)"""
    
    base_url = "http://localhost:8006"
    test_url = "https://bananarepublic.gap.com/browse/product.do?pid=704275052"
    
    print("\n🧪 Testing scan action creation (duplicates should still be saved)...")
    
    try:
        # Make a scan request
        scan_data = {
            "product_url": test_url,
            "user_id": 1,
            "fit_preference": "Standard"
        }
        
        response = requests.post(f"{base_url}/garment/size-recommendation", json=scan_data)
        
        if response.status_code == 200:
            print("✅ Scan request successful")
            result = response.json()
            print(f"   Recommended size: {result.get('recommended_size')}")
            print(f"   Confidence: {result.get('confidence')}")
            print("   Note: This scan action was saved to database for tracking")
        else:
            print(f"❌ Scan request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on port 8006.")
    except Exception as e:
        print(f"❌ Error testing scan action creation: {str(e)}")

if __name__ == "__main__":
    print("🔍 Testing Duplicate Detection System")
    print("=" * 50)
    print("📝 Note: Duplicates are saved to database for tracking but filtered in UI")
    print("=" * 50)
    
    test_scan_history_duplicate_detection()
    test_scan_action_creation()
    
    print("\n✅ Test completed!")
