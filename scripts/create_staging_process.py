#!/usr/bin/env python3
"""Create staging table and safe import process for J.Crew data"""

import psycopg2
import json
from datetime import datetime
import sys
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

class SafeJCrewImporter:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()
        self.staging_table = f"jcrew_staging_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_staging_table(self):
        """Create a staging table for safe imports"""
        print(f"\n📦 Creating staging table: {self.staging_table}")
        
        # Create staging table with same structure as main table
        self.cur.execute(f"""
            CREATE TABLE {self.staging_table} AS 
            SELECT * FROM jcrew_product_cache WHERE 1=0
        """)
        
        print(f"   ✅ Staging table created")
        return self.staging_table
    
    def import_to_staging(self, products):
        """Import products to staging table for validation"""
        print(f"\n📥 Importing {len(products)} products to staging...")
        
        success_count = 0
        error_count = 0
        errors = []
        
        for product in products:
            try:
                self.cur.execute(f"""
                    INSERT INTO {self.staging_table} (
                        product_code, product_name, product_url,
                        fit_options, colors_available, sizes_available,
                        category, subcategory, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                """, (
                    product.get('product_code'),
                    product.get('product_name'),
                    product.get('product_url'),
                    product.get('fit_options'),
                    product.get('colors'),
                    product.get('sizes'),
                    product.get('category'),
                    product.get('subcategory')
                ))
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append({
                    'product_code': product.get('product_code'),
                    'error': str(e)
                })
        
        print(f"   ✅ Imported: {success_count}")
        print(f"   ❌ Failed: {error_count}")
        
        if errors:
            print(f"\n   Errors:")
            for err in errors[:5]:
                print(f"      {err['product_code']}: {err['error'][:50]}...")
        
        return success_count, error_count
    
    def validate_staging(self):
        """Validate data in staging table"""
        print(f"\n🔍 Validating staging data...")
        
        # Use the SQL validation function
        self.cur.execute(f"SELECT * FROM validate_staging_import('{self.staging_table}')")
        validations = self.cur.fetchall()
        
        all_valid = True
        for validation_type, passed, message, details in validations:
            status = "✅" if passed else "❌"
            print(f"   {status} {validation_type}: {message}")
            if not passed and validation_type != 'Import Statistics':
                all_valid = False
        
        return all_valid
    
    def check_regressions(self):
        """Check for potential data regressions"""
        print(f"\n🔄 Checking for regressions...")
        
        # Products that would lose fit data
        self.cur.execute(f"""
            SELECT c.product_code, c.product_name, c.fit_options as current_fits, s.fit_options as new_fits
            FROM jcrew_product_cache c
            JOIN {self.staging_table} s ON c.product_code = s.product_code
            WHERE c.fit_options IS NOT NULL
            AND array_length(c.fit_options, 1) > 0
            AND (s.fit_options IS NULL OR array_length(s.fit_options, 1) = 0 OR array_length(s.fit_options, 1) IS NULL)
        """)
        
        regressions = self.cur.fetchall()
        if regressions:
            print(f"   ⚠️ WARNING: {len(regressions)} products would lose fit data:")
            for code, name, current, new in regressions[:5]:
                print(f"      {code}: {current} → {new}")
            return False
        else:
            print(f"   ✅ No regressions detected")
            return True
    
    def merge_to_production(self, skip_regressions=True):
        """Merge validated staging data to production"""
        print(f"\n🔀 Merging to production...")
        
        if skip_regressions:
            # Merge only non-regressing updates
            self.cur.execute(f"""
                INSERT INTO jcrew_product_cache
                SELECT s.*
                FROM {self.staging_table} s
                WHERE NOT EXISTS (
                    SELECT 1 FROM jcrew_product_cache c
                    WHERE c.product_code = s.product_code
                )
                ON CONFLICT (product_code) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    product_url = EXCLUDED.product_url,
                    fit_options = CASE
                        WHEN jcrew_product_cache.fit_options IS NOT NULL 
                        AND array_length(jcrew_product_cache.fit_options, 1) > 0
                        AND (EXCLUDED.fit_options IS NULL OR array_length(EXCLUDED.fit_options, 1) = 0)
                        THEN jcrew_product_cache.fit_options  -- Keep existing
                        ELSE EXCLUDED.fit_options  -- Use new
                    END,
                    colors_available = COALESCE(EXCLUDED.colors_available, jcrew_product_cache.colors_available),
                    sizes_available = COALESCE(EXCLUDED.sizes_available, jcrew_product_cache.sizes_available),
                    category = COALESCE(EXCLUDED.category, jcrew_product_cache.category),
                    subcategory = COALESCE(EXCLUDED.subcategory, jcrew_product_cache.subcategory),
                    updated_at = NOW()
            """)
        else:
            # Merge everything (not recommended)
            self.cur.execute(f"""
                INSERT INTO jcrew_product_cache
                SELECT * FROM {self.staging_table}
                ON CONFLICT (product_code) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    product_url = EXCLUDED.product_url,
                    fit_options = EXCLUDED.fit_options,
                    colors_available = EXCLUDED.colors_available,
                    sizes_available = EXCLUDED.sizes_available,
                    category = EXCLUDED.category,
                    subcategory = EXCLUDED.subcategory,
                    updated_at = NOW()
            """)
        
        affected = self.cur.rowcount
        print(f"   ✅ Merged {affected} products")
        return affected
    
    def cleanup_staging(self):
        """Drop the staging table"""
        print(f"\n🧹 Cleaning up staging table...")
        self.cur.execute(f"DROP TABLE IF EXISTS {self.staging_table}")
        print(f"   ✅ Staging table dropped")
    
    def safe_import_process(self, products_json_file=None):
        """Complete safe import process"""
        print("=" * 80)
        print("SAFE J.CREW IMPORT PROCESS")
        print("=" * 80)
        
        # Sample data for testing
        if not products_json_file:
            sample_products = [
                {
                    'product_code': 'TEST_IMPORT_001',
                    'product_name': 'Test Import Shirt',
                    'product_url': 'https://www.jcrew.com/test',
                    'fit_options': ['Classic', 'Slim'],
                    'colors': ['Blue', 'White'],
                    'sizes': ['S', 'M', 'L', 'XL'],
                    'category': 'Shirts',
                    'subcategory': 'Test'
                }
            ]
        else:
            with open(products_json_file, 'r') as f:
                sample_products = json.load(f)
        
        try:
            # Step 1: Create staging
            self.create_staging_table()
            
            # Step 2: Import to staging
            success, errors = self.import_to_staging(sample_products)
            
            if success == 0:
                print("\n❌ No products imported to staging. Aborting.")
                return False
            
            # Step 3: Validate
            valid = self.validate_staging()
            
            if not valid:
                print("\n⚠️ Validation failed. Review issues before proceeding.")
                response = input("Continue anyway? (y/N): ")
                if response.lower() != 'y':
                    self.cleanup_staging()
                    return False
            
            # Step 4: Check regressions
            no_regressions = self.check_regressions()
            
            if not no_regressions:
                print("\n⚠️ Regressions detected!")
                response = input("Skip regressing products? (Y/n): ")
                skip = response.lower() != 'n'
            else:
                skip = True
            
            # Step 5: Merge to production
            merged = self.merge_to_production(skip_regressions=skip)
            
            # Step 6: Cleanup
            self.cleanup_staging()
            
            print("\n" + "=" * 80)
            print(f"✅ IMPORT COMPLETE: {merged} products updated")
            print("=" * 80)
            return True
            
        except Exception as e:
            print(f"\n❌ Import failed: {e}")
            self.cleanup_staging()
            return False
        finally:
            self.cur.close()
            self.conn.close()

def demonstrate_safe_import():
    """Demonstrate the safe import process"""
    importer = SafeJCrewImporter()
    importer.safe_import_process()

if __name__ == "__main__":
    demonstrate_safe_import()
