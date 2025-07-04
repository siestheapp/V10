"""
Estimate user body measurements (e.g., chest, sleeve, waist) from garment data and fit feedback.
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
        
        Algorithm:
        1. Get all garments the user owns with chest measurements and fit feedback
        2. Group by fit type (tight, good, relaxed)
        3. Calculate weighted average based on fit preference
        4. Return estimated chest measurement
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user's garments with chest measurements and fit feedback
            query = """
                SELECT 
                    b.name as brand,
                    ug.category as garment_name,
                    ug.chest_range,
                    ug.size_label as size,
                    ug.owns_garment,
                    ug.fit_feedback,
                    uff.chest_fit as chest_feedback
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
                WHERE ug.user_id = %s 
                AND ug.owns_garment = true
                AND ug.chest_range IS NOT NULL
                AND (ug.fit_feedback IS NOT NULL OR uff.chest_fit IS NOT NULL)
                ORDER BY ug.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            
            if not garments:
                self.logger.info(f"No garments found for user {user_id}")
                return None
            
            self.logger.info(f"Found {len(garments)} garments for user {user_id}")
            
            # Process each garment to extract chest measurement and fit type
            measurements = []
            
            for garment in garments:
                brand, garment_name, chest_range, size, owns_garment, fit_feedback, chest_feedback = garment
                
                # Parse chest range to get a single value (use average if range)
                chest_value = self._parse_chest_range(chest_range)
                if chest_value is None:
                    continue
                
                # Determine fit type from feedback
                fit_type = self._categorize_fit(chest_feedback)
                if fit_type is None:
                    continue
                
                measurements.append({
                    'chest_value': chest_value,
                    'fit_type': fit_type,
                    'brand': brand,
                    'size': size
                })
            
            if not measurements:
                self.logger.info(f"No valid measurements found for user {user_id}")
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
    
    def _parse_chest_range(self, chest_range: str) -> Optional[float]:
        """Parse chest range string to get average value"""
        try:
            if '-' in chest_range:
                # Range like "39-40" or "36.0-38.0"
                parts = chest_range.split('-')
                min_val = float(parts[0].strip())
                max_val = float(parts[1].strip())
                return (min_val + max_val) / 2
            else:
                # Single value like "47" or "41.00"
                return float(chest_range.strip())
        except (ValueError, IndexError):
            return None
    
    def _categorize_fit(self, feedback: str) -> Optional[str]:
        """Categorize fit feedback into tight, good, or relaxed"""
        feedback_lower = feedback.lower()
        
        if any(word in feedback_lower for word in ['tight', 'too tight']):
            return 'tight'
        elif any(word in feedback_lower for word in ['good fit', 'perfect']):
            return 'good'
        elif any(word in feedback_lower for word in ['loose', 'relaxed', 'comfortable']):
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

    def estimate_chest(self):
        estimates = []
        for g in self.garments:
            feedback = g.get('fit_feedback')
            chest_range = g.get('chest_range')
            if not feedback or not chest_range:
                continue
            # Use min value if range, else float
            if '-' in chest_range:
                chest = float(chest_range.split('-')[0])
            else:
                chest = float(chest_range)
            delta = self.FEEDBACK_DELTAS.get(feedback)
            if delta is not None:
                estimates.append(chest - delta)
        if not estimates:
            return None
        # Remove outliers (simple: 10th-90th percentile)
        estimates.sort()
        n = len(estimates)
        lower = int(n * 0.1)
        upper = int(n * 0.9)
        trimmed = estimates[lower:upper] if n > 4 else estimates
        return round(statistics.median(trimmed), 2)

    def estimate_neck_measurement(self, user_id: int) -> Optional[float]:
        """
        Estimate neck measurement based on user's garment data and fit feedback.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT 
                    b.name as brand,
                    ug.category as garment_name,
                    ug.neck_range,
                    ug.size_label as size,
                    ug.owns_garment,
                    ug.fit_feedback,
                    uff.neck_fit as neck_feedback
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
                WHERE ug.user_id = %s 
                AND ug.owns_garment = true
                AND ug.neck_range IS NOT NULL
                AND (ug.fit_feedback IS NOT NULL OR uff.neck_fit IS NOT NULL)
                ORDER BY ug.created_at DESC
            """
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            if not garments:
                self.logger.info(f"No garments with neck for user {user_id}")
                return None
            measurements = []
            for garment in garments:
                brand, garment_name, neck_range, size, owns_garment, fit_feedback, neck_feedback = garment
                neck_value = self._parse_chest_range(neck_range)
                if neck_value is None:
                    continue
                fit_type = self._categorize_fit(neck_feedback)
                if fit_type is None:
                    continue
                measurements.append({'neck_value': neck_value, 'fit_type': fit_type, 'brand': brand, 'size': size})
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
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT 
                    b.name as brand,
                    ug.category as garment_name,
                    ug.sleeve_range,
                    ug.size_label as size,
                    ug.owns_garment,
                    ug.fit_feedback,
                    uff.sleeve_fit as sleeve_feedback
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
                WHERE ug.user_id = %s 
                AND ug.owns_garment = true
                AND ug.sleeve_range IS NOT NULL
                AND (ug.fit_feedback IS NOT NULL OR uff.sleeve_fit IS NOT NULL)
                ORDER BY ug.created_at DESC
            """
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            if not garments:
                self.logger.info(f"No garments with sleeve for user {user_id}")
                return None
            measurements = []
            for garment in garments:
                brand, garment_name, sleeve_range, size, owns_garment, fit_feedback, sleeve_feedback = garment
                sleeve_value = self._parse_chest_range(sleeve_range)
                if sleeve_value is None:
                    continue
                fit_type = self._categorize_fit(sleeve_feedback)
                if fit_type is None:
                    continue
                measurements.append({'sleeve_value': sleeve_value, 'fit_type': fit_type, 'brand': brand, 'size': size})
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