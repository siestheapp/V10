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
    
    def estimate_chest_measurement(self, user_id: int) -> Optional[dict]:
        """
        Estimate body chest circumference from garment chest measurements.
        This converts garment chest measurements to body chest measurements that match what a tailor would measure.
        Returns both the estimate and detailed breakdown of garments used.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user's garments with chest measurements and fit feedback (most recent feedback only)
            query = """
                WITH latest_feedback AS (
                    SELECT 
                        ug.id as user_garment_id,
                        b.name as brand,
                        ug.product_name,
                        ug.size_label,
                        ug.owns_garment,
                        sge.chest_min,
                        sge.chest_max,
                        sge.chest_range,
                        sg.guide_level,
                        ugf.dimension,
                        fc.feedback_text as feedback,
                        ugf.created_at as feedback_date,
                        ROW_NUMBER() OVER (PARTITION BY ug.id, ugf.dimension ORDER BY ugf.created_at DESC) as rn
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
                )
                SELECT 
                    brand, product_name, size_label, owns_garment, 
                    chest_min, chest_max, chest_range, guide_level, dimension, feedback, feedback_date
                FROM latest_feedback 
                WHERE rn = 1
                ORDER BY user_garment_id DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            
            if not garments:
                self.logger.info(f"No garments with chest measurements found for user {user_id}")
                return None
            
            self.logger.info(f"Found {len(garments)} garments with chest measurements for user {user_id}")
            
            # Process each garment to calculate estimated body measurement
            body_measurements = []
            garment_details = []
            
            for garment in garments:
                brand, product_name, size_label, owns_garment, chest_min, chest_max, chest_range, guide_level, dimension, feedback, feedback_date = garment
                
                # Parse garment chest measurement
                garment_chest = self._parse_measurement(chest_min, chest_max, chest_range)
                if garment_chest is None:
                    continue
                
                # Create detailed entry for transparency
                chest_range_display = ""
                if chest_min is not None and chest_max is not None:
                    if chest_min == chest_max:
                        chest_range_display = f"{chest_min}\""
                    else:
                        chest_range_display = f"{chest_min}-{chest_max}\""
                elif chest_range:
                    chest_range_display = chest_range
                else:
                    chest_range_display = f"{garment_chest}\""
                
                garment_details.append({
                    'brand': brand,
                    'product_name': product_name or "Unknown Product",
                    'size': size_label,
                    'measurement_display': chest_range_display,
                    'feedback': feedback or "No feedback",
                    'guide_level': guide_level or "unknown",
                    'feedback_date': feedback_date.isoformat() if feedback_date else None
                })
                
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
            
            self.logger.info(f"Final estimated body chest circumference for user {user_id}: {estimated_chest:.1f}\"")
            self.logger.info(f"NOTE: This represents body chest circumference that a tailor would measure.")
            
            cursor.close()
            conn.close()
            
            return {
                'estimate': estimated_chest,
                'garment_details': garment_details,
                'data_points': len(garment_details)
            }
            
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
    
    def estimate_neck_measurement(self, user_id: int) -> Optional[dict]:
        """
        Estimate body neck circumference from garment neck measurements.
        This converts garment neck openings to body neck measurements that match what a tailor would measure.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query for garments with neck measurements and EITHER neck feedback OR overall "Good Fit" (deduplicated)
            query = """
                WITH latest_feedback AS (
                    SELECT 
                        ug.id as user_garment_id,
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
                        END as feedback_source,
                        COALESCE(neck_ugf.created_at, overall_ugf.created_at) as feedback_date,
                        ROW_NUMBER() OVER (PARTITION BY ug.id ORDER BY 
                            CASE WHEN neck_fc.feedback_text IS NOT NULL THEN 1 ELSE 2 END,
                            COALESCE(neck_ugf.created_at, overall_ugf.created_at) DESC
                        ) as rn
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
                )
                SELECT 
                    brand, product_name, size_label, neck_min, neck_max, neck_range, 
                    guide_level, neck_feedback, overall_feedback, feedback_source, feedback_date
                FROM latest_feedback 
                WHERE rn = 1
                ORDER BY 
                    CASE WHEN neck_feedback IS NOT NULL THEN 1 ELSE 2 END,
                    user_garment_id DESC
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
            
            # Process each garment to estimate body neck circumference
            body_neck_measurements = []
            garment_details = []
            for garment in garments:
                (brand, product_name, size_label, neck_min, neck_max, neck_range, 
                 guide_level, neck_feedback, overall_feedback, feedback_source, feedback_date) = garment
                
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
                
                # CONVERSION TO BODY NECK CIRCUMFERENCE:
                # Garment neck openings are designed to fit over the head, so they're typically
                # 2-3" larger than body neck circumference for dress shirts
                
                neck_ease = 2.5  # Standard ease between garment neck opening and body neck
                
                # Adjust ease based on feedback about fit
                if feedback_to_use == "Too Tight" or feedback_to_use == "Tight but I Like It":
                    # If neck feels tight, garment opening is closer to body size
                    adjusted_ease = neck_ease - 0.75
                elif feedback_to_use == "Too Loose" or feedback_to_use == "Loose but I Like It":
                    # If neck feels loose, garment opening is much larger than body
                    adjusted_ease = neck_ease + 0.75
                elif feedback_to_use == "Slightly Loose":
                    adjusted_ease = neck_ease + 0.25
                else:  # Good Fit
                    adjusted_ease = neck_ease
                
                # Create detailed entry for transparency
                neck_range_display = ""
                if neck_min is not None and neck_max is not None:
                    if neck_min == neck_max:
                        neck_range_display = f"{neck_min}\""
                    else:
                        neck_range_display = f"{neck_min}-{neck_max}\""
                elif neck_range:
                    neck_range_display = neck_range
                else:
                    neck_range_display = f"{garment_neck}\""
                
                garment_details.append({
                    'brand': brand,
                    'product_name': product_name or "Unknown Product", 
                    'size': size_label,
                    'measurement_display': neck_range_display,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'guide_level': guide_level or "unknown",
                    'feedback_date': feedback_date.isoformat() if feedback_date else None
                })
                
                # Calculate body neck circumference: Garment neck - ease
                body_neck_estimate = garment_neck - adjusted_ease
                
                base_confidence = self._calculate_confidence(feedback_to_use, len(garments), guide_level)
                final_confidence = base_confidence * confidence_multiplier * 0.7  # Lower confidence for neck conversion
                
                body_neck_measurements.append({
                    'measurement': body_neck_estimate,
                    'garment_neck': garment_neck,
                    'neck_ease': adjusted_ease,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label,
                    'confidence': final_confidence
                })
                
                self.logger.info(f"    Garment neck: {garment_neck}\", Ease: {adjusted_ease}\", "
                               f"Body neck estimate: {body_neck_estimate:.1f}\"")
            
            if not body_neck_measurements:
                return None
            
            estimated_neck = self._calculate_confidence_weighted_average(body_neck_measurements)
            
            self.logger.info(f"Estimated body neck circumference for user {user_id}: {estimated_neck:.1f}\". "
                           f"Based on {specific_feedback_count} specific + {inferred_feedback_count} inferred feedback points.")
            self.logger.info(f"NOTE: This represents body neck circumference that a tailor would measure.")
            
            cursor.close()
            conn.close()
            
            return {
                'estimate': estimated_neck,
                'garment_details': garment_details,
                'data_points': len(garment_details)
            }
            
        except Exception as e:
            self.logger.error(f"Error estimating neck measurement for user {user_id}: {str(e)}")
            return None

    def estimate_sleeve_measurement(self, user_id: int) -> Optional[dict]:
        """
        Estimate body arm length (shoulder to wrist) from garment sleeve measurements.
        This converts garment sleeve lengths to body arm measurements that match what a tailor would measure.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query for garments with sleeve measurements and EITHER sleeve feedback OR overall "Good Fit" (deduplicated)
            query = """
                WITH latest_feedback AS (
                    SELECT 
                        ug.id as user_garment_id,
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
                        END as feedback_source,
                        COALESCE(sleeve_ugf.created_at, overall_ugf.created_at) as feedback_date,
                        ROW_NUMBER() OVER (PARTITION BY ug.id ORDER BY 
                            CASE WHEN sleeve_fc.feedback_text IS NOT NULL THEN 1 ELSE 2 END,
                            COALESCE(sleeve_ugf.created_at, overall_ugf.created_at) DESC
                        ) as rn
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
                )
                SELECT 
                    brand, product_name, size_label, sleeve_min, sleeve_max, sleeve_range,
                    guide_level, sleeve_feedback, overall_feedback, feedback_source, feedback_date
                FROM latest_feedback 
                WHERE rn = 1
                ORDER BY 
                    CASE WHEN sleeve_feedback IS NOT NULL THEN 1 ELSE 2 END,
                    user_garment_id DESC
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
            
            # Process each garment to estimate body arm length
            body_arm_measurements = []
            garment_details = []
            for garment in garments:
                (brand, product_name, size_label, sleeve_min, sleeve_max, sleeve_range, 
                 guide_level, sleeve_feedback, overall_feedback, feedback_source, feedback_date) = garment
                
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
                
                # CONVERSION TO BODY ARM LENGTH:
                # For "Good Fit" sleeves, subtract typical sleeve ease (1.5-2")
                # Adjust based on feedback about length preference
                
                sleeve_ease = 1.75  # Standard sleeve ease for arm length conversion
                
                # Adjust ease based on feedback
                if feedback_to_use == "Too Tight" or feedback_to_use == "Tight but I Like It":
                    # If sleeve feels tight/short, they prefer longer sleeves, so less ease
                    adjusted_ease = sleeve_ease - 0.5
                elif feedback_to_use == "Too Loose" or feedback_to_use == "Loose but I Like It":
                    # If sleeve feels loose/long, they prefer shorter sleeves, so more ease
                    adjusted_ease = sleeve_ease + 0.5
                elif feedback_to_use == "Slightly Loose":
                    adjusted_ease = sleeve_ease + 0.25
                else:  # Good Fit
                    adjusted_ease = sleeve_ease
                
                # Create detailed entry for transparency
                sleeve_range_display = ""
                if sleeve_min is not None and sleeve_max is not None:
                    if sleeve_min == sleeve_max:
                        sleeve_range_display = f"{sleeve_min}\""
                    else:
                        sleeve_range_display = f"{sleeve_min}-{sleeve_max}\""
                elif sleeve_range:
                    sleeve_range_display = sleeve_range
                else:
                    sleeve_range_display = f"{garment_sleeve}\""
                
                garment_details.append({
                    'brand': brand,
                    'product_name': product_name or "Unknown Product",
                    'size': size_label,
                    'measurement_display': sleeve_range_display,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'guide_level': guide_level or "unknown",
                    'feedback_date': feedback_date.isoformat() if feedback_date else None
                })
                
                # Calculate body arm length: Garment sleeve - ease
                body_arm_estimate = garment_sleeve - adjusted_ease
                
                base_confidence = self._calculate_confidence(feedback_to_use, len(garments), guide_level)
                final_confidence = base_confidence * confidence_multiplier
                
                body_arm_measurements.append({
                    'measurement': body_arm_estimate,
                    'garment_sleeve': garment_sleeve,
                    'sleeve_ease': adjusted_ease,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label,
                    'confidence': final_confidence
                })
                
                self.logger.info(f"    Garment sleeve: {garment_sleeve}\", Ease: {adjusted_ease}\", "
                               f"Body arm estimate: {body_arm_estimate:.1f}\"")
            
            if not body_arm_measurements:
                return None
            
            estimated_arm_length = self._calculate_confidence_weighted_average(body_arm_measurements)
            
            self.logger.info(f"Estimated body arm length for user {user_id}: {estimated_arm_length:.1f}\". "
                           f"Based on {specific_feedback_count} specific + {inferred_feedback_count} inferred feedback points.")
            self.logger.info(f"NOTE: This represents body arm length (shoulder to wrist) that a tailor would measure.")
            
            cursor.close()
            conn.close()
            
            return {
                'estimate': estimated_arm_length,
                'garment_details': garment_details,
                'data_points': len(garment_details)
            }
            
        except Exception as e:
            self.logger.error(f"Error estimating arm length for user {user_id}: {str(e)}")
            return None
    
    def estimate_waist_measurement(self, user_id: int) -> Optional[dict]:
        """
        Estimate body waist circumference from garment waist measurements.
        This converts garment waist measurements to body waist measurements that match what a tailor would measure.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query for garments with waist measurements and EITHER waist feedback OR overall "Good Fit" (deduplicated)
            query = """
                WITH latest_feedback AS (
                    SELECT 
                        ug.id as user_garment_id,
                        b.name as brand,
                        ug.product_name,
                        ug.size_label,
                        sge.waist_min,
                        sge.waist_max,
                        sge.waist_range,
                        sg.guide_level,
                        waist_fc.feedback_text as waist_feedback,
                        overall_fc.feedback_text as overall_feedback,
                        CASE 
                            WHEN waist_fc.feedback_text IS NOT NULL THEN 'specific'
                            WHEN overall_fc.feedback_text = 'Good Fit' THEN 'inferred'
                            ELSE 'none'
                        END as feedback_source,
                        COALESCE(waist_ugf.created_at, overall_ugf.created_at) as feedback_date,
                        ROW_NUMBER() OVER (PARTITION BY ug.id ORDER BY 
                            CASE WHEN waist_fc.feedback_text IS NOT NULL THEN 1 ELSE 2 END,
                            COALESCE(waist_ugf.created_at, overall_ugf.created_at) DESC
                        ) as rn
                    FROM user_garments ug
                    JOIN brands b ON ug.brand_id = b.id
                    LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                    LEFT JOIN size_guides sg ON sge.size_guide_id = sg.id
                    -- Get specific waist feedback
                    LEFT JOIN user_garment_feedback waist_ugf ON ug.id = waist_ugf.user_garment_id AND waist_ugf.dimension = 'waist'
                    LEFT JOIN feedback_codes waist_fc ON waist_ugf.feedback_code_id = waist_fc.id
                    -- Get overall feedback
                    LEFT JOIN user_garment_feedback overall_ugf ON ug.id = overall_ugf.user_garment_id AND overall_ugf.dimension = 'overall'
                    LEFT JOIN feedback_codes overall_fc ON overall_ugf.feedback_code_id = overall_fc.id
                    WHERE ug.user_id = %s 
                    AND ug.owns_garment = true
                    AND (sge.waist_min IS NOT NULL OR sge.waist_max IS NOT NULL OR sge.waist_range IS NOT NULL)
                    AND (waist_fc.feedback_text IS NOT NULL OR overall_fc.feedback_text = 'Good Fit')
                )
                SELECT 
                    brand, product_name, size_label, waist_min, waist_max, waist_range, 
                    guide_level, waist_feedback, overall_feedback, feedback_source, feedback_date
                FROM latest_feedback 
                WHERE rn = 1
                ORDER BY 
                    CASE WHEN waist_feedback IS NOT NULL THEN 1 ELSE 2 END,
                    user_garment_id DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            
            if not garments:
                self.logger.info(f"No garments with waist measurements and feedback found for user {user_id}")
                return None
            
            specific_feedback_count = len([g for g in garments if g[7] is not None])  # waist_feedback IS NOT NULL
            inferred_feedback_count = len(garments) - specific_feedback_count
            
            self.logger.info(f"Found {len(garments)} garments with waist measurements for user {user_id}:")
            self.logger.info(f"  - {specific_feedback_count} with specific waist feedback")
            self.logger.info(f"  - {inferred_feedback_count} inferred from overall 'Good Fit'")
            
            # Process each garment to estimate body waist circumference
            body_waist_measurements = []
            garment_details = []
            for garment in garments:
                (brand, product_name, size_label, waist_min, waist_max, waist_range, 
                 guide_level, waist_feedback, overall_feedback, feedback_source, feedback_date) = garment
                
                garment_waist = self._parse_measurement(waist_min, waist_max, waist_range)
                if garment_waist is None:
                    continue
                
                # Determine which feedback to use and confidence adjustment
                if feedback_source == 'specific':
                    # Use specific waist feedback with full confidence
                    feedback_to_use = waist_feedback
                    confidence_multiplier = 1.0
                    self.logger.info(f"  {brand} {size_label}: Using SPECIFIC waist feedback '{waist_feedback}'")
                elif feedback_source == 'inferred':
                    # Infer "Good Fit" for waist from overall feedback, but with lower confidence
                    feedback_to_use = "Good Fit"
                    confidence_multiplier = 0.7  # Lower confidence for inferred feedback
                    self.logger.info(f"  {brand} {size_label}: INFERRED waist fit from overall 'Good Fit'")
                else:
                    continue
                
                # CONVERSION TO BODY WAIST CIRCUMFERENCE:
                # Garment waist measurements need ease for comfort
                
                waist_ease = 1.5  # Standard waist ease for comfort
                
                # Adjust ease based on feedback about fit
                if feedback_to_use == "Too Tight" or feedback_to_use == "Tight but I Like It":
                    # If waist feels tight, garment is closer to body size
                    adjusted_ease = waist_ease - 0.5
                elif feedback_to_use == "Too Loose" or feedback_to_use == "Loose but I Like It":
                    # If waist feels loose, garment is much larger than body
                    adjusted_ease = waist_ease + 1.0
                elif feedback_to_use == "Slightly Loose":
                    adjusted_ease = waist_ease + 0.5
                else:  # Good Fit
                    adjusted_ease = waist_ease
                
                # Create detailed entry for transparency
                waist_range_display = ""
                if waist_min is not None and waist_max is not None:
                    if waist_min == waist_max:
                        waist_range_display = f"{waist_min}\""
                    else:
                        waist_range_display = f"{waist_min}-{waist_max}\""
                elif waist_range:
                    waist_range_display = waist_range
                else:
                    waist_range_display = f"{garment_waist}\""
                
                garment_details.append({
                    'brand': brand,
                    'product_name': product_name or "Unknown Product",
                    'size': size_label,
                    'measurement_display': waist_range_display,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'guide_level': guide_level or "unknown",
                    'feedback_date': feedback_date.isoformat() if feedback_date else None
                })
                
                # Calculate body waist circumference: Garment waist - ease
                body_waist_estimate = garment_waist - adjusted_ease
                
                base_confidence = self._calculate_confidence(feedback_to_use, len(garments), guide_level)
                final_confidence = base_confidence * confidence_multiplier
                
                body_waist_measurements.append({
                    'measurement': body_waist_estimate,
                    'garment_waist': garment_waist,
                    'waist_ease': adjusted_ease,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label,
                    'confidence': final_confidence
                })
                
                self.logger.info(f"    Garment waist: {garment_waist}\", Ease: {adjusted_ease}\", "
                               f"Body waist estimate: {body_waist_estimate:.1f}\"")
            
            if not body_waist_measurements:
                return None
            
            estimated_waist = self._calculate_confidence_weighted_average(body_waist_measurements)
            
            self.logger.info(f"Estimated body waist circumference for user {user_id}: {estimated_waist:.1f}\". "
                           f"Based on {specific_feedback_count} specific + {inferred_feedback_count} inferred feedback points.")
            self.logger.info(f"NOTE: This represents body waist circumference that a tailor would measure.")
            
            cursor.close()
            conn.close()
            
            return {
                'estimate': estimated_waist,
                'garment_details': garment_details,
                'data_points': len(garment_details)
            }
            
        except Exception as e:
            self.logger.error(f"Error estimating waist measurement for user {user_id}: {str(e)}")
            return None

    def estimate_hip_measurement(self, user_id: int) -> Optional[dict]:
        """
        Estimate body hip circumference from garment hip measurements.
        This converts garment hip measurements to body hip measurements that match what a tailor would measure.
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query for garments with hip measurements and EITHER hip feedback OR overall "Good Fit" (deduplicated)
            query = """
                WITH latest_feedback AS (
                    SELECT 
                        ug.id as user_garment_id,
                        b.name as brand,
                        ug.product_name,
                        ug.size_label,
                        sge.hip_min,
                        sge.hip_max,
                        sge.hip_range,
                        sg.guide_level,
                        hip_fc.feedback_text as hip_feedback,
                        overall_fc.feedback_text as overall_feedback,
                        CASE 
                            WHEN hip_fc.feedback_text IS NOT NULL THEN 'specific'
                            WHEN overall_fc.feedback_text = 'Good Fit' THEN 'inferred'
                            ELSE 'none'
                        END as feedback_source,
                        COALESCE(hip_ugf.created_at, overall_ugf.created_at) as feedback_date,
                        ROW_NUMBER() OVER (PARTITION BY ug.id ORDER BY 
                            CASE WHEN hip_fc.feedback_text IS NOT NULL THEN 1 ELSE 2 END,
                            COALESCE(hip_ugf.created_at, overall_ugf.created_at) DESC
                        ) as rn
                    FROM user_garments ug
                    JOIN brands b ON ug.brand_id = b.id
                    LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                    LEFT JOIN size_guides sg ON sge.size_guide_id = sg.id
                    -- Get specific hip feedback
                    LEFT JOIN user_garment_feedback hip_ugf ON ug.id = hip_ugf.user_garment_id AND hip_ugf.dimension = 'hip'
                    LEFT JOIN feedback_codes hip_fc ON hip_ugf.feedback_code_id = hip_fc.id
                    -- Get overall feedback
                    LEFT JOIN user_garment_feedback overall_ugf ON ug.id = overall_ugf.user_garment_id AND overall_ugf.dimension = 'overall'
                    LEFT JOIN feedback_codes overall_fc ON overall_ugf.feedback_code_id = overall_fc.id
                    WHERE ug.user_id = %s 
                    AND ug.owns_garment = true
                    AND (sge.hip_min IS NOT NULL OR sge.hip_max IS NOT NULL OR sge.hip_range IS NOT NULL)
                    AND (hip_fc.feedback_text IS NOT NULL OR overall_fc.feedback_text = 'Good Fit')
                )
                SELECT 
                    brand, product_name, size_label, hip_min, hip_max, hip_range, 
                    guide_level, hip_feedback, overall_feedback, feedback_source, feedback_date
                FROM latest_feedback 
                WHERE rn = 1
                ORDER BY 
                    CASE WHEN hip_feedback IS NOT NULL THEN 1 ELSE 2 END,
                    user_garment_id DESC
            """
            
            cursor.execute(query, (user_id,))
            garments = cursor.fetchall()
            
            if not garments:
                self.logger.info(f"No garments with hip measurements and feedback found for user {user_id}")
                return None
            
            specific_feedback_count = len([g for g in garments if g[7] is not None])  # hip_feedback IS NOT NULL
            inferred_feedback_count = len(garments) - specific_feedback_count
            
            self.logger.info(f"Found {len(garments)} garments with hip measurements for user {user_id}:")
            self.logger.info(f"  - {specific_feedback_count} with specific hip feedback")
            self.logger.info(f"  - {inferred_feedback_count} inferred from overall 'Good Fit'")
            
            # Process each garment to estimate body hip circumference
            body_hip_measurements = []
            garment_details = []
            for garment in garments:
                (brand, product_name, size_label, hip_min, hip_max, hip_range, 
                 guide_level, hip_feedback, overall_feedback, feedback_source, feedback_date) = garment
                
                garment_hip = self._parse_measurement(hip_min, hip_max, hip_range)
                if garment_hip is None:
                    continue
                
                # Determine which feedback to use and confidence adjustment
                if feedback_source == 'specific':
                    # Use specific hip feedback with full confidence
                    feedback_to_use = hip_feedback
                    confidence_multiplier = 1.0
                    self.logger.info(f"  {brand} {size_label}: Using SPECIFIC hip feedback '{hip_feedback}'")
                elif feedback_source == 'inferred':
                    # Infer "Good Fit" for hip from overall feedback, but with lower confidence
                    feedback_to_use = "Good Fit"
                    confidence_multiplier = 0.7  # Lower confidence for inferred feedback
                    self.logger.info(f"  {brand} {size_label}: INFERRED hip fit from overall 'Good Fit'")
                else:
                    continue
                
                # CONVERSION TO BODY HIP CIRCUMFERENCE:
                # Garment hip measurements need ease for movement
                
                hip_ease = 2.0  # Standard hip ease for comfort and movement
                
                # Adjust ease based on feedback about fit
                if feedback_to_use == "Too Tight" or feedback_to_use == "Tight but I Like It":
                    # If hip feels tight, garment is closer to body size
                    adjusted_ease = hip_ease - 0.5
                elif feedback_to_use == "Too Loose" or feedback_to_use == "Loose but I Like It":
                    # If hip feels loose, garment is much larger than body
                    adjusted_ease = hip_ease + 1.0
                elif feedback_to_use == "Slightly Loose":
                    adjusted_ease = hip_ease + 0.5
                else:  # Good Fit
                    adjusted_ease = hip_ease
                
                # Create detailed entry for transparency
                hip_range_display = ""
                if hip_min is not None and hip_max is not None:
                    if hip_min == hip_max:
                        hip_range_display = f"{hip_min}\""
                    else:
                        hip_range_display = f"{hip_min}-{hip_max}\""
                elif hip_range:
                    hip_range_display = hip_range
                else:
                    hip_range_display = f"{garment_hip}\""
                
                garment_details.append({
                    'brand': brand,
                    'product_name': product_name or "Unknown Product",
                    'size': size_label,
                    'measurement_display': hip_range_display,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'guide_level': guide_level or "unknown",
                    'feedback_date': feedback_date.isoformat() if feedback_date else None
                })
                
                # Calculate body hip circumference: Garment hip - ease
                body_hip_estimate = garment_hip - adjusted_ease
                
                base_confidence = self._calculate_confidence(feedback_to_use, len(garments), guide_level)
                final_confidence = base_confidence * confidence_multiplier * 0.8  # Lower confidence for hip conversion
                
                body_hip_measurements.append({
                    'measurement': body_hip_estimate,
                    'garment_hip': garment_hip,
                    'hip_ease': adjusted_ease,
                    'feedback': feedback_to_use,
                    'feedback_source': feedback_source,
                    'brand': brand,
                    'product': product_name,
                    'size': size_label,
                    'confidence': final_confidence
                })
                
                self.logger.info(f"    Garment hip: {garment_hip}\", Ease: {adjusted_ease}\", "
                               f"Body hip estimate: {body_hip_estimate:.1f}\"")
            
            if not body_hip_measurements:
                return None
            
            estimated_hip = self._calculate_confidence_weighted_average(body_hip_measurements)
            
            self.logger.info(f"Estimated body hip circumference for user {user_id}: {estimated_hip:.1f}\". "
                           f"Based on {specific_feedback_count} specific + {inferred_feedback_count} inferred feedback points.")
            self.logger.info(f"NOTE: This represents body hip circumference that a tailor would measure.")
            
            cursor.close()
            conn.close()
            
            return {
                'estimate': estimated_hip,
                'garment_details': garment_details,
                'data_points': len(garment_details)
            }
            
        except Exception as e:
            self.logger.error(f"Error estimating hip measurement for user {user_id}: {str(e)}")
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