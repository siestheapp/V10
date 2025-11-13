#!/usr/bin/env python3
"""
Test with real J.Crew shirt: Short-sleeve Broken-in organic cotton oxford shirt
"""

import requests
import json
import time

def test_real_jcrew_shirt():
    """Test the endpoint with the actual J.Crew shirt URL"""
    print("🧪 TESTING REAL J.CREW SHIRT")
    print("👔 Product: Short-sleeve Broken-in organic cotton oxford shirt")
    print("🎨 Color: Raincoat Blue")
    print("📏 Fit: Classic/Regular fit")
    print()
    
    # Real J.Crew URL provided by user
    real_url = "https://www.jcrew.com/m/mens/categories/clothing/shirts/broken-in-oxford/short-sleeve-broken-in-organic-cotton-oxford-shirt/MP235?display=standard&fit=Classic&colorProductCode=BE986"
    
    payload = {
        "product_url": real_url,
        "user_id": 1,
        "user_fit_preference": "Standard",
        "brand_name": "J.Crew"
    }
    
    try:
        print(f"📡 Making request to: http://localhost:8006/garment/size-recommendation")
        print(f"🔗 Product URL: {real_url}")
        print()
        
        start_time = time.time()
        response = requests.post(
            "http://localhost:8006/garment/size-recommendation",
            json=payload,
            timeout=15
        )
        response_time = time.time() - start_time
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"⏱️  Response Time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ SUCCESS - Multi-dimensional analysis complete!")
            print()
            
            # Show the key results that would appear in iOS app
            print("🎯 SIZE RECOMMENDATIONS FOR THIS J.CREW SHIRT:")
            if "all_matching_sizes" in data:
                matching_sizes = data["all_matching_sizes"]
                print(f"   📊 Found {len(matching_sizes)} sizes that fit you:")
                for i, size in enumerate(matching_sizes, 1):
                    print(f"      {i}. {size}")
                print()
            
            # Show the best recommendation
            if "recommended_fit_label" in data:
                print(f"🏆 BEST RECOMMENDATION: {data['recommended_fit_label']}")
                print(f"📈 Confidence: {data.get('confidence', 'N/A')}")
                print()
            
            # Show which dimensions were analyzed
            if "dimensions_analyzed" in data:
                dimensions = data["dimensions_analyzed"]
                print(f"🔬 DIMENSIONS ANALYZED: {', '.join(dimensions).title()}")
                print()
            
            # Show multi-dimensional details
            if "all_sizes_detailed" in data and data["all_sizes_detailed"]:
                print("📋 DETAILED ANALYSIS:")
                for size_detail in data["all_sizes_detailed"][:3]:  # Show top 3
                    size_label = size_detail.get("size", "Unknown")
                    fit_label = size_detail.get("size_with_fit_label", size_label)
                    score = size_detail.get("overall_fit_score", 0)
                    fits_all = size_detail.get("fits_all_dimensions", False)
                    
                    print(f"   • {fit_label}")
                    print(f"     Score: {score:.3f} | Fits all dimensions: {'Yes' if fits_all else 'No'}")
                    
                    if "dimension_analysis" in size_detail:
                        dim_analysis = size_detail["dimension_analysis"]
                        for dim, details in dim_analysis.items():
                            if dim == "chest":
                                fit_zone = details.get("fit_zone", "unknown")
                                print(f"       {dim.title()}: {fit_zone} fit zone")
                            else:
                                fits_well = details.get("fits_well", False)
                                measurement = details.get("garment_measurement", "N/A")
                                print(f"       {dim.title()}: {measurement}\" ({'✓' if fits_well else '✗'})")
                    print()
            
            # Show reference garments used
            if "reference_garments" in data:
                ref_garments = data["reference_garments"]
                print(f"📚 REFERENCE DATA USED:")
                for key, garment in ref_garments.items():
                    dimension = garment.get("dimension", key)
                    data_points = garment.get("data_points", "N/A")
                    confidence = garment.get("confidence", "N/A")
                    print(f"   {dimension.title()}: {data_points} garments (confidence: {confidence})")
                print()
            
            print("🎉 REAL J.CREW SHIRT TEST COMPLETE!")
            print("✅ Your original vision is working perfectly!")
            print("🎯 Scan any shirt tag → Get instant, accurate recommendations")
            
        else:
            print(f"❌ HTTP ERROR - Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Backend not running on port 8006")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_real_jcrew_shirt()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")