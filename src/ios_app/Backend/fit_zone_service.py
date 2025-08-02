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
            
            # Store chest fit zones in database
            try:
                self._store_fit_zone_in_db(
                    cur, user_id, 'Tops', 'chest', zones, confidence, data_points
                )
            except Exception as store_error:
                print(f"❌ Error storing chest fit zones: {str(store_error)}")
                raise
            
            # Calculate and store neck/sleeve acceptable ranges for performance
            print(f"🔄 Calculating neck/sleeve acceptable ranges for user {user_id}")
            try:
                acceptable_ranges = self._calculate_acceptable_ranges(user_id)
                for dimension, range_data in acceptable_ranges.items():
                    self._store_acceptable_range_in_db(
                        cur, user_id, 'Tops', dimension, 
                        range_data['min'], range_data['max'],
                        range_data['confidence'], range_data['data_points']
                    )
                    print(f"✅ Stored {dimension} acceptable range: {range_data['min']:.1f}-{range_data['max']:.1f}")
            except Exception as range_error:
                print(f"⚠️ Error storing acceptable ranges (continuing): {str(range_error)}")
                # Don't fail the whole operation if acceptable ranges fail
            
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

    def _calculate_acceptable_ranges(self, user_id: int) -> Dict[str, Dict]:
        """
        Calculate acceptable ranges for neck/sleeve dimensions based on positive feedback
        This mirrors the logic from SimpleMultiDimensionalAnalyzer but caches the results
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Get user's garments with measurements and positive feedback
            query = """
                SELECT 
                    ug.id, b.name as brand, ug.product_name, ug.size_label,
                    sge.neck_min, sge.neck_max, sge.neck_range,
                    sge.sleeve_min, sge.sleeve_max, sge.sleeve_range,
                    COALESCE(
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'neck' 
                         ORDER BY ugf.created_at DESC LIMIT 1),
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' 
                         ORDER BY ugf.created_at DESC LIMIT 1)
                    ) as neck_feedback,
                    COALESCE(
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'sleeve' 
                         ORDER BY ugf.created_at DESC LIMIT 1),
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' 
                         ORDER BY ugf.created_at DESC LIMIT 1)
                    ) as sleeve_feedback
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                WHERE ug.user_id = %s AND ug.owns_garment = true
                AND sge.id IS NOT NULL  -- Must have measurements
                ORDER BY ug.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Process garments to create dimension profiles
            dimension_data = {'neck': [], 'sleeve': []}
            positive_feedback = ['Good Fit', 'Tight but I Like It', 'Loose but I Like It', 'Slightly Loose']
            
            for garment in garments:
                (garment_id, brand, product_name, size_label,
                 neck_min, neck_max, neck_range,
                 sleeve_min, sleeve_max, sleeve_range,
                 neck_feedback, sleeve_feedback) = garment
                
                # Process neck dimension
                if neck_feedback in positive_feedback and neck_min is not None:
                    actual_min, actual_max = self._parse_min_max_values(neck_min, neck_max, neck_range)
                    if actual_min is not None and actual_max is not None:
                        dimension_data['neck'].append({
                            'min_measurement': actual_min,
                            'max_measurement': actual_max,
                            'garment': f"{brand} {size_label}",
                            'feedback': neck_feedback
                        })
                
                # Process sleeve dimension  
                if sleeve_feedback in positive_feedback and sleeve_min is not None:
                    actual_min, actual_max = self._parse_min_max_values(sleeve_min, sleeve_max, sleeve_range)
                    if actual_min is not None and actual_max is not None:
                        dimension_data['sleeve'].append({
                            'min_measurement': actual_min,
                            'max_measurement': actual_max,
                            'garment': f"{brand} {size_label}",
                            'feedback': sleeve_feedback
                        })
            
            # Calculate ranges for each dimension
            acceptable_ranges = {}
            for dimension, data_points in dimension_data.items():
                if len(data_points) >= 1:  # Need at least 1 garment with positive feedback
                    all_mins = [dp['min_measurement'] for dp in data_points]
                    all_maxs = [dp['max_measurement'] for dp in data_points]
                    
                    # Calculate acceptable range from all positive feedback
                    acceptable_min = min(all_mins)  # Minimum of all minimum measurements
                    acceptable_max = max(all_maxs)  # Maximum of all maximum measurements
                    
                    confidence = min(1.0, len(data_points) / 3.0)  # Full confidence with 3+ garments
                    
                    acceptable_ranges[dimension] = {
                        'min': acceptable_min,
                        'max': acceptable_max,
                        'confidence': confidence,
                        'data_points': len(data_points)
                    }
                    
                    print(f"📏 {dimension}: {acceptable_min:.1f}-{acceptable_max:.1f} from {len(data_points)} garments")
            
            return acceptable_ranges
            
        except Exception as e:
            print(f"❌ Error calculating acceptable ranges: {str(e)}")
            return {}

    def _parse_min_max_values(self, min_val, max_val, range_str):
        """Parse measurement to get actual min and max values (not midpoint average)"""
        try:
            if min_val is not None and max_val is not None:
                return (float(min_val), float(max_val))
            elif range_str is not None:
                if '-' in range_str:
                    parts = range_str.split('-')
                    min_part = float(parts[0].strip())
                    max_part = float(parts[1].strip())
                    return (min_part, max_part)
                else:
                    # Single value - use as both min and max
                    val = float(range_str.strip())
                    return (val, val)
            elif min_val is not None:
                return (float(min_val), float(min_val))
            elif max_val is not None:
                return (float(max_val), float(max_val))
            else:
                return (None, None)
        except (ValueError, IndexError):
            return (None, None)
    
    def _store_acceptable_range_in_db(
        self, 
        cursor, 
        user_id: int, 
        category: str, 
        dimension: str, 
        acceptable_min: float,
        acceptable_max: float,
        confidence: float, 
        data_points: int
    ):
        """Store calculated acceptable ranges in the database (using good_min/good_max columns)"""
        
        # Insert or update acceptable ranges - use good_min/good_max, leave tight/relaxed as NULL
        cursor.execute("""
            INSERT INTO user_fit_zones (
                user_id, category, dimension,
                tight_min, tight_max,
                good_min, good_max, 
                relaxed_min, relaxed_max,
                confidence_score, data_points_count, last_updated
            ) VALUES (
                %s, %s, %s,
                NULL, NULL,
                %s, %s,
                NULL, NULL,
                %s, %s, %s
            )
            ON CONFLICT (user_id, category, dimension) 
            DO UPDATE SET
                good_min = EXCLUDED.good_min,
                good_max = EXCLUDED.good_max,
                confidence_score = EXCLUDED.confidence_score,
                data_points_count = EXCLUDED.data_points_count,
                last_updated = EXCLUDED.last_updated,
                tight_min = NULL,
                tight_max = NULL,
                relaxed_min = NULL,
                relaxed_max = NULL
        """, (
            user_id, category, dimension,
            acceptable_min, acceptable_max,
            confidence, data_points, datetime.now()
        ))
        
        print(f"💾 Stored {category}/{dimension} acceptable range for user {user_id}")
    
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
                
                # Check if this is a full fit zone (chest) or just acceptable range (neck/sleeve)
                has_fit_zones = (row['tight_min'] is not None and row['relaxed_min'] is not None)
                
                if has_fit_zones:
                    # Full fit zones for chest dimension
                    fit_zones[dimension] = {
                        'tight': {'min': float(row['tight_min']), 'max': float(row['tight_max'])},
                        'good': {'min': float(row['good_min']), 'max': float(row['good_max'])},
                        'relaxed': {'min': float(row['relaxed_min']), 'max': float(row['relaxed_max'])},
                        'confidence': float(row['confidence_score']),
                        'data_points': row['data_points_count'],
                        'last_updated': row['last_updated']
                    }
                else:
                    # Acceptable range only for neck/sleeve dimensions
                    fit_zones[dimension] = {
                        'acceptable_min': float(row['good_min']),
                        'acceptable_max': float(row['good_max']),
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