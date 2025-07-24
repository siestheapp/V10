"""
Estimate user body measurements (e.g., chest, sleeve, waist) from garment data and fit feedback.
Updated for tailor3 database schema.
"""
import statistics
import psycopg2
from typing import Dict, List, Optional, Tuple
import logging

class BodyMeasurementEstimator:
    FEEDBACK_DELTAS = {
        "Too Tight": 0.0,
        "Tight but I Like It": 0.5,
        "Good Fit": 1.0,
        "Loose but I Like It": 2.5,
        "Too Loose": 3.5
    }

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def estimate_chest_measurement(self, user_id: int) -> Optional[float]:
        """
        Estimate chest measurement based on user's garment data and fit feedback.
        Updated for tailor3 schema.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user's garments with chest measurements and fit feedback
            # Updated query for tailor3 schema
            query = """
                SELECT 
                    b.name as brand,
                    ug.product_name,
                    ug.size_label,
                    ug.owns_garment,
                    sge.chest_min,
                    sge.chest_max,
                    sge.chest_range,
                    ugf.dimension,
                    fc.feedback_text as feedback
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
                LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                WHERE ug.user_id = %s 
                AND ug.owns_garment = true
                AND (sge.chest_min IS NOT NULL OR sge.chest_max IS NOT NULL OR sge.chest_range IS NOT NULL)
                AND ugf.dimension = 'chest'
                ORDER BY ug.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            
            if not garments:
                self.logger.info(f"No garments with chest measurements found for user {user_id}")
                return None
            
            self.logger.info(f"Found {len(garments)} garments with chest measurements for user {user_id}")
            
            # Process each garment to extract chest measurement and fit type
            measurements = []
            
            for garment in garments:
                brand, product_name, size_label, owns_garment, chest_min, chest_max, chest_range, dimension, feedback = garment
                
                # Parse chest measurement to get a single value
                chest_value = self._parse_chest_measurement(chest_min, chest_max, chest_range)
                
                if chest_value is None:
                    continue
                
                # Determine fit type from feedback
                fit_type = self._categorize_fit(feedback)
                
                if fit_type is None:
                    continue
                
                measurements.append({
                    'chest_value': chest_value,
                    'fit_type': fit_type,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label
                })
            
            if not measurements:
                self.logger.info(f"No valid chest measurements found for user {user_id}")
                return None
            
            # Group measurements by fit type
            fit_groups = {'tight': [], 'good': [], 'relaxed': []}
            
            for measurement in measurements:
                fit_type = measurement['fit_type']
                if fit_type in fit_groups:
                    fit_groups[fit_type].append(measurement['chest_value'])
            
            # Calculate weighted average
            estimated_chest = self._calculate_weighted_average(fit_groups)
            
            self.logger.info(f"Estimated chest measurement for user {user_id}: {estimated_chest}")
            
            cursor.close()
            conn.close()
            
            return estimated_chest
            
        except Exception as e:
            self.logger.error(f"Error estimating chest measurement for user {user_id}: {str(e)}")
            return None
    
    def _parse_chest_measurement(self, chest_min: Optional[float], chest_max: Optional[float], chest_range: Optional[str]) -> Optional[float]:
        """Parse chest measurement to get average value"""
        try:
            if chest_min is not None and chest_max is not None:
                # Convert Decimal to float if needed
                min_val = float(chest_min) if chest_min is not None else None
                max_val = float(chest_max) if chest_max is not None else None
                return (min_val + max_val) / 2
            elif chest_range is not None:
                if '-' in chest_range:
                    parts = chest_range.split('-')
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    return (min_val + max_val) / 2
                else:
                    return float(chest_range.strip())
            elif chest_min is not None:
                return float(chest_min)
            elif chest_max is not None:
                return float(chest_max)
            else:
                return None
        except (ValueError, IndexError):
            return None
    
    def _categorize_fit(self, feedback: str) -> Optional[str]:
        """Categorize fit feedback into tight, good, or relaxed"""
        if not feedback:
            return None
            
        feedback_lower = feedback.lower()
        
        # Tight category
        if any(word in feedback_lower for word in ['too tight', 'tight but i like it', 'slightly tight']):
            return 'tight'
        # Good category  
        elif any(word in feedback_lower for word in ['good fit', 'perfect']):
            return 'good'
        # Relaxed/Loose category
        elif any(word in feedback_lower for word in ['loose', 'relaxed', 'comfortable', 'too loose', 'slightly loose', 'loose but i like it']):
            return 'relaxed'
        else:
            return None
    
    def _calculate_weighted_average(self, fit_groups: Dict[str, List[float]]) -> float:
        """
        Calculate weighted average based on fit preferences.
        Weights: good fit = 1.0, tight = 0.8 (slightly smaller), relaxed = 1.2 (slightly larger)
        """
        weights = {'tight': 0.8, 'good': 1.0, 'relaxed': 1.2}
        total_weighted_sum = 0
        total_weight = 0
        
        for fit_type, measurements in fit_groups.items():
            if measurements:
                weight = weights[fit_type]
                avg_measurement = sum(measurements) / len(measurements)
                total_weighted_sum += avg_measurement * weight * len(measurements)
                total_weight += weight * len(measurements)
        
        if total_weight == 0:
            return 0
        
        return total_weighted_sum / total_weight

    def estimate_neck_measurement(self, user_id: int) -> Optional[float]:
        """
        Estimate neck measurement based on user's garment data and fit feedback.
        Updated for tailor3 schema.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    b.name as brand,
                    ug.product_name,
                    ug.size_label,
                    ug.owns_garment,
                    sge.neck_min,
                    sge.neck_max,
                    sge.neck_range,
                    ugf.dimension,
                    fc.feedback_text as feedback
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
                LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                WHERE ug.user_id = %s 
                AND ug.owns_garment = true
                AND (sge.neck_min IS NOT NULL OR sge.neck_max IS NOT NULL OR sge.neck_range IS NOT NULL)
                AND ugf.dimension = 'neck'
                ORDER BY ug.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            
            if not garments:
                self.logger.info(f"No garments with neck measurements found for user {user_id}")
                return None
            
            measurements = []
            for garment in garments:
                brand, product_name, size_label, owns_garment, neck_min, neck_max, neck_range, dimension, feedback = garment
                
                neck_value = self._parse_chest_measurement(neck_min, neck_max, neck_range)
                if neck_value is None:
                    continue
                
                fit_type = self._categorize_fit(feedback)
                if fit_type is None:
                    continue
                
                measurements.append({
                    'neck_value': neck_value,
                    'fit_type': fit_type,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label
                })
            
            if not measurements:
                return None
            
            fit_groups = {'tight': [], 'good': [], 'relaxed': []}
            for measurement in measurements:
                fit_type = measurement['fit_type']
                if fit_type in fit_groups:
                    fit_groups[fit_type].append(measurement['neck_value'])
            
            estimated_neck = self._calculate_weighted_average(fit_groups)
            
            cursor.close()
            conn.close()
            
            return estimated_neck
            
        except Exception as e:
            self.logger.error(f"Error estimating neck measurement for user {user_id}: {str(e)}")
            return None

    def estimate_sleeve_measurement(self, user_id: int) -> Optional[float]:
        """
        Estimate sleeve measurement based on user's garment data and fit feedback.
        Updated for tailor3 schema.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    b.name as brand,
                    ug.product_name,
                    ug.size_label,
                    ug.owns_garment,
                    sge.sleeve_min,
                    sge.sleeve_max,
                    sge.sleeve_range,
                    ugf.dimension,
                    fc.feedback_text as feedback
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
                LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                WHERE ug.user_id = %s 
                AND ug.owns_garment = true
                AND (sge.sleeve_min IS NOT NULL OR sge.sleeve_max IS NOT NULL OR sge.sleeve_range IS NOT NULL)
                AND ugf.dimension = 'sleeve'
                ORDER BY ug.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            
            if not garments:
                self.logger.info(f"No garments with sleeve measurements found for user {user_id}")
                return None
            
            measurements = []
            for garment in garments:
                brand, product_name, size_label, owns_garment, sleeve_min, sleeve_max, sleeve_range, dimension, feedback = garment
                
                sleeve_value = self._parse_chest_measurement(sleeve_min, sleeve_max, sleeve_range)
                if sleeve_value is None:
                    continue
                
                fit_type = self._categorize_fit(feedback)
                if fit_type is None:
                    continue
                
                measurements.append({
                    'sleeve_value': sleeve_value,
                    'fit_type': fit_type,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label
                })
            
            if not measurements:
                return None
            
            fit_groups = {'tight': [], 'good': [], 'relaxed': []}
            for measurement in measurements:
                fit_type = measurement['fit_type']
                if fit_type in fit_groups:
                    fit_groups[fit_type].append(measurement['sleeve_value'])
            
            estimated_sleeve = self._calculate_weighted_average(fit_groups)
            
            cursor.close()
            conn.close()
            
            return estimated_sleeve
            
        except Exception as e:
            self.logger.error(f"Error estimating sleeve measurement for user {user_id}: {str(e)}")
            return None 