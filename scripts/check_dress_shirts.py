#!/usr/bin/env python3
"""Check dress shirt results"""

import sys
sys.path.append('/Users/seandavey/projects/V10')

import psycopg2
from db_config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print("\n" + "="*70)
print("J.CREW DRESS SHIRTS CRAWL RESULTS")
print("="*70)

# Check the dress shirt products just crawled
cur.execute("""
    SELECT product_code, product_name, fit_options, price
    FROM jcrew_product_cache
    WHERE product_code IN ('CP682', 'BX291', 'CM238', 'CG334', 'BM492', 
                           'BM493', 'BN777', 'BN130', 'CD173', 'BU902')
    ORDER BY 
        CASE 
            WHEN fit_options IS NOT NULL THEN 0 
            ELSE 1 
        END,
        product_code
""")

products = cur.fetchall()

# Count fits vs no fits
with_fits = 0
without_fits = 0

print("\n🔸 DRESS SHIRTS WITH FIT OPTIONS:")
print("-" * 40)
for code, name, fits, price in products:
    if fits:
        with_fits += 1
        price_str = f'${price:.2f}' if price else 'N/A'
        print(f'{code}: {name[:40] if name else code:<40} Price: {price_str}')
        print(f'       Fits: {fits}')
        print()

print("\n🔹 SINGLE FIT DRESS SHIRTS (No Options):")
print("-" * 40)
for code, name, fits, price in products:
    if not fits:
        without_fits += 1
        price_str = f'${price:.2f}' if price else 'N/A'
        print(f'{code}: {name[:40] if name else code:<40} Price: {price_str}')

print("\n" + "="*70)
print("SUMMARY:")
print(f"  Total Dress Shirts Crawled: {len(products)}")
print(f"  With Fit Options: {with_fits}")
print(f"  Single Fit (No Options): {without_fits}")
print("="*70)

cur.close()
conn.close()