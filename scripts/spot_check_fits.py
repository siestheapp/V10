#!/usr/bin/env python3
"""Spot check fit options - pull URLs and fits for verification"""

import sys
sys.path.append('/Users/seandavey/projects/V10')

import psycopg2
from db_config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print("\n" + "="*80)
print("SPOT CHECK: J.CREW FIT OPTIONS")
print("="*80)

# Get 3 casual shirts (from recent crawls)
print("\n🔵 CASUAL SHIRTS (3):")
print("-" * 80)

cur.execute("""
    SELECT product_code, product_name, product_url, fit_options
    FROM jcrew_product_cache
    WHERE product_url IS NOT NULL
    AND product_code IN ('BE996', 'CF783', 'BF792')
    ORDER BY product_code
""")

casual_shirts = cur.fetchall()
for code, name, url, fits in casual_shirts:
    print(f"\n{code}: {name if name else code}")
    print(f"URL: {url}")
    print(f"Fit Options in DB: {fits if fits else 'None (single fit)'}")
    print("-" * 40)

# Get 2 dress shirts
print("\n🔷 DRESS SHIRTS (2):")
print("-" * 80)

cur.execute("""
    SELECT product_code, product_name, product_url, fit_options
    FROM jcrew_product_cache
    WHERE product_url IS NOT NULL
    AND product_code IN ('CP682', 'BM493')
    ORDER BY product_code
""")

dress_shirts = cur.fetchall()
for code, name, url, fits in dress_shirts:
    print(f"\n{code}: {name if name else code}")
    print(f"URL: {url}")
    print(f"Fit Options in DB: {fits if fits else 'None (single fit)'}")
    print("-" * 40)

print("\n" + "="*80)
print("🔍 PLEASE VERIFY:")
print("Visit each URL above and check if the fit options match what's in the database")
print("="*80 + "\n")

cur.close()
conn.close()

