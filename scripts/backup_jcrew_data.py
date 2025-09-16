#!/usr/bin/env python3
"""Create a backup of current J.Crew data before making changes"""

import psycopg2
from datetime import datetime
import json
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

def create_backup():
    """Create a backup table and export current state"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_table = f'jcrew_backup_{timestamp}'
    
    print("=" * 80)
    print("CREATING J.CREW DATA BACKUP")
    print("=" * 80)
    
    try:
        # Get current statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE fit_options IS NOT NULL AND array_length(fit_options, 1) > 0) as with_fits,
                COUNT(*) FILTER (WHERE fit_options IS NULL OR array_length(fit_options, 1) = 0) as without_fits
            FROM jcrew_product_cache
        """)
        
        total, with_fits, without_fits = cur.fetchone()
        print(f"\n📊 Current State:")
        print(f"   Total products: {total}")
        print(f"   With fit options: {with_fits}")
        print(f"   Without fit options: {without_fits}")
        
        # Create backup table
        print(f"\n🔄 Creating backup table: {backup_table}")
        cur.execute(f"""
            CREATE TABLE {backup_table} AS 
            SELECT * FROM jcrew_product_cache
        """)
        
        # Verify backup
        cur.execute(f"SELECT COUNT(*) FROM {backup_table}")
        backup_count = cur.fetchone()[0]
        
        if backup_count == total:
            print(f"   ✅ Backup successful: {backup_count} records")
        else:
            print(f"   ⚠️ Backup mismatch: {backup_count} vs {total}")
            
        # Add comment with metadata
        cur.execute(f"""
            COMMENT ON TABLE {backup_table} IS %s
        """, (json.dumps({
            'created_at': timestamp,
            'total_products': total,
            'with_fits': with_fits,
            'without_fits': without_fits,
            'purpose': 'Backup before implementing data protection framework'
        }),))
        
        # Export critical products for verification
        cur.execute("""
            SELECT product_code, product_name, fit_options
            FROM jcrew_product_cache
            WHERE product_code IN ('BE996', 'ME681', 'BM492', 'MP235')
            ORDER BY product_code
        """)
        
        critical_products = cur.fetchall()
        
        print(f"\n🔒 Critical Products Snapshot:")
        for code, name, fits in critical_products:
            print(f"   {code}: {fits}")
        
        # Save to JSON file as well
        cur.execute("""
            SELECT product_code, product_name, product_url, fit_options, 
                   colors_available, sizes_available, updated_at::text
            FROM jcrew_product_cache
            ORDER BY product_code
        """)
        
        all_products = []
        for row in cur.fetchall():
            all_products.append({
                'product_code': row[0],
                'product_name': row[1],
                'product_url': row[2],
                'fit_options': row[3],
                'colors_available': row[4],
                'sizes_available': row[5],
                'updated_at': row[6]
            })
        
        backup_filename = f'jcrew_backup_{timestamp}.json'
        with open(backup_filename, 'w') as f:
            json.dump(all_products, f, indent=2)
        
        print(f"\n📁 JSON backup saved to: {backup_filename}")
        
        print(f"\n✅ BACKUP COMPLETE")
        print(f"   Database table: {backup_table}")
        print(f"   JSON file: {backup_filename}")
        
        return backup_table
        
    except Exception as e:
        print(f"\n❌ Backup failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_backup()
