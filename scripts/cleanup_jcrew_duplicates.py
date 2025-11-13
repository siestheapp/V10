#!/usr/bin/env python3
"""
Clean up J.Crew duplicate products by consolidating variants
"""

import psycopg2
import sys
import os
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import DB_CONFIG

def cleanup_jcrew_duplicates():
    """Consolidate duplicate J.Crew products"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("🧹 Cleaning up J.Crew duplicate products...")
    print("=" * 70)
    
    try:
        # First, identify the duplicates we created today
        cur.execute("""
            SELECT base_name, array_agg(product_code ORDER BY product_code), 
                   array_agg(id ORDER BY product_code),
                   COUNT(*) as count
            FROM product_master 
            WHERE brand_id = 4
            AND DATE(created_at) = '2025-09-18'
            GROUP BY base_name
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """)
        
        duplicates = cur.fetchall()
        
        if not duplicates:
            print("✅ No duplicates found from today's ingestion")
            return
        
        print(f"Found {len(duplicates)} sets of duplicates to consolidate:\n")
        
        consolidation_log = []
        
        for name, codes, ids, count in duplicates:
            print(f"📦 '{name[:50]}...'")
            print(f"   Codes: {codes}")
            print(f"   IDs: {ids}")
            
            # Strategy: Keep the first one as master, convert others to variants
            master_id = ids[0]
            master_code = codes[0]
            variant_ids = ids[1:]
            variant_codes = codes[1:]
            
            print(f"   → Keeping {master_code} (ID: {master_id}) as master")
            print(f"   → Converting {variant_codes} to variants")
            
            # Get existing variants for the master
            cur.execute("""
                SELECT id, color_name, fit_option 
                FROM product_variants 
                WHERE product_master_id = %s
            """, (master_id,))
            existing_variants = cur.fetchall()
            
            # For each duplicate, move its variants to the master
            for variant_id, variant_code in zip(variant_ids, variant_codes):
                # Get variants from the duplicate
                cur.execute("""
                    SELECT color_name, fit_option 
                    FROM product_variants 
                    WHERE product_master_id = %s
                """, (variant_id,))
                duplicate_variants = cur.fetchall()
                
                # Add them to master (if not already there)
                for color, fit in duplicate_variants:
                    # Check if this variant already exists on master
                    cur.execute("""
                        SELECT id FROM product_variants
                        WHERE product_master_id = %s 
                        AND color_name = %s 
                        AND fit_option = %s
                    """, (master_id, color, fit))
                    
                    if not cur.fetchone():
                        # Add the variant to master
                        cur.execute("""
                            INSERT INTO product_variants 
                            (product_master_id, color_name, fit_option, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (master_id, color or variant_code, fit, datetime.now(), datetime.now()))
                        print(f"      + Added variant: {color or variant_code} / {fit}")
                
                # Also create a variant for the duplicate product code itself
                cur.execute("""
                    SELECT id FROM product_variants
                    WHERE product_master_id = %s 
                    AND color_name = %s
                """, (master_id, variant_code))
                
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO product_variants 
                        (product_master_id, color_name, fit_option, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (master_id, variant_code, 'Classic', datetime.now(), datetime.now()))
                    print(f"      + Created variant for code: {variant_code}")
                
                # Delete the duplicate product and its variants
                cur.execute("""
                    DELETE FROM product_variants 
                    WHERE product_master_id = %s
                """, (variant_id,))
                
                cur.execute("""
                    DELETE FROM product_master 
                    WHERE id = %s
                """, (variant_id,))
                
                print(f"      ✓ Deleted duplicate product: {variant_code}")
            
            consolidation_log.append({
                'product': name,
                'master_kept': {'id': master_id, 'code': master_code},
                'variants_consolidated': list(zip(variant_ids, variant_codes))
            })
            
            print()
        
        # Commit the changes
        conn.commit()
        
        # Save the log
        with open('jcrew_consolidation_log.json', 'w') as f:
            json.dump(consolidation_log, f, indent=2, default=str)
        
        print("=" * 70)
        print("✅ Consolidation complete!")
        
        # Show final state
        cur.execute("""
            SELECT COUNT(DISTINCT pm.id) as products,
                   COUNT(DISTINCT pv.id) as variants
            FROM product_master pm
            LEFT JOIN product_variants pv ON pm.id = pv.product_master_id
            WHERE pm.brand_id = 4
        """)
        
        products, variants = cur.fetchone()
        print(f"\n📊 Final J.Crew database state:")
        print(f"   Products: {products}")
        print(f"   Variants: {variants}")
        
        # Update the existing codes file
        cur.execute("""
            SELECT DISTINCT product_code 
            FROM product_master 
            WHERE brand_id = 4
            ORDER BY product_code
        """)
        
        all_codes = [row[0] for row in cur.fetchall()]
        
        with open('existing_jcrew_codes.json', 'w') as f:
            json.dump({
                'brand_id': 4,
                'brand': 'J.Crew',
                'count': len(all_codes),
                'codes': all_codes,
                'last_cleanup': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n💾 Updated existing_jcrew_codes.json with {len(all_codes)} products")
        print("💾 Saved consolidation log to jcrew_consolidation_log.json")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during cleanup: {str(e)}")
        raise
    finally:
        conn.close()


def verify_cleanup():
    """Verify no more duplicates exist"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("\n🔍 Verifying cleanup...")
    print("-" * 40)
    
    # Check for any remaining duplicates
    cur.execute("""
        SELECT base_name, COUNT(*) as count
        FROM product_master 
        WHERE brand_id = 4
        GROUP BY base_name
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 5
    """)
    
    remaining_dupes = cur.fetchall()
    
    if remaining_dupes:
        print("⚠️ Some potential duplicates remain:")
        for name, count in remaining_dupes:
            print(f"   {name[:50]}: {count} entries")
    else:
        print("✅ No duplicate product names found!")
    
    # Show sample of consolidated products with variants
    print("\n📦 Sample consolidated products with variants:")
    cur.execute("""
        SELECT pm.product_code, pm.base_name, 
               COUNT(DISTINCT pv.id) as variant_count,
               array_agg(DISTINCT pv.color_name) as colors
        FROM product_master pm
        LEFT JOIN product_variants pv ON pm.id = pv.product_master_id
        WHERE pm.brand_id = 4
        AND pm.base_name LIKE '%denim%' OR pm.base_name LIKE '%chambray%'
        GROUP BY pm.product_code, pm.base_name
        HAVING COUNT(DISTINCT pv.id) > 1
        ORDER BY variant_count DESC
        LIMIT 5
    """)
    
    for code, name, variant_count, colors in cur.fetchall():
        print(f"\n   {code}: {name[:40]}...")
        print(f"      {variant_count} variants: {colors[:5]}")
    
    conn.close()


if __name__ == "__main__":
    cleanup_jcrew_duplicates()
    verify_cleanup()


