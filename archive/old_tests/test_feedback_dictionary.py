#!/usr/bin/env python3
"""
Quick test to verify the "feedback" field is now a dictionary
"""

import requests
import json

def test_feedback_dictionary():
    """Test that the feedback field is now a dictionary, not string"""
    print("🧪 TESTING FEEDBACK AS DICTIONARY\n")
    
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
                print("🔍 Reference Garments Feedback Structure:")
                for key, garment in data["reference_garments"].items():
                    print(f"\n   {key}:")
                    
                    if "feedback" in garment:
                        feedback = garment["feedback"]
                        data_type = type(feedback).__name__
                        print(f"      feedback: {feedback} ({data_type})")
                        
                        if data_type == 'dict':
                            print(f"        ✅ Dictionary type as expected by iOS")
                            # Show the dictionary contents
                            for fb_key, fb_value in feedback.items():
                                print(f"          {fb_key}: {fb_value}")
                        else:
                            print(f"        ❌ Not dictionary! iOS will fail to decode")
                    else:
                        print(f"      ❌ No feedback field")
                
                print(f"\n✅ Check if all feedback values are dictionaries!")
            else:
                print("❌ No reference_garments found")
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_feedback_dictionary()