#!/usr/bin/env python3
"""Check results from the full crawler"""

import sys
sys.path.append('/Users/seandavey/projects/V10')

import psycopg2
from db_config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Check the newly crawled products
print("\n" + "="*70)
print("NEWLY CRAWLED PRODUCTS")
print("="*70)

cur.execute("""
    SELECT product_code, product_name, fit_options, price
    FROM jcrew_product_cache
    WHERE product_code IN ('CM389', 'CF783', 'CN406', 'BE996', 'BX291')
    ORDER BY product_code
""")

products = cur.fetchall()
for code, name, fits, price in products:
    fit_str = f'{fits}' if fits else 'None (single fit)'
    price_str = f'${price:.2f}' if price else 'N/A'
    print(f'{code}: {name[:40]:<40} Price: {price_str}')
    print(f'       Fits: {fit_str}')
    print()

cur.close()
conn.close()

