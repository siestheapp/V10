"""
Multi-Dimensional Fit Analyzer
Expands beyond chest-only analysis to consider all available garment dimensions
(chest, neck, waist, sleeve, hip) for comprehensive size recommendations.
"""

import psycopg2
import statistics
import math
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass

@dataclass
class DimensionFitZone:
    """Represents fit zones for a single dimension"""
    tight_min: float
    tight_max: float
    good_min: float
    good_max: float
    relaxed_min: float
    relaxed_max: float
    dimension: str
    confidence: float
    data_points: int

@dataclass
class UserDimensionProfile:
    """User's measurement profile for a single dimension"""
    estimated_measurement: float
    confidence: float
    data_points: int
    garment_details: List[Dict]

@dataclass
class SizeRecommendation:
    """Comprehensive size recommendation with multi-dimensional analysis"""
    size_label: str
    overall_fit_score: float
    dimension_scores: Dict[str, Dict[str, Any]]  # dimension -> {fit_type, score, measurement, etc.}
    available_dimensions: List[str]
    confidence: float
    primary_concerns: List[str]  # Dimensions that might be problematic
    recommendation_reasoning: str

class MultiDimensionalFitAnalyzer:
    """
    Analyzes garment fit across all available dimensions (chest, neck, waist, sleeve, hip)
    to provide comprehensive size recommendations that consider the user's comfort
    in ALL measurement areas, not just chest.
    """
    
    # Available dimensions in order of importance for fit recommendations
    DIMENSIONS = ['chest', 'neck', 'waist', 'sleeve', 'hip']
    
    # Dimension importance weights for overall scoring
    DIMENSION_WEIGHTS = {
        'chest': 1.0,      # Most important for overall fit
        'waist': 0.9,      # Very important for comfort
        'neck': 0.8,       # Important for comfort, especially dress shirts
        'sleeve': 0.7,     # Important for appearance and comfort
        'hip': 0.6         # Less critical for most garments
    }
    
    # Fit type scoring (higher = better fit)
    FIT_SCORES = {
        'good': 1.0,
        'tight_acceptable': 0.8,  # "Tight but I Like It"
        'loose_acceptable': 0.8,  # "Loose but I Like It"  
        'tight_concerning': 0.4,  # "Too Tight"
        'loose_concerning': 0.4,  # "Too Loose"
        'no_data': 0.5           # No measurement available
    }

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def get_user_multi_dimensional_profile(self, user_id: int) -> Dict[str, UserDimensionProfile]:
        """
        Get user's estimated measurements across all dimensions
        
        Returns:
            Dict mapping dimension names to UserDimensionProfile objects
        """
        from body_measurement_estimator import BodyMeasurementEstimator
        
        estimator = BodyMeasurementEstimator(self.db_config)
        profile = {}
        
        # Get chest measurements
        chest_result = estimator.estimate_chest_measurement(user_id)
        if chest_result:
            profile['chest'] = UserDimensionProfile(
                estimated_measurement=chest_result['estimate'],
                confidence=0.9,  # High confidence for chest
                data_points=chest_result['data_points'],
                garment_details=chest_result['garment_details']
            )
        
        # Get neck measurements
        neck_result = estimator.estimate_neck_measurement(user_id)
        if neck_result:
            profile['neck'] = UserDimensionProfile(
                estimated_measurement=neck_result['estimate'],
                confidence=0.7,  # Lower confidence for neck conversion
                data_points=neck_result['data_points'],
                garment_details=neck_result['garment_details']
            )
        
        # Get sleeve/arm length measurements
        sleeve_result = estimator.estimate_sleeve_measurement(user_id)
        if sleeve_result:
            profile['sleeve'] = UserDimensionProfile(
                estimated_measurement=sleeve_result['estimate'],
                confidence=0.8,  # Good confidence for sleeve
                data_points=sleeve_result['data_points'],
                garment_details=sleeve_result['garment_details']
            )
        
        # Get waist measurements
        waist_result = estimator.estimate_waist_measurement(user_id)
        if waist_result:
            profile['waist'] = UserDimensionProfile(
                estimated_measurement=waist_result['estimate'],
                confidence=0.8,  # Good confidence for waist
                data_points=waist_result['data_points'],
                garment_details=waist_result['garment_details']
            )
        
        # Get hip measurements
        hip_result = estimator.estimate_hip_measurement(user_id)
        if hip_result:
            profile['hip'] = UserDimensionProfile(
                estimated_measurement=hip_result['estimate'],
                confidence=0.7,  # Lower confidence for hip conversion
                data_points=hip_result['data_points'],
                garment_details=hip_result['garment_details']
            )
        
        self.logger.info(f"Generated multi-dimensional profile for user {user_id}: {list(profile.keys())}")
        return profile

    def calculate_multi_dimensional_fit_zones(self, user_id: int) -> Dict[str, DimensionFitZone]:
        """
        Calculate fit zones for all available dimensions based on user's garment feedback
        
        Returns:
            Dict mapping dimension names to DimensionFitZone objects
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            fit_zones = {}
            
            for dimension in self.DIMENSIONS:
                self.logger.info(f"Calculating fit zones for dimension: {dimension}")
                
                # Get user's garments with measurements and feedback for this dimension
                query = f"""
                    WITH latest_feedback AS (
                        SELECT 
                            ug.id as user_garment_id,
                            b.name as brand,
                            ug.product_name,
                            ug.size_label,
                            sge.{dimension}_min,
                            sge.{dimension}_max,
                            sge.{dimension}_range,
                            fc.feedback_text as feedback,
                            ugf.created_at as feedback_date,
                            ROW_NUMBER() OVER (
                                PARTITION BY ug.id, ugf.dimension 
                                ORDER BY ugf.created_at DESC
                            ) as rn
                        FROM user_garments ug
                        JOIN brands b ON ug.brand_id = b.id
                        LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                        LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
                        LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                        WHERE ug.user_id = %s 
                        AND ug.owns_garment = true
                        AND (sge.{dimension}_min IS NOT NULL 
                             OR sge.{dimension}_max IS NOT NULL 
                             OR sge.{dimension}_range IS NOT NULL)
                        AND ugf.dimension = %s
                    )
                    SELECT 
                        brand, product_name, size_label, 
                        {dimension}_min, {dimension}_max, {dimension}_range,
                        feedback, feedback_date
                    FROM latest_feedback 
                    WHERE rn = 1
                    ORDER BY user_garment_id DESC
                """
                
                cursor.execute(query, (user_id, dimension))
                garments = cursor.fetchall()
                
                if not garments:
                    self.logger.info(f"No {dimension} measurements with feedback found for user {user_id}")
                    continue
                
                # Group measurements by feedback type
                fit_groups = {
                    'tight': [],
                    'good': [], 
                    'relaxed': []
                }
                
                for garment in garments:
                    (brand, product_name, size_label, dim_min, dim_max, dim_range, 
                     feedback, feedback_date) = garment
                    
                    # Parse measurement
                    measurement = self._parse_measurement(dim_min, dim_max, dim_range)
                    if measurement is None:
                        continue
                    
                    # Categorize feedback
                    fit_category = self._categorize_feedback(feedback)
                    if fit_category:
                        fit_groups[fit_category].append(measurement)
                
                # Calculate statistical zones
                zones = self._calculate_statistical_zones(fit_groups, dimension)
                if zones:
                    fit_zones[dimension] = zones
                    
            cursor.close()
            conn.close()
            
            self.logger.info(f"Calculated fit zones for dimensions: {list(fit_zones.keys())}")
            return fit_zones
            
        except Exception as e:
            self.logger.error(f"Error calculating multi-dimensional fit zones: {str(e)}")
            return {}

    def analyze_garment_multi_dimensional_fit(
        self, 
        user_profile: Dict[str, UserDimensionProfile],
        brand_name: str,
        size_guide_entry_data: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze how a specific garment size fits across all available dimensions
        
        Args:
            user_profile: User's estimated measurements per dimension
            brand_name: Brand name for context
            size_guide_entry_data: Dict with measurement data (chest_min, chest_max, etc.)
            
        Returns:
            Dict mapping dimensions to fit analysis results
        """
        dimension_analysis = {}
        
        for dimension in self.DIMENSIONS:
            # Check if this dimension has data
            min_key = f"{dimension}_min"
            max_key = f"{dimension}_max"
            range_key = f"{dimension}_range"
            
            if not any(key in size_guide_entry_data and size_guide_entry_data[key] is not None 
                      for key in [min_key, max_key, range_key]):
                continue
                
            # Parse garment measurement
            garment_measurement = self._parse_measurement(
                size_guide_entry_data.get(min_key),
                size_guide_entry_data.get(max_key), 
                size_guide_entry_data.get(range_key)
            )
            
            if garment_measurement is None:
                continue
            
            # Check if user has estimated measurement for this dimension
            if dimension not in user_profile:
                dimension_analysis[dimension] = {
                    'fit_type': 'no_user_data',
                    'score': self.FIT_SCORES['no_data'],
                    'garment_measurement': garment_measurement,
                    'user_measurement': None,
                    'explanation': f"No user data available for {dimension} measurement"
                }
                continue
            
            user_measurement = user_profile[dimension].estimated_measurement
            ease = garment_measurement - user_measurement
            
            # Determine fit type based on ease amount
            fit_type, score, explanation = self._analyze_dimension_fit(
                dimension, user_measurement, garment_measurement, ease
            )
            
            dimension_analysis[dimension] = {
                'fit_type': fit_type,
                'score': score,
                'garment_measurement': garment_measurement,
                'user_measurement': user_measurement,
                'ease': ease,
                'explanation': explanation,
                'user_confidence': user_profile[dimension].confidence
            }
        
        return dimension_analysis

    def get_comprehensive_size_recommendations(
        self, 
        user_id: int, 
        brand_name: str,
        category: str = "Shirts"
    ) -> List[SizeRecommendation]:
        """
        Get comprehensive size recommendations considering all available dimensions
        
        Args:
            user_id: User ID
            brand_name: Brand name
            category: Garment category (default: "Shirts")
            
        Returns:
            List of SizeRecommendation objects sorted by overall fit score
        """
        try:
            # Get user's multi-dimensional profile
            user_profile = self.get_user_multi_dimensional_profile(user_id)
            
            if not user_profile:
                self.logger.warning(f"No user profile data available for user {user_id}")
                return []
            
            # Get brand's size guide data
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    sge.size_label,
                    sge.chest_min, sge.chest_max, sge.chest_range,
                    sge.neck_min, sge.neck_max, sge.neck_range,
                    sge.waist_min, sge.waist_max, sge.waist_range,
                    sge.sleeve_min, sge.sleeve_max, sge.sleeve_range,
                    sge.hip_min, sge.hip_max, sge.hip_range,
                    sge.center_back_length
                FROM size_guide_entries sge
                JOIN size_guides sg ON sge.size_guide_id = sg.id
                JOIN brands b ON sg.brand_id = b.id
                JOIN categories c ON sg.category_id = c.id
                WHERE b.name = %s AND c.name = %s
                ORDER BY 
                    CASE sge.size_label
                        WHEN 'XS' THEN 1
                        WHEN 'S' THEN 2
                        WHEN 'M' THEN 3
                        WHEN 'L' THEN 4
                        WHEN 'XL' THEN 5
                        WHEN 'XXL' THEN 6
                        ELSE 7
                    END
            """, (brand_name, category))
            
            size_entries = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not size_entries:
                self.logger.warning(f"No size guide found for {brand_name} {category}")
                return []
            
            recommendations = []
            
            for size_entry in size_entries:
                # Convert to dict for easier handling
                size_data = dict(zip([
                    'size_label', 'chest_min', 'chest_max', 'chest_range',
                    'neck_min', 'neck_max', 'neck_range',
                    'waist_min', 'waist_max', 'waist_range', 
                    'sleeve_min', 'sleeve_max', 'sleeve_range',
                    'hip_min', 'hip_max', 'hip_range', 'center_back_length'
                ], size_entry))
                
                # Analyze fit across all dimensions
                dimension_analysis = self.analyze_garment_multi_dimensional_fit(
                    user_profile, brand_name, size_data
                )
                
                if not dimension_analysis:
                    continue
                
                # Calculate overall fit score
                overall_score, primary_concerns = self._calculate_overall_fit_score(dimension_analysis)
                
                # Determine available dimensions
                available_dimensions = list(dimension_analysis.keys())
                
                # Generate recommendation reasoning
                reasoning = self._generate_recommendation_reasoning(
                    dimension_analysis, available_dimensions, primary_concerns
                )
                
                recommendations.append(SizeRecommendation(
                    size_label=size_data['size_label'],
                    overall_fit_score=overall_score,
                    dimension_scores=dimension_analysis,
                    available_dimensions=available_dimensions,
                    confidence=self._calculate_recommendation_confidence(dimension_analysis, user_profile),
                    primary_concerns=primary_concerns,
                    recommendation_reasoning=reasoning
                ))
            
            # Sort by overall fit score (best first)
            recommendations.sort(key=lambda x: x.overall_fit_score, reverse=True)
            
            self.logger.info(f"Generated {len(recommendations)} comprehensive size recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive size recommendations: {str(e)}")
            return []

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

    def _categorize_feedback(self, feedback: str) -> Optional[str]:
        """Categorize feedback into fit groups"""
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

    def _calculate_statistical_zones(self, fit_groups: Dict[str, List[float]], dimension: str) -> Optional[DimensionFitZone]:
        """Calculate statistical fit zones for a dimension"""
        try:
            # Need at least some data to calculate zones
            all_measurements = []
            for measurements in fit_groups.values():
                all_measurements.extend(measurements)
            
            if len(all_measurements) < 2:
                return None
            
            # Calculate center and spread
            center = statistics.mean(all_measurements)
            std = statistics.stdev(all_measurements) if len(all_measurements) > 1 else 1.0
            
            # Create zones based on statistical distribution
            return DimensionFitZone(
                tight_min=center - 2*std,
                tight_max=center - 0.5*std,
                good_min=center - 0.5*std,
                good_max=center + 0.5*std,
                relaxed_min=center + 0.5*std,
                relaxed_max=center + 2*std,
                dimension=dimension,
                confidence=0.8,  # Default confidence
                data_points=len(all_measurements)
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating statistical zones for {dimension}: {str(e)}")
            return None

    def _analyze_dimension_fit(self, dimension: str, user_measurement: float, garment_measurement: float, ease: float) -> Tuple[str, float, str]:
        """Analyze fit for a specific dimension"""
        
        # Dimension-specific fit criteria
        if dimension == 'chest':
            if ease < 0:
                return 'tight_concerning', self.FIT_SCORES['tight_concerning'], f"Chest too tight ({ease:.1f}\" ease)"
            elif ease < 1:
                return 'tight_acceptable', self.FIT_SCORES['tight_acceptable'], f"Fitted chest ({ease:.1f}\" ease)"
            elif ease <= 2.5:
                return 'good', self.FIT_SCORES['good'], f"Good chest fit ({ease:.1f}\" ease)"
            elif ease <= 4:
                return 'loose_acceptable', self.FIT_SCORES['loose_acceptable'], f"Relaxed chest fit ({ease:.1f}\" ease)"
            else:
                return 'loose_concerning', self.FIT_SCORES['loose_concerning'], f"Chest too loose ({ease:.1f}\" ease)"
                
        elif dimension == 'neck':
            if ease < 1:
                return 'tight_concerning', self.FIT_SCORES['tight_concerning'], f"Neck too tight ({ease:.1f}\" ease)"
            elif ease < 2:
                return 'tight_acceptable', self.FIT_SCORES['tight_acceptable'], f"Snug neck ({ease:.1f}\" ease)" 
            elif ease <= 3.5:
                return 'good', self.FIT_SCORES['good'], f"Comfortable neck ({ease:.1f}\" ease)"
            elif ease <= 5:
                return 'loose_acceptable', self.FIT_SCORES['loose_acceptable'], f"Loose neck ({ease:.1f}\" ease)"
            else:
                return 'loose_concerning', self.FIT_SCORES['loose_concerning'], f"Neck too loose ({ease:.1f}\" ease)"
                
        elif dimension == 'sleeve':
            if ease < -1:
                return 'tight_concerning', self.FIT_SCORES['tight_concerning'], f"Sleeves too short ({ease:.1f}\" ease)"
            elif ease < 0:
                return 'tight_acceptable', self.FIT_SCORES['tight_acceptable'], f"Sleeves slightly short ({ease:.1f}\" ease)"
            elif ease <= 2:
                return 'good', self.FIT_SCORES['good'], f"Good sleeve length ({ease:.1f}\" ease)"
            elif ease <= 3:
                return 'loose_acceptable', self.FIT_SCORES['loose_acceptable'], f"Sleeves slightly long ({ease:.1f}\" ease)"
            else:
                return 'loose_concerning', self.FIT_SCORES['loose_concerning'], f"Sleeves too long ({ease:.1f}\" ease)"
                
        elif dimension == 'waist':
            if ease < -1:
                return 'tight_concerning', self.FIT_SCORES['tight_concerning'], f"Waist too tight ({ease:.1f}\" ease)"
            elif ease < 0.5:
                return 'tight_acceptable', self.FIT_SCORES['tight_acceptable'], f"Fitted waist ({ease:.1f}\" ease)"
            elif ease <= 3:
                return 'good', self.FIT_SCORES['good'], f"Comfortable waist ({ease:.1f}\" ease)"
            elif ease <= 5:
                return 'loose_acceptable', self.FIT_SCORES['loose_acceptable'], f"Relaxed waist ({ease:.1f}\" ease)"
            else:
                return 'loose_concerning', self.FIT_SCORES['loose_concerning'], f"Waist too loose ({ease:.1f}\" ease)"
                
        else:  # hip or other dimensions
            if ease < 0:
                return 'tight_concerning', self.FIT_SCORES['tight_concerning'], f"{dimension.title()} too tight ({ease:.1f}\" ease)"
            elif ease < 1:
                return 'tight_acceptable', self.FIT_SCORES['tight_acceptable'], f"Fitted {dimension} ({ease:.1f}\" ease)"
            elif ease <= 3:
                return 'good', self.FIT_SCORES['good'], f"Good {dimension} fit ({ease:.1f}\" ease)"
            elif ease <= 5:
                return 'loose_acceptable', self.FIT_SCORES['loose_acceptable'], f"Relaxed {dimension} ({ease:.1f}\" ease)"
            else:
                return 'loose_concerning', self.FIT_SCORES['loose_concerning'], f"{dimension.title()} too loose ({ease:.1f}\" ease)"

    def _calculate_overall_fit_score(self, dimension_analysis: Dict[str, Dict[str, Any]]) -> Tuple[float, List[str]]:
        """Calculate overall fit score and identify primary concerns"""
        
        total_weighted_score = 0.0
        total_weight = 0.0
        primary_concerns = []
        
        for dimension, analysis in dimension_analysis.items():
            weight = self.DIMENSION_WEIGHTS.get(dimension, 0.5)
            score = analysis['score']
            
            # Weight by user confidence if available
            if 'user_confidence' in analysis:
                weight *= analysis['user_confidence']
            
            total_weighted_score += score * weight
            total_weight += weight
            
            # Identify concerning dimensions
            if analysis['fit_type'] in ['tight_concerning', 'loose_concerning']:
                primary_concerns.append(dimension)
        
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        return overall_score, primary_concerns

    def _calculate_recommendation_confidence(self, dimension_analysis: Dict[str, Dict[str, Any]], user_profile: Dict[str, UserDimensionProfile]) -> float:
        """Calculate confidence in the recommendation"""
        
        confidences = []
        
        for dimension, analysis in dimension_analysis.items():
            # Base confidence from fit analysis
            base_confidence = 0.8
            
            # Adjust based on user data confidence
            if dimension in user_profile:
                user_confidence = user_profile[dimension].confidence
                data_points = user_profile[dimension].data_points
                
                # More data points = higher confidence
                data_confidence = min(1.0, data_points / 5.0)
                
                dimension_confidence = base_confidence * user_confidence * data_confidence
            else:
                dimension_confidence = 0.3  # Low confidence with no user data
            
            confidences.append(dimension_confidence)
        
        return statistics.mean(confidences) if confidences else 0.5

    def _generate_recommendation_reasoning(self, dimension_analysis: Dict[str, Dict[str, Any]], available_dimensions: List[str], primary_concerns: List[str]) -> str:
        """Generate human-readable reasoning for the recommendation"""
        
        if not dimension_analysis:
            return "No measurement data available for analysis"
        
        good_fits = [dim for dim, analysis in dimension_analysis.items() if analysis['fit_type'] == 'good']
        acceptable_fits = [dim for dim, analysis in dimension_analysis.items() if analysis['fit_type'] in ['tight_acceptable', 'loose_acceptable']]
        
        reasoning_parts = []
        
        if good_fits:
            reasoning_parts.append(f"Good fit for: {', '.join(good_fits)}")
        
        if acceptable_fits:
            reasoning_parts.append(f"Acceptable fit for: {', '.join(acceptable_fits)}")
        
        if primary_concerns:
            concern_details = []
            for concern in primary_concerns:
                analysis = dimension_analysis[concern]
                concern_details.append(f"{concern} ({analysis['explanation']})")
            reasoning_parts.append(f"Concerns: {', '.join(concern_details)}")
        
        if not reasoning_parts:
            reasoning_parts.append("Limited fit data available")
        
        return "; ".join(reasoning_parts) 