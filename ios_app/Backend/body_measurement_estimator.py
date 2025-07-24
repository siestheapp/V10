"""
Estimate user body measurements (e.g., chest, sleeve, waist) from garment data and fit feedback.
Updated for tailor3 database schema with improved algorithms and validation.
Includes proper garment-to-body measurement conversion with ease calculations.
"""
import statistics
import psycopg2
from typing import Dict, List, Optional, Tuple
import logging

class BodyMeasurementEstimator:
    # Feedback deltas for different fit types (how much to adjust the garment measurement)
    FEEDBACK_DELTAS = {
        "Too Tight": -2.0,        # User's body is 2" larger than garment
        "Tight but I Like It": -1.0,  # User's body is 1" larger than garment
        "Good Fit": 0.0,          # User's body matches garment measurement
        "Slightly Loose": 0.5,    # User's body is 0.5" smaller than garment
        "Loose but I Like It": 1.0,   # User's body is 1" smaller than garment
        "Too Loose": 2.0          # User's body is 2" smaller than garment
    }
    
    # Industry standard ease amounts (garment measurement - body measurement)
    EASE_AMOUNTS = {
        'tight_fit': 0.5,      # 0-1 inch ease
        'regular_fit': 1.5,    # 1-2 inches ease  
        'loose_fit': 3.0,      # 2-4 inches ease
        'oversized_fit': 5.0   # 4-6+ inches ease
    }
    
    # Size guide specificity confidence weights
    GUIDE_LEVEL_WEIGHTS = {
        'product_level': 1.0,    # Most specific - garment-specific measurements
        'category_level': 0.8,   # Category-specific measurements  
        'brand_level': 0.6       # Least specific - brand-wide measurements
    }
    
    # Size adjustment factors (how much larger each size typically is)
    SIZE_ADJUSTMENTS = {
        'XS': -4.0, 'S': -2.0, 'M': 0.0, 'L': 2.0, 'XL': 4.0, 'XXL': 6.0, 'XXXL': 8.0
    }

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def garment_to_body_measurement(self, garment_measurement: float, fit_type: str = 'regular_fit') -> float:
        """
        Convert garment measurement to body measurement using industry standard ease.
        
        Formula: Body Measurement = Garment Measurement - Ease
        
        Args:
            garment_measurement: The garment's measurement (e.g., chest width)
            fit_type: Expected fit type ('tight_fit', 'regular_fit', 'loose_fit', 'oversized_fit')
            
        Returns:
            Estimated body measurement
        """
        ease = self.EASE_AMOUNTS.get(fit_type, self.EASE_AMOUNTS['regular_fit'])
        body_measurement = garment_measurement - ease
        
        self.logger.debug(f"Garment {garment_measurement}\" - {ease}\" ease = {body_measurement}\" body ({fit_type})")
        return body_measurement
    
    def body_to_garment_measurement(self, body_measurement: float, desired_fit: str = 'regular_fit') -> float:
        """
        Convert body measurement to required garment measurement for desired fit.
        
        Formula: Garment Measurement = Body Measurement + Ease
        
        Args:
            body_measurement: The user's body measurement
            desired_fit: Desired fit type ('tight_fit', 'regular_fit', 'loose_fit', 'oversized_fit')
            
        Returns:
            Required garment measurement for desired fit
        """
        ease = self.EASE_AMOUNTS.get(desired_fit, self.EASE_AMOUNTS['regular_fit'])
        garment_measurement = body_measurement + ease
        
        self.logger.debug(f"Body {body_measurement}\" + {ease}\" ease = {garment_measurement}\" garment ({desired_fit})")
        return garment_measurement
    
    def predict_garment_fit(self, user_body_measurement: float, garment_measurement: float) -> Dict[str, any]:
        """
        Predict how a garment will fit based on user's body measurement and garment measurement.
        
        Args:
            user_body_measurement: User's actual body measurement
            garment_measurement: The garment's measurement
            
        Returns:
            Dictionary with fit prediction details
        """
        ease = garment_measurement - user_body_measurement
        
        # Determine fit category based on ease amount
        if ease < 0:
            fit_category = "Too Tight"
            confidence = 0.9
        elif ease < 1:
            fit_category = "Tight but I Like It" 
            confidence = 0.8
        elif ease <= 2:
            fit_category = "Good Fit"
            confidence = 0.9
        elif ease <= 4:
            fit_category = "Loose but I Like It"
            confidence = 0.8
        else:
            fit_category = "Too Loose"
            confidence = 0.7
        
        return {
            'predicted_fit': fit_category,
            'ease_amount': ease,
            'confidence': confidence,
            'explanation': f"Garment ({garment_measurement}\") - Body ({user_body_measurement}\") = {ease}\" ease"
        }
    
    def estimate_chest_measurement(self, user_id: int) -> Optional[float]:
        """
        Estimate chest measurement based on user's garment data and fit feedback.
        This is the most reliable measurement since garment chest closely correlates with body chest.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user's garments with chest measurements and fit feedback
            query = """
                SELECT 
                    b.name as brand,
                    ug.product_name,
                    ug.size_label,
                    ug.owns_garment,
                    sge.chest_min,
                    sge.chest_max,
                    sge.chest_range,
                    sg.guide_level,
                    ugf.dimension,
                    fc.feedback_text as feedback
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                LEFT JOIN size_guides sg ON sge.size_guide_id = sg.id
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
            
            # Process each garment to calculate estimated body measurement
            body_measurements = []
            
            for garment in garments:
                brand, product_name, size_label, owns_garment, chest_min, chest_max, chest_range, guide_level, dimension, feedback = garment
                
                # Parse garment chest measurement
                garment_chest = self._parse_measurement(chest_min, chest_max, chest_range)
                if garment_chest is None:
                    continue
                
                # Method 1: Use feedback-based adjustment (current approach)
                feedback_delta = self.FEEDBACK_DELTAS.get(feedback, 0.0)
                body_estimate_feedback = garment_chest + feedback_delta
                
                # Method 2: Use ease-based conversion (industry standard)
                # Assume regular fit if "Good Fit", adjust for other feedback
                if feedback == "Good Fit":
                    fit_type = 'regular_fit'
                elif feedback in ["Tight but I Like It", "Too Tight"]:
                    fit_type = 'tight_fit'
                elif feedback in ["Loose but I Like It", "Slightly Loose"]:
                    fit_type = 'loose_fit'
                elif feedback == "Too Loose":
                    fit_type = 'oversized_fit'
                else:
                    fit_type = 'regular_fit'
                
                body_estimate_ease = self.garment_to_body_measurement(garment_chest, fit_type)
                
                # Average the two methods for more robust estimate
                body_estimate_combined = (body_estimate_feedback + body_estimate_ease) / 2
                
                body_measurements.append({
                    'measurement': body_estimate_combined,
                    'garment_chest': garment_chest,
                    'feedback': feedback,
                    'feedback_method': body_estimate_feedback,
                    'ease_method': body_estimate_ease,
                    'fit_type': fit_type,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label,
                    'confidence': self._calculate_confidence(feedback, len(garments), guide_level)
                })
                
                self.logger.info(f"Garment: {brand} {size_label}, Garment chest: {garment_chest}\", "
                               f"Feedback: {feedback}, Feedback method: {body_estimate_feedback}\", "
                               f"Ease method ({fit_type}): {body_estimate_ease}\", "
                               f"Combined estimate: {body_estimate_combined}\"")
            
            if not body_measurements:
                self.logger.info(f"No valid chest measurements found for user {user_id}")
                return None
            
            # Calculate weighted average of body measurements
            estimated_chest = self._calculate_confidence_weighted_average(body_measurements)
            
            self.logger.info(f"Final estimated chest measurement for user {user_id}: {estimated_chest}\"")
            
            cursor.close()
            conn.close()
            
            return estimated_chest
            
        except Exception as e:
            self.logger.error(f"Error estimating chest measurement for user {user_id}: {str(e)}")
            return None
    
    def get_size_recommendations(self, user_body_chest: float, brand_name: str = None) -> List[Dict]:
        """
        Get size recommendations for a user based on their body measurements.
        
        Args:
            user_body_chest: User's estimated body chest measurement
            brand_name: Optional brand to filter recommendations
            
        Returns:
            List of size recommendations with fit predictions
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query for available garments/sizes
            where_clause = "WHERE b.name = %s" if brand_name else ""
            params = [brand_name] if brand_name else []
            
            query = f"""
                SELECT 
                    b.name as brand,
                    sge.size_label,
                    sge.chest_min,
                    sge.chest_max,
                    sge.chest_range
                FROM size_guide_entries sge
                JOIN size_guides sg ON sge.size_guide_id = sg.id
                JOIN brands b ON sg.brand_id = b.id
                {where_clause}
                AND (sge.chest_min IS NOT NULL OR sge.chest_max IS NOT NULL OR sge.chest_range IS NOT NULL)
                ORDER BY b.name, sge.size_label
            """
            
            cursor.execute(query, params)
            garments = cursor.fetchall()
            
            recommendations = []
            
            for garment in garments:
                brand, size_label, chest_min, chest_max, chest_range = garment
                
                garment_chest = self._parse_measurement(chest_min, chest_max, chest_range)
                if garment_chest is None:
                    continue
                
                # Predict fit for this garment
                fit_prediction = self.predict_garment_fit(user_body_chest, garment_chest)
                
                recommendations.append({
                    'brand': brand,
                    'size': size_label,
                    'garment_chest': garment_chest,
                    'predicted_fit': fit_prediction['predicted_fit'],
                    'ease_amount': fit_prediction['ease_amount'],
                    'confidence': fit_prediction['confidence'],
                    'explanation': fit_prediction['explanation']
                })
            
            # Sort by confidence and fit preference
            recommendations.sort(key=lambda x: (
                x['confidence'] if x['predicted_fit'] in ['Good Fit', 'Tight but I Like It', 'Loose but I Like It'] else 0,
                -abs(x['ease_amount'] - 1.5)  # Prefer ~1.5" ease (regular fit)
            ), reverse=True)
            
            cursor.close()
            conn.close()
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting size recommendations: {str(e)}")
            return []
    
    def estimate_neck_measurement(self, user_id: int) -> Optional[float]:
        """
        Estimate neck measurement using both specific neck feedback AND inferring from overall fit.
        If user rates a garment "Good Fit" overall, we assume the neck is also acceptable.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query for garments with neck measurements and EITHER neck feedback OR overall "Good Fit"
            query = """
                SELECT 
                    b.name as brand,
                    ug.product_name,
                    ug.size_label,
                    sge.neck_min,
                    sge.neck_max,
                    sge.neck_range,
                    sg.guide_level,
                    neck_fc.feedback_text as neck_feedback,
                    overall_fc.feedback_text as overall_feedback,
                    CASE 
                        WHEN neck_fc.feedback_text IS NOT NULL THEN 'specific'
                        WHEN overall_fc.feedback_text = 'Good Fit' THEN 'inferred'
                        ELSE 'none'
                    END as feedback_source
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                LEFT JOIN size_guides sg ON sge.size_guide_id = sg.id
                -- Get specific neck feedback
                LEFT JOIN user_garment_feedback neck_ugf ON ug.id = neck_ugf.user_garment_id AND neck_ugf.dimension = 'neck'
                LEFT JOIN feedback_codes neck_fc ON neck_ugf.feedback_code_id = neck_fc.id
                -- Get overall feedback
                LEFT JOIN user_garment_feedback overall_ugf ON ug.id = overall_ugf.user_garment_id AND overall_ugf.dimension = 'overall'
                LEFT JOIN feedback_codes overall_fc ON overall_ugf.feedback_code_id = overall_fc.id
                WHERE ug.user_id = %s 
                AND ug.owns_garment = true
                AND (sge.neck_min IS NOT NULL OR sge.neck_max IS NOT NULL OR sge.neck_range IS NOT NULL)
                AND (neck_fc.feedback_text IS NOT NULL OR overall_fc.feedback_text = 'Good Fit')
                ORDER BY 
                    CASE WHEN neck_fc.feedback_text IS NOT NULL THEN 1 ELSE 2 END, -- Prioritize specific feedback
                    ug.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            
            if not garments:
                self.logger.info(f"No garments with neck measurements and feedback found for user {user_id}")
                return None
            
            specific_feedback_count = len([g for g in garments if g[7] is not None])  # neck_feedback IS NOT NULL
            inferred_feedback_count = len(garments) - specific_feedback_count
            
            self.logger.info(f"Found {len(garments)} garments with neck measurements for user {user_id}:")
            self.logger.info(f"  - {specific_feedback_count} with specific neck feedback")
            self.logger.info(f"  - {inferred_feedback_count} inferred from overall 'Good Fit'")
            
            # Process each garment
            body_measurements = []
            for garment in garments:
                (brand, product_name, size_label, neck_min, neck_max, neck_range, 
                 guide_level, neck_feedback, overall_feedback, feedback_source) = garment
                
                garment_neck = self._parse_measurement(neck_min, neck_max, neck_range)
                if garment_neck is None:
                    continue
                
                # Determine which feedback to use and confidence adjustment
                if feedback_source == 'specific':
                    # Use specific neck feedback with full confidence
                    feedback_to_use = neck_feedback
                    confidence_multiplier = 1.0
                    self.logger.info(f"  {brand} {size_label}: Using SPECIFIC neck feedback '{neck_feedback}'")
                elif feedback_source == 'inferred':
                    # Infer "Good Fit" for neck from overall feedback, but with lower confidence
                    feedback_to_use = "Good Fit"
                    confidence_multiplier = 0.7  # Lower confidence for inferred feedback
                    self.logger.info(f"  {brand} {size_label}: INFERRED neck fit from overall 'Good Fit'")
                else:
                    continue
                
                # For neck, we use smaller deltas since garment neck opening != body neck circumference
                neck_feedback_delta = self.FEEDBACK_DELTAS.get(feedback_to_use, 0.0) * 0.3  # Reduce impact
                
                # Also use ease-based conversion
                if feedback_to_use == "Good Fit":
                    fit_type = 'regular_fit'
                elif feedback_to_use in ["Tight but I Like It", "Too Tight"]:
                    fit_type = 'tight_fit'
                elif feedback_to_use in ["Loose but I Like It", "Slightly Loose"]:
                    fit_type = 'loose_fit'
                else:
                    fit_type = 'regular_fit'
                
                # For neck, ease conversion is less reliable, so we weight it less
                body_estimate_ease = self.garment_to_body_measurement(garment_neck, fit_type)
                body_estimate_feedback = garment_neck + neck_feedback_delta
                
                # Weight the feedback method more heavily for neck since ease is less reliable
                body_estimate_combined = (body_estimate_feedback * 0.7 + body_estimate_ease * 0.3)
                
                base_confidence = self._calculate_confidence(feedback_to_use, len(garments), guide_level)
                final_confidence = base_confidence * confidence_multiplier * 0.6  # Overall lower confidence for neck
                
                body_measurements.append({
                    'measurement': body_estimate_combined,
                    'garment_measurement': garment_neck,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'feedback_delta': neck_feedback_delta,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label,
                    'confidence': final_confidence
                })
            
            if not body_measurements:
                return None
            
            estimated_neck = self._calculate_confidence_weighted_average(body_measurements)
            
            self.logger.info(f"Estimated neck measurement for user {user_id}: {estimated_neck:.1f}\". "
                           f"Based on {specific_feedback_count} specific + {inferred_feedback_count} inferred feedback points.")
            self.logger.warning(f"NOTE: Neck estimates are less reliable than chest estimates. "
                              f"Garment neck measurements ≠ body neck circumference.")
            
            cursor.close()
            conn.close()
            
            return estimated_neck
            
        except Exception as e:
            self.logger.error(f"Error estimating neck measurement for user {user_id}: {str(e)}")
            return None

    def estimate_sleeve_measurement(self, user_id: int) -> Optional[float]:
        """
        Estimate sleeve measurement using both specific sleeve feedback AND inferring from overall fit.
        If user rates a garment "Good Fit" overall, we assume the sleeve is also acceptable.
        Note: This estimates garment sleeve length preference, not body arm measurements.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query for garments with sleeve measurements and EITHER sleeve feedback OR overall "Good Fit"
            query = """
                SELECT 
                    b.name as brand,
                    ug.product_name,
                    ug.size_label,
                    sge.sleeve_min,
                    sge.sleeve_max,
                    sge.sleeve_range,
                    sg.guide_level,
                    sleeve_fc.feedback_text as sleeve_feedback,
                    overall_fc.feedback_text as overall_feedback,
                    CASE 
                        WHEN sleeve_fc.feedback_text IS NOT NULL THEN 'specific'
                        WHEN overall_fc.feedback_text = 'Good Fit' THEN 'inferred'
                        ELSE 'none'
                    END as feedback_source
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                LEFT JOIN size_guides sg ON sge.size_guide_id = sg.id
                -- Get specific sleeve feedback
                LEFT JOIN user_garment_feedback sleeve_ugf ON ug.id = sleeve_ugf.user_garment_id AND sleeve_ugf.dimension = 'sleeve'
                LEFT JOIN feedback_codes sleeve_fc ON sleeve_ugf.feedback_code_id = sleeve_fc.id
                -- Get overall feedback
                LEFT JOIN user_garment_feedback overall_ugf ON ug.id = overall_ugf.user_garment_id AND overall_ugf.dimension = 'overall'
                LEFT JOIN feedback_codes overall_fc ON overall_ugf.feedback_code_id = overall_fc.id
                WHERE ug.user_id = %s 
                AND ug.owns_garment = true
                AND (sge.sleeve_min IS NOT NULL OR sge.sleeve_max IS NOT NULL OR sge.sleeve_range IS NOT NULL)
                AND (sleeve_fc.feedback_text IS NOT NULL OR overall_fc.feedback_text = 'Good Fit')
                ORDER BY 
                    CASE WHEN sleeve_fc.feedback_text IS NOT NULL THEN 1 ELSE 2 END, -- Prioritize specific feedback
                    ug.created_at DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            
            if not garments:
                self.logger.info(f"No garments with sleeve measurements and feedback found for user {user_id}")
                return None
            
            specific_feedback_count = len([g for g in garments if g[7] is not None])  # sleeve_feedback IS NOT NULL
            inferred_feedback_count = len(garments) - specific_feedback_count
            
            self.logger.info(f"Found {len(garments)} garments with sleeve measurements for user {user_id}:")
            self.logger.info(f"  - {specific_feedback_count} with specific sleeve feedback")
            self.logger.info(f"  - {inferred_feedback_count} inferred from overall 'Good Fit'")
            
            # Process each garment
            sleeve_measurements = []
            for garment in garments:
                (brand, product_name, size_label, sleeve_min, sleeve_max, sleeve_range, 
                 guide_level, sleeve_feedback, overall_feedback, feedback_source) = garment
                
                garment_sleeve = self._parse_measurement(sleeve_min, sleeve_max, sleeve_range)
                if garment_sleeve is None:
                    continue
                
                # Determine which feedback to use and confidence adjustment
                if feedback_source == 'specific':
                    # Use specific sleeve feedback with full confidence
                    feedback_to_use = sleeve_feedback
                    confidence_multiplier = 1.0
                    self.logger.info(f"  {brand} {size_label}: Using SPECIFIC sleeve feedback '{sleeve_feedback}'")
                elif feedback_source == 'inferred':
                    # Infer "Good Fit" for sleeve from overall feedback, but with lower confidence
                    feedback_to_use = "Good Fit"
                    confidence_multiplier = 0.7  # Lower confidence for inferred feedback
                    self.logger.info(f"  {brand} {size_label}: INFERRED sleeve fit from overall 'Good Fit'")
                else:
                    continue
                
                # For sleeve length preference, use feedback deltas
                sleeve_feedback_delta = self.FEEDBACK_DELTAS.get(feedback_to_use, 0.0)
                
                # Also use ease-based conversion (though less applicable for sleeve length)
                if feedback_to_use == "Good Fit":
                    fit_type = 'regular_fit'
                elif feedback_to_use in ["Tight but I Like It", "Too Tight"]:
                    fit_type = 'tight_fit'
                elif feedback_to_use in ["Loose but I Like It", "Slightly Loose"]:
                    fit_type = 'loose_fit'
                else:
                    fit_type = 'regular_fit'
                
                # For sleeve, the ease conversion is less meaningful, so we weight feedback more heavily
                sleeve_estimate_feedback = garment_sleeve + sleeve_feedback_delta
                sleeve_estimate_ease = self.garment_to_body_measurement(garment_sleeve, fit_type)
                
                # Weight the feedback method much more heavily for sleeve since ease is not very applicable
                sleeve_estimate_combined = (sleeve_estimate_feedback * 0.8 + sleeve_estimate_ease * 0.2)
                
                base_confidence = self._calculate_confidence(feedback_to_use, len(garments), guide_level)
                final_confidence = base_confidence * confidence_multiplier * 0.8  # Moderate confidence for sleeve
                
                sleeve_measurements.append({
                    'measurement': sleeve_estimate_combined,
                    'garment_measurement': garment_sleeve,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'feedback_delta': sleeve_feedback_delta,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label,
                    'confidence': final_confidence
                })
            
            if not sleeve_measurements:
                return None
            
            estimated_sleeve = self._calculate_confidence_weighted_average(sleeve_measurements)
            
            self.logger.info(f"Estimated sleeve length preference for user {user_id}: {estimated_sleeve:.1f}\". "
                           f"Based on {specific_feedback_count} specific + {inferred_feedback_count} inferred feedback points.")
            self.logger.info(f"NOTE: This represents preferred garment sleeve length, not body arm measurements.")
            
            cursor.close()
            conn.close()
            
            return estimated_sleeve
            
        except Exception as e:
            self.logger.error(f"Error estimating sleeve measurement for user {user_id}: {str(e)}")
            return None
    
    def _parse_measurement(self, min_val: Optional[float], max_val: Optional[float], range_str: Optional[str]) -> Optional[float]:
        """Parse measurement to get average value"""
        try:
            if min_val is not None and max_val is not None:
                return (float(min_val) + float(max_val)) / 2
            elif range_str is not None:
                if '-' in range_str:
                    parts = range_str.split('-')
                    min_part = float(parts[0].strip())
                    max_part = float(parts[1].strip())
                    return (min_part + max_part) / 2
                else:
                    return float(range_str.strip())
            elif min_val is not None:
                return float(min_val)
            elif max_val is not None:
                return float(max_val)
            else:
                return None
        except (ValueError, IndexError):
            return None
    
    def _calculate_confidence(self, feedback: str, total_measurements: int, guide_level: Optional[str]) -> float:
        """Calculate confidence score based on feedback type, data quantity, and size guide specificity"""
        # Base confidence based on feedback reliability
        feedback_confidence = {
            "Good Fit": 1.0,
            "Tight but I Like It": 0.9,
            "Loose but I Like It": 0.9,
            "Too Tight": 0.8,
            "Too Loose": 0.8,
            "Slightly Loose": 0.7,
            "Slightly Tight": 0.7
        }.get(feedback, 0.5)
        
        # Adjust based on total data points available
        data_confidence = min(1.0, total_measurements / 5.0)  # Max confidence with 5+ measurements
        
        # Adjust based on size guide specificity
        if guide_level == 'product_level':
            guide_adjustment = 1.2 # More specific guides have higher confidence
        elif guide_level == 'category_level':
            guide_adjustment = 1.0
        elif guide_level == 'brand_level':
            guide_adjustment = 0.8
        else:
            guide_adjustment = 0.6
            
        return feedback_confidence * data_confidence * guide_adjustment
    
    def _calculate_confidence_weighted_average(self, measurements: List[Dict]) -> float:
        """Calculate weighted average based on confidence scores"""
        if not measurements:
            return 0.0
        
        total_weighted_sum = 0.0
        total_weight = 0.0
        
        for measurement in measurements:
            weight = measurement['confidence']
            value = measurement['measurement']
            total_weighted_sum += value * weight
            total_weight += weight
        
        if total_weight == 0:
            return sum(m['measurement'] for m in measurements) / len(measurements)
        
        return total_weighted_sum / total_weight

    # Deprecated methods for backwards compatibility
    def _parse_chest_measurement(self, chest_min: Optional[float], chest_max: Optional[float], chest_range: Optional[str]) -> Optional[float]:
        """Deprecated: Use _parse_measurement instead"""
        return self._parse_measurement(chest_min, chest_max, chest_range)
    
    def _categorize_fit(self, feedback: str) -> Optional[str]:
        """Deprecated: Old categorization method"""
        if not feedback:
            return None
        feedback_lower = feedback.lower()
        if any(word in feedback_lower for word in ['too tight', 'tight but i like it', 'slightly tight']):
            return 'tight'
        elif any(word in feedback_lower for word in ['good fit', 'perfect']):
            return 'good'
        elif any(word in feedback_lower for word in ['loose', 'relaxed', 'comfortable', 'too loose', 'slightly loose', 'loose but i like it']):
            return 'relaxed'
        else:
            return None
    
    def _calculate_weighted_average(self, fit_groups: Dict[str, List[float]]) -> float:
        """Deprecated: Old weighted average method"""
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