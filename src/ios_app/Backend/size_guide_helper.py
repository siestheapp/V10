#!/usr/bin/env python3
"""
Size Guide Helper - Ensures correct schema usage

This helper prevents accidentally using deprecated size_guides tables
and provides the correct workflow for adding size guides.
"""

import psycopg2
import sys
import os
from typing import Dict, List, Tuple, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from db_config import DB_CONFIG

class SizeGuideHelper:
    """Helper class for managing size guides in the CURRENT schema"""
    
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()
    
    def check_schema_status(self):
        """Verify we're using the current schema"""
        print("🔍 SCHEMA STATUS CHECK")
        print("-" * 25)
        
        # Check deprecated tables
        deprecated_tables = ['size_guides', 'size_guide_entries']
        for table in deprecated_tables:
            self.cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cur.fetchone()[0]
            print(f"❌ DEPRECATED {table}: {count} rows (DO NOT ADD NEW ENTRIES)")
        
        # Check current tables
        current_tables = ['measurement_sets', 'measurements']
        for table in current_tables:
            self.cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cur.fetchone()[0]
            print(f"✅ CURRENT {table}: {count} rows (USE THIS)")
        
        print("\n⚠️  REMINDER: Always use measurement_sets + measurements tables!")
    
    def get_brand_measurement_sets(self, brand_id: int) -> List[Dict]:
        """Get existing measurement sets for a brand"""
        self.cur.execute("""
            SELECT id, fit_type, header, category_id, gender, 
                   (SELECT COUNT(*) FROM measurements WHERE set_id = ms.id) as measurement_count
            FROM measurement_sets ms
            WHERE brand_id = %s AND is_active = true
            ORDER BY fit_type
        """, (brand_id,))
        
        results = []
        for row in self.cur.fetchall():
            results.append({
                'set_id': row[0],
                'fit_type': row[1],
                'header': row[2],
                'category_id': row[3],
                'gender': row[4],
                'measurement_count': row[5]
            })
        
        return results
    
    def create_measurement_set(self, brand_id: int, category_id: int, 
                             fit_type: str, gender: str = 'male', 
                             unit: str = 'in', header: str = None,
                             notes: str = None) -> int:
        """
        Create a new measurement set (size guide)
        
        Returns: measurement_set_id for adding measurements
        """
        
        # Validate required constraint values
        scope = 'size_guide'  # Required for size guides
        garment_id = None     # Must be NULL for size guides
        
        # Check if this fit_type already exists
        existing = self.get_brand_measurement_sets(brand_id)
        for ms in existing:
            if ms['fit_type'] == fit_type and ms['category_id'] == category_id:
                raise ValueError(f"Measurement set already exists: {fit_type} for brand {brand_id}, category {category_id}")
        
        # Create the measurement set
        self.cur.execute("""
            INSERT INTO measurement_sets (
                brand_id, category_id, gender, fit_type, scope, garment_id,
                unit, header, notes, is_active, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW()
            ) RETURNING id
        """, (brand_id, category_id, gender, fit_type, scope, garment_id, 
              unit, header, notes))
        
        set_id = self.cur.fetchone()[0]
        self.conn.commit()
        
        print(f"✅ Created measurement set ID {set_id}: {fit_type} for brand {brand_id}")
        return set_id
    
    def add_measurements(self, set_id: int, brand_id: int, 
                        size_measurements: List[Tuple]) -> int:
        """
        Add measurements for each size to a measurement set
        
        size_measurements format:
        [
            ('S', [('body_chest', 35, 37), ('body_neck', 14, 14.5), ...]),
            ('M', [('body_chest', 38, 40), ('body_neck', 15, 15.5), ...]),
            ...
        ]
        
        Returns: number of measurements added
        """
        
        total_added = 0
        
        for size_label, measurements in size_measurements:
            for measurement_type, min_val, max_val in measurements:
                
                # Validate measurement_type format
                if not (measurement_type.startswith('body_') or measurement_type.startswith('garment_')):
                    raise ValueError(f"Invalid measurement_type: {measurement_type}. Must start with 'body_' or 'garment_'")
                
                self.cur.execute("""
                    INSERT INTO measurements (
                        set_id, brand_id, size_label, measurement_type,
                        min_value, max_value, unit, source_type,
                        created_at, created_by
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, 'in', 'size_guide', NOW(), 1
                    )
                """, (set_id, brand_id, size_label, measurement_type, min_val, max_val))
                
                total_added += 1
        
        self.conn.commit()
        print(f"✅ Added {total_added} measurements to set {set_id}")
        return total_added
    
    def add_complete_size_guide(self, brand_id: int, category_id: int,
                               fit_type: str, size_data: Dict,
                               gender: str = 'male', unit: str = 'in',
                               header: str = None, notes: str = None) -> Dict:
        """
        Complete workflow: Create measurement set + add all measurements
        
        size_data format:
        {
            'S': {'body_chest': (35, 37), 'body_neck': (14, 14.5), ...},
            'M': {'body_chest': (38, 40), 'body_neck': (15, 15.5), ...},
            ...
        }
        """
        
        print(f"\n🏷️  Adding {fit_type} size guide for brand {brand_id}")
        print("-" * 50)
        
        # Step 1: Create measurement set
        set_id = self.create_measurement_set(
            brand_id, category_id, fit_type, gender, unit, header, notes
        )
        
        # Step 2: Convert size_data to the format expected by add_measurements
        size_measurements = []
        for size_label, measurements in size_data.items():
            measurement_list = [(mt, min_val, max_val) for mt, (min_val, max_val) in measurements.items()]
            size_measurements.append((size_label, measurement_list))
        
        # Step 3: Add measurements
        measurement_count = self.add_measurements(set_id, brand_id, size_measurements)
        
        result = {
            'set_id': set_id,
            'fit_type': fit_type,
            'measurement_count': measurement_count,
            'sizes': list(size_data.keys())
        }
        
        print(f"\n🎉 Size guide added successfully!")
        print(f"   • Set ID: {set_id}")
        print(f"   • Fit Type: {fit_type}")
        print(f"   • Sizes: {', '.join(result['sizes'])}")
        print(f"   • Measurements: {measurement_count}")
        
        return result

def prevent_deprecated_usage():
    """Show warning if someone tries to use deprecated tables"""
    print("🚨 WARNING: DEPRECATED SCHEMA DETECTED")
    print("=" * 50)
    print("You're trying to use the old size_guides schema.")
    print("Please use the SizeGuideHelper class instead:")
    print("")
    print("from size_guide_helper import SizeGuideHelper")
    print("")
    print("with SizeGuideHelper() as helper:")
    print("    helper.add_complete_size_guide(...)")
    print("")
    print("See DATABASE_SCHEMA_GUIDE.md for full documentation.")

if __name__ == "__main__":
    # Example usage
    with SizeGuideHelper() as helper:
        helper.check_schema_status()
        
        # Show existing J.Crew measurement sets
        print("\n📊 J.Crew Measurement Sets:")
        jcrew_sets = helper.get_brand_measurement_sets(4)
        for ms in jcrew_sets:
            print(f"  • {ms['fit_type']}: {ms['header']} ({ms['measurement_count']} measurements)")

