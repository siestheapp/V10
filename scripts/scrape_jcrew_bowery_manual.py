#!/usr/bin/env python3
"""
Manual entry for J.Crew Bowery dress shirts based on the page content
"""

import json
from datetime import datetime

# Based on the Bowery Performance Stretch dress shirts page
bowery_products = [
    {
        'product_code': 'BE996',
        'product_name': 'Bowery performance stretch dress shirt with spread collar',
        'colors': ['White', 'Fairweather Blue', 'Rian White Pink', 'Port Stripe Blue White', 'Ed Check Orange White'],
        'fits': ['Classic', 'Slim', 'Slim Untucked'],
        'price': 98.00,
        'category': 'Dress Shirts',
        'subcategory': 'Bowery',
        'brand_name': 'J.Crew',
        'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/bowery/BE996',
        'sizes_available': ['14.5/32', '14.5/33', '15/32', '15/33', '15/34', '15.5/32', '15.5/33', '15.5/34', '15.5/35', 
                           '16/32', '16/33', '16/34', '16/35', '16.5/33', '16.5/34', '16.5/35', '17/34', '17/35', '17/36', '18/35', '18/36']
    },
    {
        'product_code': 'AW770',
        'product_name': 'Bowery wrinkle-free stretch cotton dress shirt with spread collar',
        'colors': ['White', 'Fairweather Blue'],
        'fits': ['Classic', 'Slim'],
        'price': 89.50,
        'category': 'Dress Shirts',
        'subcategory': 'Bowery',
        'brand_name': 'J.Crew',
        'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/bowery/AW770',
        'sizes_available': ['14.5/32', '14.5/33', '15/32', '15/33', '15/34', '15.5/32', '15.5/33', '15.5/34', '15.5/35', 
                           '16/32', '16/33', '16/34', '16/35', '16.5/33', '16.5/34', '16.5/35', '17/34', '17/35']
    },
    {
        'product_code': 'K6873',
        'product_name': 'Bowery wrinkle-free dress shirt with button-down collar',
        'colors': ['White', 'Fairweather Blue'],
        'fits': ['Classic', 'Slim'],
        'price': 89.50,
        'category': 'Dress Shirts',
        'subcategory': 'Bowery',
        'brand_name': 'J.Crew',
        'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/bowery/K6873',
        'sizes_available': ['14.5/32', '14.5/33', '15/32', '15/33', '15/34', '15.5/32', '15.5/33', '15.5/34', '15.5/35', 
                           '16/32', '16/33', '16/34', '16/35', '16.5/33', '16.5/34', '16.5/35', '17/34', '17/35']
    },
    {
        'product_code': 'BN994',
        'product_name': 'Bowery performance stretch dress shirt with button-down collar',
        'colors': ['White', 'Fairweather Blue'],
        'fits': ['Classic', 'Slim', 'Slim Untucked'],
        'price': 98.00,
        'category': 'Dress Shirts',
        'subcategory': 'Bowery',
        'brand_name': 'J.Crew',
        'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/bowery/BN994',
        'sizes_available': ['14.5/32', '14.5/33', '15/32', '15/33', '15/34', '15.5/32', '15.5/33', '15.5/34', '15.5/35', 
                           '16/32', '16/33', '16/34', '16/35', '16.5/33', '16.5/34', '16.5/35', '17/34', '17/35', '17/36', '18/35', '18/36']
    }
]

# Save to JSON
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'jcrew_bowery_shirts_{timestamp}.json'

with open(filename, 'w') as f:
    json.dump(bowery_products, f, indent=2)

print(f"✅ Created {filename} with {len(bowery_products)} Bowery dress shirts")
print(f"\n📊 Summary:")
for product in bowery_products:
    print(f"  - {product['product_code']}: {product['product_name']}")
    print(f"    Colors: {', '.join(product['colors'])}")
    print(f"    Fits: {', '.join(product['fits'])}")
    print(f"    Price: ${product['price']}")
    print()




