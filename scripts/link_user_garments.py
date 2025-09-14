#!/usr/bin/env python3
"""
Link user garments to product master records
This enables AI to use rich product data when analyzing user feedback
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from db_config import DB_CONFIG

def link_garments_to_masters():
    """Link existing user garments to product masters"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("🔗 LINKING USER GARMENTS TO PRODUCT MASTERS")
    print("=" * 60)
    
    # First, check current state
    cur.execute("""
        SELECT COUNT(*) as total,
               COUNT(product_master_id) as linked
        FROM user_garments
        WHERE brand_id = 4
    """)
    
    total, linked = cur.fetchone()
    print(f"\nCurrent J.Crew garments: {total}")
    print(f"Already linked: {linked}")
    
    if total > linked:
        # Link based on product URL matching
        print(f"\nLinking {total - linked} unlinked garments...")
        
        cur.execute("""
            UPDATE user_garments ug
            SET product_master_id = pm.id,
                product_variant_id = pv.id
            FROM product_master pm
            LEFT JOIN product_variants pv ON pm.id = pv.product_master_id
            WHERE ug.brand_id = pm.brand_id
            AND ug.product_master_id IS NULL
            AND (
                -- Match by product code if available
                (ug.product_code IS NOT NULL AND ug.product_code = pm.product_code)
                OR
                -- Match by product name similarity
                (ug.product_name ILIKE '%' || pm.base_name || '%')
            )
            AND ug.brand_id = 4
        """)
        
        updated = cur.rowcount
        conn.commit()
        
        print(f"✅ Linked {updated} garments to product masters!")
    
    # Show what's now possible
    print("\n🤖 AI INSIGHTS NOW AVAILABLE FOR USER GARMENTS:")
    print("-" * 60)
    
    cur.execute("""
        SELECT 
            ug.product_name,
            pm.materials->>'primary_fabric' as fabric,
            pm.care_instructions[1] as care,
            ugf.feedback->>'overall_rating' as rating
        FROM user_garments ug
        JOIN product_master pm ON ug.product_master_id = pm.id
        LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
        WHERE ug.user_id = 1
        AND ug.product_master_id IS NOT NULL
        LIMIT 3
    """)
    
    results = cur.fetchall()
    if results:
        print("\nExample user garments with rich data:")
        for name, fabric, care, rating in results:
            print(f"\n• {name[:40]}")
            print(f"  Fabric: {fabric or 'Mixed'}")
            print(f"  Care: {care or 'Not specified'}")
            if rating:
                print(f"  User Rating: {rating}/5")
    
    # Show preference patterns we can detect
    print("\n📊 PREFERENCE PATTERNS AI CAN NOW DETECT:")
    print("-" * 60)
    
    cur.execute("""
        SELECT 
            pm.materials->>'primary_fabric' as fabric,
            COUNT(*) as owned_count,
            AVG(CAST(ugf.feedback->>'overall_rating' AS FLOAT)) as avg_rating
        FROM user_garments ug
        JOIN product_master pm ON ug.product_master_id = pm.id
        LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
        WHERE ug.user_id = 1
        AND pm.materials IS NOT NULL
        GROUP BY fabric
        HAVING COUNT(*) > 0
    """)
    
    fabric_prefs = cur.fetchall()
    if fabric_prefs:
        print("\nFabric preferences based on ownership:")
        for fabric, count, rating in fabric_prefs:
            if fabric:
                print(f"  • {fabric}: {count} items owned")
                if rating:
                    print(f"    Average rating: {rating:.1f}/5")
    
    # Show care preference patterns
    cur.execute("""
        SELECT 
            care_instructions[1] as primary_care,
            COUNT(*) as products
        FROM user_garments ug
        JOIN product_master pm ON ug.product_master_id = pm.id
        WHERE ug.user_id = 1
        AND ARRAY_LENGTH(pm.care_instructions, 1) > 0
        GROUP BY primary_care
        ORDER BY products DESC
        LIMIT 3
    """)
    
    care_prefs = cur.fetchall()
    if care_prefs:
        print("\nCare requirements pattern:")
        for care, count in care_prefs:
            print(f"  • {care}: {count} items")
    
    # Show the power of linking
    print("\n✨ WHAT THIS ENABLES:")
    print("=" * 60)
    print("• AI learns user's fabric preferences from actual purchases")
    print("• Can filter products by care requirements user accepts")
    print("• Predicts fit based on feedback on similar constructions")
    print("• Recommends products with features user rates highly")
    print("• Avoids suggesting items with dealbreaker attributes")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    link_garments_to_masters()
