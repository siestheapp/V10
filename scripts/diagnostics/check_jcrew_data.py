#!/usr/bin/env python3
"""Check what J.Crew data is in the database"""

import psycopg2
import json
from datetime import datetime

DB_CONFIG = {
    'database': 'postgres',
    'user': 'postgres.lbilxlkchzpducggkrxx',
    'password': 'efvTower12',
    'host': 'aws-0-us-east-2.pooler.supabase.com',
    'port': '6543'
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("=" * 70)
    print("J.CREW DATABASE CHECK")
    print("=" * 70)
    
    # Total count
    cur.execute('SELECT COUNT(*), COUNT(DISTINCT product_code) FROM jcrew_product_cache')
    total, unique = cur.fetchone()
    print(f"\n📊 Total entries: {total}")
    print(f"📊 Unique product codes: {unique}")
    
    # Check by date
    cur.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM jcrew_product_cache 
        GROUP BY DATE(created_at) 
        ORDER BY date DESC
        LIMIT 10
    """)
    
    print("\n📅 Products by creation date:")
    for date, count in cur.fetchall():
        print(f"   {date}: {count} products")
    
    # Check your spot-checked products
    test_codes = ['BE996', 'BF792', 'CF783', 'BM493', 'CP682', 'MP235', 'BE986']
    cur.execute('''
        SELECT product_code, product_name, fit_options, created_at
        FROM jcrew_product_cache 
        WHERE product_code = ANY(%s)
        ORDER BY product_code
    ''', (test_codes,))
    
    results = cur.fetchall()
    print(f"\n🔍 Your spot-check products ({len(results)}/{len(test_codes)} found):")
    for code, name, fits, created in results:
        fit_str = f"{fits}" if fits else "None"
        name_str = name[:40] if name else "[No name]"
        print(f"   {code}: {name_str} | Fits: {fit_str}")
    
    missing = set(test_codes) - set([r[0] for r in results])
    if missing:
        print(f"\n❌ Missing from database: {', '.join(sorted(missing))}")
    
    # Check products WITH fit options
    cur.execute('''
        SELECT product_code, fit_options 
        FROM jcrew_product_cache 
        WHERE fit_options IS NOT NULL 
        AND array_length(fit_options, 1) > 0
        LIMIT 5
    ''')
    
    fit_products = cur.fetchall()
    if fit_products:
        print(f"\n✅ Products WITH fit options ({len(fit_products)} shown):")
        for code, fits in fit_products:
            print(f"   {code}: {fits}")
    else:
        print("\n⚠️ NO products have fit options stored!")
    
    # Check for the MP235/BE986 product that was causing issues
    cur.execute("""
        SELECT product_code, colors_available, cache_key, created_at
        FROM jcrew_product_cache 
        WHERE product_code IN ('MP235', 'BE986')
        OR cache_key LIKE '%MP235%'
        OR cache_key LIKE '%BE986%'
    """)
    
    problem_products = cur.fetchall()
    if problem_products:
        print(f"\n🔧 MP235/BE986 products ({len(problem_products)} found):")
        for code, colors, key, created in problem_products:
            color_str = str(colors)[:50] if colors else "None"
            print(f"   {code}: Colors: {color_str}... | Key: {key}")
    
    cur.close()
    conn.close()
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"❌ Database error: {e}")
