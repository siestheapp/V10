#!/usr/bin/env python3
"""
Check the current status of fit options in the J.Crew product database
"""

import sys
sys.path.append('/Users/seandavey/projects/V10')

import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DB_CONFIG
import json

def check_fit_status():
    """Check and report on the current state of fit options in the database"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("\n" + "="*70)
    print("J.CREW PRODUCT FIT OPTIONS STATUS REPORT")
    print("="*70 + "\n")
    
    # Overall statistics
    cur.execute("""
        SELECT 
            COUNT(*) as total_products,
            COUNT(CASE WHEN fit_options IS NOT NULL AND array_length(fit_options, 1) > 0 THEN 1 END) as has_fits,
            COUNT(CASE WHEN fit_options IS NULL THEN 1 END) as null_fits,
            COUNT(CASE WHEN fit_options = '{}' THEN 1 END) as empty_array_fits
        FROM jcrew_product_cache
    """)
    
    stats = cur.fetchone()
    
    print("📊 OVERALL STATISTICS:")
    print(f"   Total Products: {stats['total_products']}")
    print(f"   Products with Fit Options: {stats['has_fits']}")
    print(f"   Products with NULL Fits: {stats['null_fits']}")
    print(f"   Products with Empty Array: {stats['empty_array_fits']}")
    print()
    
    # Check for verified correct product
    cur.execute("""
        SELECT product_code, product_name, fit_options
        FROM jcrew_product_cache
        WHERE product_code = 'BE996'
    """)
    
    verified = cur.fetchone()
    if verified:
        print("✅ VERIFIED PRODUCT (BE996):")
        print(f"   Name: {verified['product_name']}")
        print(f"   Fit Options: {verified['fit_options']}")
        print(f"   Expected: ['Classic', 'Slim', 'Slim Untucked', 'Tall', 'Relaxed']")
        print()
    
    # Sample of products with fits
    cur.execute("""
        SELECT product_code, product_name, fit_options, array_length(fit_options, 1) as num_fits
        FROM jcrew_product_cache
        WHERE fit_options IS NOT NULL AND array_length(fit_options, 1) > 0
        ORDER BY array_length(fit_options, 1) DESC
        LIMIT 10
    """)
    
    products_with_fits = cur.fetchall()
    
    if products_with_fits:
        print("📦 PRODUCTS WITH FIT OPTIONS (Top 10):")
        for p in products_with_fits:
            print(f"   {p['product_code']}: {p['product_name'][:40]}")
            print(f"      Fits ({p['num_fits']}): {p['fit_options']}")
        print()
    
    # Sample of products without fits
    cur.execute("""
        SELECT product_code, product_name, product_url
        FROM jcrew_product_cache
        WHERE fit_options IS NULL
        ORDER BY product_code
        LIMIT 10
    """)
    
    products_without_fits = cur.fetchall()
    
    if products_without_fits:
        print("⚠️ PRODUCTS WITHOUT FIT OPTIONS (First 10):")
        for p in products_without_fits:
            print(f"   {p['product_code']}: {p['product_name'][:40]}")
            if p['product_url']:
                print(f"      URL: {p['product_url'][:60]}...")
        print()
    
    # Check for suspicious data (too many fits)
    cur.execute("""
        SELECT product_code, product_name, fit_options, array_length(fit_options, 1) as num_fits
        FROM jcrew_product_cache
        WHERE array_length(fit_options, 1) > 5
        ORDER BY array_length(fit_options, 1) DESC
        LIMIT 5
    """)
    
    suspicious = cur.fetchall()
    
    if suspicious:
        print("🚨 POTENTIALLY INCORRECT DATA (>5 fits):")
        for p in suspicious:
            print(f"   {p['product_code']}: {p['product_name'][:40]}")
            print(f"      Fits ({p['num_fits']}): {p['fit_options']}")
        print()
    
    # Distribution of fit counts
    cur.execute("""
        SELECT 
            array_length(fit_options, 1) as num_fits,
            COUNT(*) as product_count
        FROM jcrew_product_cache
        WHERE fit_options IS NOT NULL
        GROUP BY array_length(fit_options, 1)
        ORDER BY num_fits
    """)
    
    distribution = cur.fetchall()
    
    if distribution:
        print("📈 FIT OPTIONS DISTRIBUTION:")
        for d in distribution:
            print(f"   {d['num_fits']} fits: {d['product_count']} products")
        print()
    
    print("="*70)
    print("RECOMMENDED NEXT STEPS:")
    print("1. Run the crawler with test mode first: python jcrew_fit_crawler.py --test")
    print("2. Process a small batch: python jcrew_fit_crawler.py --limit 10")
    print("3. Process all remaining: python jcrew_fit_crawler.py --headless")
    print("="*70 + "\n")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_fit_status()

