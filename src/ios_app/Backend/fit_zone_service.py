"""
Fit Zone Service - Fast database-stored fit zone management
Replaces on-demand calculations with precomputed zones for better performance
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional
from datetime import datetime
from fit_zone_calculator import FitZoneCalculator


class FitZoneService:
    """Service for managing database-stored fit zones with event-driven updates"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def calculate_and_store_fit_zones(self, user_id: int) -> bool:
        """
        Calculate fit zones for a user and store them in the database
        This is the main method called when user's garment feedback changes
        """
        try:
            conn = self.get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            print(f"🔄 Calculating and storing fit zones for user {user_id}")
            
            # Get user's garments for fit zone calculation
            cur.execute("""
                SELECT ug.id, b.name as brand, ug.product_name, ug.size_label,
                       COALESCE(ug.fit_feedback, 'Good Fit') as fit_feedback,
                       CASE 
                           WHEN sge.chest_min IS NOT NULL AND sge.chest_max IS NOT NULL 
                           THEN CONCAT(sge.chest_min, '-', sge.chest_max)
                           WHEN sge.chest_min IS NOT NULL 
                           THEN sge.chest_min::text
                           ELSE '40.0'
                       END as chest_range
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id  
                LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                WHERE ug.user_id = %s AND ug.owns_garment = true
                ORDER BY ug.created_at DESC
            """, (user_id,))
            garment_rows = cur.fetchall()
            
            if not garment_rows:
                print(f"⚠️ No garments found for user {user_id}")
                return False
            
            # Convert to format expected by FitZoneCalculator
            garments = []
            for row in garment_rows:
                garments.append({
                    'brand': row['brand'],
                    'garment_name': row['product_name'],
                    'size': row['size_label'],
                    'fit_feedback': row['fit_feedback'],
                    'chest_range': row['chest_range']
                })
            
            print(f"📊 Found {len(garments)} garments for fit zone calculation")
            
            # Calculate fit zones using existing FitZoneCalculator
            # Use separate connection to avoid transaction conflicts
            calc_conn = self.get_db_connection() 
            calculator = FitZoneCalculator(user_id, calc_conn)
            fit_zone_result = calculator.calculate_chest_fit_zone(garments)
            calc_conn.close()
            
            if not fit_zone_result:
                print(f"❌ Could not calculate fit zones for user {user_id}: No result returned")
                return False
                
            # Check if result has zones (the calculator returns zones directly at top level)
            expected_zones = ['tight', 'good', 'relaxed']
            if not any(zone in fit_zone_result for zone in expected_zones):
                print(f"❌ Could not calculate fit zones for user {user_id}: No zones in result")
                print(f"Result keys: {list(fit_zone_result.keys())}")
                return False
            
            # Extract just the zone data (FitZoneCalculator returns zones at top level)
            zones = {zone: fit_zone_result[zone] for zone in expected_zones if zone in fit_zone_result}
            confidence = fit_zone_result.get('confidence', 0.8)
            data_points = len(garments)
            
            print(f"✅ Calculated zones: {list(zones.keys())}")
            print(f"Zone details: {zones}")
            
            # Store fit zones in database (currently just chest for Tops category)
            try:
                self._store_fit_zone_in_db(
                    cur, user_id, 'Tops', 'chest', zones, confidence, data_points
                )
            except Exception as store_error:
                print(f"❌ Error storing fit zones: {str(store_error)}")
                raise
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Successfully stored fit zones for user {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error calculating fit zones for user {user_id}: {str(e)}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def _store_fit_zone_in_db(
        self, 
        cursor, 
        user_id: int, 
        category: str, 
        dimension: str, 
        zones: dict, 
        confidence: float, 
        data_points: int
    ):
        """Store calculated fit zones in the database"""
        
        # Insert or update fit zones
        cursor.execute("""
            INSERT INTO user_fit_zones (
                user_id, category, dimension,
                tight_min, tight_max,
                good_min, good_max, 
                relaxed_min, relaxed_max,
                confidence_score, data_points_count, last_updated
            ) VALUES (
                %s, %s, %s,
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s, %s
            )
            ON CONFLICT (user_id, category, dimension) 
            DO UPDATE SET
                tight_min = EXCLUDED.tight_min,
                tight_max = EXCLUDED.tight_max,
                good_min = EXCLUDED.good_min,
                good_max = EXCLUDED.good_max,
                relaxed_min = EXCLUDED.relaxed_min,
                relaxed_max = EXCLUDED.relaxed_max,
                confidence_score = EXCLUDED.confidence_score,
                data_points_count = EXCLUDED.data_points_count,
                last_updated = EXCLUDED.last_updated
        """, (
            user_id, category, dimension,
            zones.get('tight', {}).get('min', 0),
            zones.get('tight', {}).get('max', 0),
            zones.get('good', {}).get('min', 0), 
            zones.get('good', {}).get('max', 0),
            zones.get('relaxed', {}).get('min', 0),
            zones.get('relaxed', {}).get('max', 0),
            confidence, data_points, datetime.now()
        ))
        
        print(f"💾 Stored {category}/{dimension} fit zones for user {user_id}")
    
    def get_stored_fit_zones(self, user_id: int, category: str) -> Optional[Dict]:
        """
        Get precomputed fit zones from database (FAST lookup)
        This replaces the slow on-demand calculation
        """
        try:
            conn = self.get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT dimension, tight_min, tight_max, good_min, good_max,
                       relaxed_min, relaxed_max, confidence_score, data_points_count,
                       last_updated
                FROM user_fit_zones 
                WHERE user_id = %s AND category = %s
            """, (user_id, category))
            
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            if not rows:
                print(f"⚠️ No stored fit zones found for user {user_id}, category {category}")
                return None
            
            # Convert to format expected by shopping API
            fit_zones = {}
            for row in rows:
                dimension = row['dimension']
                fit_zones[dimension] = {
                    'tight': {'min': float(row['tight_min']), 'max': float(row['tight_max'])},
                    'good': {'min': float(row['good_min']), 'max': float(row['good_max'])},
                    'relaxed': {'min': float(row['relaxed_min']), 'max': float(row['relaxed_max'])},
                    'confidence': float(row['confidence_score']),
                    'data_points': row['data_points_count'],
                    'last_updated': row['last_updated']
                }
            
            print(f"⚡ Retrieved stored fit zones for user {user_id}: {list(fit_zones.keys())}")
            return fit_zones
            
        except Exception as e:
            print(f"❌ Error retrieving fit zones for user {user_id}: {str(e)}")
            return None
    
    def populate_existing_users(self) -> int:
        """
        One-time migration: Calculate and store fit zones for all existing users
        """
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            
            # Get all users who have garments
            cur.execute("""
                SELECT DISTINCT user_id 
                FROM user_garments 
                WHERE owns_garment = true
                ORDER BY user_id
            """)
            user_ids = [row[0] for row in cur.fetchall()]
            
            cur.close()
            conn.close()
            
            print(f"🔄 Populating fit zones for {len(user_ids)} existing users")
            
            success_count = 0
            for user_id in user_ids:
                if self.calculate_and_store_fit_zones(user_id):
                    success_count += 1
                    print(f"✅ {success_count}/{len(user_ids)} users processed")
                else:
                    print(f"❌ Failed to process user {user_id}")
            
            print(f"🎉 Migration complete: {success_count}/{len(user_ids)} users processed")
            return success_count
            
        except Exception as e:
            print(f"❌ Error during migration: {str(e)}")
            return 0


if __name__ == "__main__":
    # Test script - populate fit zones for existing users
    DB_CONFIG = {
        "host": "aws-0-us-east-2.pooler.supabase.com",
        "port": 6543,
        "database": "postgres", 
        "user": "postgres.lbilxlkchzpducggkrxx",
        "password": "efvTower12"
    }
    
    service = FitZoneService(DB_CONFIG)
    service.populate_existing_users()