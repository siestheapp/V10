#!/usr/bin/env python3
"""
Targeted cleanup of J.Crew data quality issues
"""

import psycopg2
import sys
import os
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_config import DB_CONFIG

def targeted_cleanup():
    """Clean up specific data quality issues in J.Crew products"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("🎯 Targeted J.Crew Cleanup")
    print("=" * 70)
    
    cleanup_log = {
        'deleted_empty_names': [],
        'consolidated_ludlow': {},
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Step 1: Delete products with empty names
        print("\n1️⃣ Removing products with empty names...")
        cur.execute("""
            SELECT id, product_code 
            FROM product_master 
            WHERE brand_id = 4 
            AND (base_name = '' OR base_name IS NULL)
        """)
        
        empty_products = cur.fetchall()
        for id, code in empty_products:
            # First delete any variants
            cur.execute("DELETE FROM product_variants WHERE product_master_id = %s", (id,))
            # Then delete the product
            cur.execute("DELETE FROM product_master WHERE id = %s", (id,))
            cleanup_log['deleted_empty_names'].append({'id': id, 'code': code})
            print(f"   ✓ Deleted {code} (ID: {id})")
        
        print(f"   Removed {len(empty_products)} products with empty names")
        
        # Step 2: Consolidate Ludlow shirts
        print("\n2️⃣ Consolidating Ludlow dress shirts...")
        
        # Get the Ludlow shirts
        cur.execute("""
            SELECT id, product_code, base_name 
            FROM product_master 
            WHERE brand_id = 4 
            AND product_code IN ('AI873', 'AI874')
            ORDER BY product_code
        """)
        
        ludlow_shirts = cur.fetchall()
        
        if len(ludlow_shirts) == 2:
            master = ludlow_shirts[0]  # AI873
            variant = ludlow_shirts[1]  # AI874
            
            print(f"   Master: {master[1]} (ID: {master[0]})")
            print(f"   Converting to variant: {variant[1]} (ID: {variant[0]})")
            
            # Check existing variants for the variant product
            cur.execute("""
                SELECT color_name, fit_option 
                FROM product_variants 
                WHERE product_master_id = %s
            """, (variant[0],))
            
            variant_data = cur.fetchall()
            
            # Move variants to master
            for color, fit in variant_data:
                # Check if this variant already exists on master
                cur.execute("""
                    SELECT id FROM product_variants
                    WHERE product_master_id = %s 
                    AND color_name = %s 
                    AND (fit_option = %s OR (fit_option IS NULL AND %s IS NULL))
                """, (master[0], color, fit, fit))
                
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO product_variants 
                        (product_master_id, color_name, fit_option, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (master[0], color, fit, datetime.now(), datetime.now()))
                    print(f"      + Moved variant: {color} / {fit}")
            
            # Create a variant for the AI874 code itself
            cur.execute("""
                INSERT INTO product_variants 
                (product_master_id, color_name, fit_option, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (master[0], variant[1], 'Slim', datetime.now(), datetime.now()))
            print(f"      + Created variant for code: {variant[1]}")
            
            # Delete the variant product
            cur.execute("DELETE FROM product_variants WHERE product_master_id = %s", (variant[0],))
            cur.execute("DELETE FROM product_master WHERE id = %s", (variant[0],))
            
            cleanup_log['consolidated_ludlow'] = {
                'master': {'id': master[0], 'code': master[1]},
                'consolidated': {'id': variant[0], 'code': variant[1]}
            }
            
            print(f"   ✓ Consolidated Ludlow shirts")
        else:
            print(f"   ⚠️ Found {len(ludlow_shirts)} Ludlow shirts, expected 2")
        
        # Step 3: Verify Secret Wash shirts remain separate
        print("\n3️⃣ Verifying Secret Wash products...")
        cur.execute("""
            SELECT product_code, base_name 
            FROM product_master 
            WHERE brand_id = 4 
            AND base_name LIKE 'Secret Wash%'
            ORDER BY product_code
        """)
        
        secret_wash = cur.fetchall()
        print(f"   ✓ Keeping {len(secret_wash)} Secret Wash products separate:")
        for code, name in secret_wash:
            print(f"      • {code}: {name[:50]}...")
        
        # Commit changes
        conn.commit()
        
        # Save cleanup log
        with open('targeted_cleanup_log.json', 'w') as f:
            json.dump(cleanup_log, f, indent=2, default=str)
        
        # Final statistics
        print("\n" + "=" * 70)
        print("✅ Cleanup Complete!")
        
        cur.execute("""
            SELECT COUNT(*) FROM product_master WHERE brand_id = 4
        """)
        final_count = cur.fetchone()[0]
        
        print(f"\n📊 Final Statistics:")
        print(f"   Products before: 57")
        print(f"   Products after:  {final_count}")
        print(f"   Removed: {len(empty_products)} empty-name products")
        print(f"   Consolidated: 1 Ludlow duplicate")
        print(f"   Preserved: {len(secret_wash)} Secret Wash variations")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        conn.close()


def update_deduplicator_rules():
    """Add new rules to the deduplicator based on what we learned"""
    
    rules = {
        'consecutive_codes': {
            'description': 'Consecutive product codes (AI873/AI874) likely indicate color variants',
            'action': 'add_variant',
            'example': 'AI873 and AI874 are variants of the same Ludlow shirt'
        },
        'empty_names': {
            'description': 'Products with empty names should be rejected during scraping',
            'action': 'reject',
            'example': 'Skip any product without a base_name'
        },
        'style_variations': {
            'description': 'Similar names with style differences are separate products',
            'action': 'create_master',
            'example': 'Secret Wash shirt vs Secret Wash shirt in stripe'
        },
        'master_codes': {
            'description': 'MP### codes indicate master products',
            'action': 'create_master_or_skip',
            'example': 'MP832 is a master product code'
        }
    }
    
    with open('deduplicator_rules.json', 'w') as f:
        json.dump(rules, f, indent=2)
    
    print("\n📝 Updated deduplicator rules saved to deduplicator_rules.json")
    return rules


if __name__ == "__main__":
    targeted_cleanup()
    update_deduplicator_rules()


