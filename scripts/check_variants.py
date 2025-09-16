#!/usr/bin/env python3
import sys
sys.path.append('/Users/seandavey/projects/V10')

import psycopg2
from db_config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print('Checking cotton-cashmere products in database...')
print('='*60)

cur.execute("""
    SELECT product_code, base_product_code, variant_code, product_name, price, fit_options
    FROM jcrew_product_cache
    WHERE base_product_code = 'ME053' OR product_code LIKE 'ME053%'
    ORDER BY product_code
""")

results = cur.fetchall()
for r in results:
    code, base, variant, name, price, fits = r
    print(f'Code: {code}')
    print(f'  Base: {base}, Variant: {variant}')
    print(f'  Name: {name}')
    print(f'  Price: ${price:.2f}' if price else '  Price: N/A')
    print(f'  Fits: {fits if fits else "None (single fit)"}'.strip())
    print('-'*40)

print(f'\nTotal ME053 products: {len(results)}')

cur.close()
conn.close()

