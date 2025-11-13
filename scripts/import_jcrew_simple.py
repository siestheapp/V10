#!/usr/bin/env python3
"""
Simple, reliable import script for J.Crew broken-in oxford products
"""

import json
import sys
import os
from datetime import datetime

def main():
    print("🚀 Starting Simple J.Crew Import")
    print("=" * 40)
    
    # Find the JSON file
    json_file = "jcrew_broken_in_oxford_complete_20250915_120745.json"
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return
    
    # Load data
    try:
        with open(json_file, 'r') as f:
            products = json.load(f)
        print(f"✅ Loaded {len(products)} products")
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return
    
    # Show summary
    print(f"\n📊 Product Summary:")
    unique_codes = set()
    for product in products:
        code = product.get('code', 'unknown')
        name = product.get('name', 'unknown')
        colors = product.get('colors', [])
        unique_codes.add(code)
        print(f"  • {code}: {name} ({len(colors)} colors)")
    
    print(f"\n🎯 Found {len(unique_codes)} unique product codes:")
    for code in sorted(unique_codes):
        print(f"  - {code}")
    
    print(f"\n✅ Import data ready for database insertion")
    print(f"📁 Data file: {json_file}")
    print(f"📊 Total products: {len(products)}")
    print(f"🔢 Unique codes: {len(unique_codes)}")

if __name__ == "__main__":
    main()

