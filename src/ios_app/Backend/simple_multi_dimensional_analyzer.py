"""
Simple Multi-Dimensional Analyzer
Practical approach that uses all available user data without overcomplicating fit zones.

PHILOSOPHY:
- Chest: Uses fit zones (Tight/Standard/Relaxed) - users have preferences
- Other dimensions: Single "good fit" range - users just want these to work
- Use ALL available measurements from user's closet + feedback
"""

import psycopg2
import statistics
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass

@dataclass
class UserDimensionProfile:
    """User's established measurements for a single dimension"""
    dimension: str
    good_fit_min: float
    good_fit_max: float
    confidence: float
    data_points: int
    source_garments: List[str]  # For transparency

@dataclass
class SizeAnalysis:
    """Analysis of how well a specific size fits the user"""
    size_label: str
    overall_fit_score: float
    dimension_analysis: Dict[str, Dict[str, Any]]
    chest_fit_zone: Optional[str]  # "tight", "standard", "relaxed" or None
    fits_all_dimensions: bool
    concerns: List[str]
    reasoning: str

class SimpleMultiDimensionalAnalyzer:
    """
    Practical multi-dimensional analysis:
    - Chest: Uses existing fit zones for user preference
    - Other dimensions: Single good fit range from closet data
    - Leverages ALL available user garment data + feedback
    """
    
    # Dimension importance for overall scoring
    DIMENSION_WEIGHTS = {
        'chest': 1.0,      # Most important + has fit zones
        'neck': 0.8,       # Very important for dress shirts
        'sleeve': 0.7,     # Important for appearance
        'waist': 0.6,      # Less critical for most tops
        'hip': 0.5         # Least critical for tops
    }
    
    # Tolerance for "good fit" matching (inches)
    GOOD_FIT_TOLERANCE = 1.0

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
        
        # Import fit zone service for chest analysis
        from fit_zone_service import FitZoneService
        self.fit_zone_service = FitZoneService(db_config)
        
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def analyze_all_sizes(self, user_id: int, brand_name: str, category: str = "Tops", user_fit_preference: str = "Standard") -> List[SizeAnalysis]:
        """
        Analyze ALL sizes for a brand using user's multi-dimensional profile
        
        Returns list of SizeAnalysis objects showing how each size fits across all dimensions
        """
        try:
            self.logger.info(f"🔬 Analyzing all sizes for user {user_id}, brand {brand_name}")
            
            # Step 1: Get user's dimension profiles
            user_profiles = self._get_user_dimension_profiles(user_id)
            
            if not user_profiles:
                self.logger.warning(f"No dimension profiles found for user {user_id}")
                return []
            
            # Step 2: Get chest fit zones for preference matching
            chest_fit_zones = self._get_chest_fit_zones(user_id, category)
            
            # Step 3: Get brand's size guide
            size_entries = self._get_brand_size_guide(brand_name, category)
            
            if not size_entries:
                self.logger.warning(f"No size guide found for {brand_name} {category}")
                return []
            
            # Step 4: Analyze each size
            analyses = []
            for size_entry in size_entries:
                analysis = self._analyze_single_size(
                    size_entry, user_profiles, chest_fit_zones, user_fit_preference, category
                )
                if analysis:
                    analyses.append(analysis)
            
            # Step 5: Sort by overall fit score
            analyses.sort(key=lambda a: a.overall_fit_score, reverse=True)
            
            self.logger.info(f"✅ Analyzed {len(analyses)} sizes across {len(user_profiles)} dimensions")
            return analyses
            
        except Exception as e:
            self.logger.error(f"Error analyzing sizes: {str(e)}")
            return []

    def _get_user_dimension_profiles(self, user_id: int) -> Dict[str, UserDimensionProfile]:
        """
        Get user's established acceptable ranges for each dimension from their closet
        Uses cached data from FitZoneService for performance, falls back to calculation if needed
        """
        try:
            # First try to get cached acceptable ranges from FitZoneService (FAST!)
            cached_data = self.fit_zone_service.get_stored_fit_zones(user_id, "Tops")
            
            profiles = {}
            
            # Extract neck/sleeve acceptable ranges from cache if available
            if cached_data:
                for dimension in ['neck', 'sleeve']:
                    if dimension in cached_data:
                        cache_entry = cached_data[dimension]
                        if 'acceptable_min' in cache_entry and 'acceptable_max' in cache_entry:
                            profiles[dimension] = UserDimensionProfile(
                                dimension=dimension,
                                good_fit_min=cache_entry['acceptable_min'],
                                good_fit_max=cache_entry['acceptable_max'],
                                confidence=cache_entry['confidence'],
                                data_points=cache_entry['data_points'],
                                source_garments=[f"Cached ({cache_entry['data_points']} garments)"]
                            )
                            self.logger.info(f"⚡ Using cached {dimension} range: {cache_entry['acceptable_min']:.1f}-{cache_entry['acceptable_max']:.1f}")
            
            # If we have all cached data, return it (PERFORMANCE WIN!)
            if len(profiles) >= 2:  # neck + sleeve
                self.logger.info(f"⚡ All dimension profiles loaded from cache - skipping expensive calculation!")
                return profiles
            
            # Fallback: Calculate missing profiles using expensive query (SLOW FALLBACK)
            self.logger.info(f"🔄 Some profiles missing from cache, calculating from scratch...")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user's garments with measurements and positive feedback
            query = """
                SELECT 
                    ug.id, b.name as brand, ug.product_name, ug.size_label,
                    sge.chest_min, sge.chest_max, sge.chest_range,
                    sge.neck_min, sge.neck_max, sge.neck_range,
                    sge.sleeve_min, sge.sleeve_max, sge.sleeve_range,
                    sge.waist_min, sge.waist_max, sge.waist_range,
                    sge.hip_min, sge.hip_max, sge.hip_range,
                    -- Get feedback for each dimension (prioritize specific, fall back to overall)
                    COALESCE(
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest' 
                         ORDER BY ugf.created_at DESC LIMIT 1),
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' 
                         ORDER BY ugf.created_at DESC LIMIT 1)
                    ) as chest_feedback,
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
                    ) as sleeve_feedback,
                    COALESCE(
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'waist' 
                         ORDER BY ugf.created_at DESC LIMIT 1),
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' 
                         ORDER BY ugf.created_at DESC LIMIT 1)
                    ) as waist_feedback,
                    COALESCE(
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'hip' 
                         ORDER BY ugf.created_at DESC LIMIT 1),
                        (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                         JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                         WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' 
                         ORDER BY ugf.created_at DESC LIMIT 1)
                    ) as hip_feedback
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
            dimension_data = {}
            
            for garment in garments:
                (garment_id, brand, product_name, size_label,
                 chest_min, chest_max, chest_range,
                 neck_min, neck_max, neck_range,
                 sleeve_min, sleeve_max, sleeve_range,
                 waist_min, waist_max, waist_range,
                 hip_min, hip_max, hip_range,
                 chest_feedback, neck_feedback, sleeve_feedback, waist_feedback, hip_feedback) = garment
                
                # Process each dimension
                dimensions = {
                    'chest': (chest_min, chest_max, chest_range, chest_feedback),
                    'neck': (neck_min, neck_max, neck_range, neck_feedback),
                    'sleeve': (sleeve_min, sleeve_max, sleeve_range, sleeve_feedback),
                    'waist': (waist_min, waist_max, waist_range, waist_feedback),
                    'hip': (hip_min, hip_max, hip_range, hip_feedback)
                }
                
                for dim_name, (min_val, max_val, range_str, feedback) in dimensions.items():
                    # Use garments with ANY positive feedback to create broader acceptable ranges
                    positive_feedback = ['Good Fit', 'Tight but I Like It', 'Loose but I Like It', 'Slightly Loose']
                    if feedback in positive_feedback:
                        # Parse actual min/max values, not midpoints
                        actual_min, actual_max = self._parse_min_max_values(min_val, max_val, range_str)
                        if actual_min is not None and actual_max is not None:
                            if dim_name not in dimension_data:
                                dimension_data[dim_name] = []
                            
                            dimension_data[dim_name].append({
                                'min_measurement': actual_min,
                                'max_measurement': actual_max,
                                'garment': f"{brand} {size_label}",
                                'feedback': feedback,
                                'source': 'positive_feedback'
                            })
            
            # Create dimension profiles from the data
            profiles = {}
            for dimension, data_points in dimension_data.items():
                if len(data_points) >= 1:  # Need at least 1 garment with positive feedback
                    # Collect all actual min and max values from size guide measurements
                    all_mins = [dp['min_measurement'] for dp in data_points]
                    all_maxs = [dp['max_measurement'] for dp in data_points]
                    garments = [dp['garment'] for dp in data_points]
                    
                    # Calculate acceptable range from all positive feedback (min to max of all measurements)
                    # This creates the broadest possible acceptable range from user's closet data
                    good_fit_min = min(all_mins)  # Minimum of all minimum measurements
                    good_fit_max = max(all_maxs)  # Maximum of all maximum measurements
                    
                    # Keep the actual range from size guide measurements
                    # No artificial expansion - use the real data from user's positive feedback
                    
                    confidence = min(1.0, len(data_points) / 3.0)  # Full confidence with 3+ garments
                    
                    profiles[dimension] = UserDimensionProfile(
                        dimension=dimension,
                        good_fit_min=good_fit_min,
                        good_fit_max=good_fit_max,
                        confidence=confidence,
                        data_points=len(data_points),
                        source_garments=garments
                    )
            
            self.logger.info(f"Created profiles for {len(profiles)} dimensions: {list(profiles.keys())}")
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error getting user dimension profiles: {str(e)}")
            return {}

    def _get_chest_fit_zones(self, user_id: int, category: str) -> Optional[Dict[str, Tuple[float, float]]]:
        """Get chest fit zones for user preference matching"""
        try:
            stored_zones = self.fit_zone_service.get_stored_fit_zones(user_id, category)
            
            if stored_zones and 'chest' in stored_zones:
                chest_zones = stored_zones['chest']
                return {
                    'tight': (chest_zones['tight']['min'], chest_zones['tight']['max']),
                    'standard': (chest_zones['good']['min'], chest_zones['good']['max']),
                    'relaxed': (chest_zones['relaxed']['min'], chest_zones['relaxed']['max'])
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting chest fit zones: {str(e)}")
            return None

    def _get_brand_size_guide(self, brand_name: str, category: str) -> List[Dict[str, Any]]:
        """Get brand's size guide entries"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    sge.size_label,
                    sge.chest_min, sge.chest_max, sge.chest_range,
                    sge.neck_min, sge.neck_max, sge.neck_range,
                    sge.sleeve_min, sge.sleeve_max, sge.sleeve_range,
                    sge.waist_min, sge.waist_max, sge.waist_range,
                    sge.hip_min, sge.hip_max, sge.hip_range
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
            """
            
            cursor.execute(query, (brand_name, category))
            entries = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Convert to structured format
            size_entries = []
            for entry in entries:
                entry_dict = dict(zip([
                    'size_label',
                    'chest_min', 'chest_max', 'chest_range',
                    'neck_min', 'neck_max', 'neck_range',
                    'sleeve_min', 'sleeve_max', 'sleeve_range',
                    'waist_min', 'waist_max', 'waist_range',
                    'hip_min', 'hip_max', 'hip_range'
                ], entry))
                
                size_entries.append(entry_dict)
            
            return size_entries
            
        except Exception as e:
            self.logger.error(f"Error getting brand size guide: {str(e)}")
            return []

    def _analyze_single_size(
        self, 
        size_entry: Dict[str, Any], 
        user_profiles: Dict[str, UserDimensionProfile],
        chest_fit_zones: Optional[Dict[str, Tuple[float, float]]],
        user_fit_preference: str,
        category: str = "Tops"
    ) -> Optional[SizeAnalysis]:
        """Analyze how well a single size fits the user across all dimensions"""
        
        size_label = size_entry['size_label']
        dimension_analysis = {}
        dimension_scores = []
        concerns = []
        chest_fit_zone = None
        
        # Define dimensions to analyze based on category
        if category.lower() == 'tops':
            # For tops, exclude waist since it measures garment width, not user waist
            dimensions_to_analyze = ['chest', 'neck', 'sleeve', 'hip']
        else:
            # For other categories, analyze all dimensions
            dimensions_to_analyze = ['chest', 'neck', 'sleeve', 'waist', 'hip']
        
        # Analyze each dimension
        for dimension in dimensions_to_analyze:
            garment_measurement = self._parse_measurement(
                size_entry.get(f'{dimension}_min'),
                size_entry.get(f'{dimension}_max'),
                size_entry.get(f'{dimension}_range')
            )
            
            if garment_measurement is None:
                continue
            
            # Special handling for chest (has fit zones)
            if dimension == 'chest' and chest_fit_zones:
                chest_analysis = self._analyze_chest_with_fit_zones(
                    garment_measurement, chest_fit_zones, user_fit_preference
                )
                if chest_analysis:
                    dimension_analysis[dimension] = chest_analysis
                    dimension_scores.append(chest_analysis['score'])
                    chest_fit_zone = chest_analysis['fit_zone']
                    if chest_analysis.get('concern'):
                        concerns.append(f"chest {chest_analysis['concern']}")
            
            # Handle other dimensions (single good fit range)
            elif dimension in user_profiles:
                profile = user_profiles[dimension]
                fits_well = (profile.good_fit_min - self.GOOD_FIT_TOLERANCE) <= garment_measurement <= (profile.good_fit_max + self.GOOD_FIT_TOLERANCE)
                
                if fits_well:
                    # Calculate how well it fits within the range
                    range_center = (profile.good_fit_min + profile.good_fit_max) / 2
                    distance_from_center = abs(garment_measurement - range_center)
                    range_width = profile.good_fit_max - profile.good_fit_min
                    
                    # Score: 1.0 at center, decreases toward edges
                    if range_width > 0:
                        fit_score = max(0.2, 1.0 - (distance_from_center / (range_width / 2 + self.GOOD_FIT_TOLERANCE)))
                    else:
                        fit_score = 0.8  # Good score for single data point match
                    
                    dimension_analysis[dimension] = {
                        'fits_well': True,
                        'garment_measurement': garment_measurement,
                        'good_fit_range': f"{profile.good_fit_min:.1f}-{profile.good_fit_max:.1f}\"",
                        'score': fit_score,
                        'confidence': profile.confidence,
                        'data_points': profile.data_points,
                        'explanation': f"{dimension.title()}: {garment_measurement}\" fits within your good range ({profile.good_fit_min:.1f}-{profile.good_fit_max:.1f}\")"
                    }
                    
                    dimension_scores.append(fit_score * self.DIMENSION_WEIGHTS.get(dimension, 0.5))
                    
                else:
                    # Doesn't fit well - note the concern
                    if garment_measurement < profile.good_fit_min:
                        concerns.append(f"{dimension} too small ({garment_measurement}\" < {profile.good_fit_min:.1f}\")")
                    else:
                        concerns.append(f"{dimension} too large ({garment_measurement}\" > {profile.good_fit_max:.1f}\")")
        
        # Must have at least some dimensional analysis
        if not dimension_analysis:
            return None
        
        # Calculate overall fit score
        if dimension_scores:
            total_weight = sum(self.DIMENSION_WEIGHTS.get(dim, 0.5) for dim in dimension_analysis.keys())
            overall_fit_score = sum(dimension_scores) / total_weight if total_weight > 0 else 0
        else:
            overall_fit_score = 0
        
        # Generate reasoning
        fits_dimensions = list(dimension_analysis.keys())
        reasoning = f"Size {size_label} analyzed across {len(fits_dimensions)} dimensions: {', '.join(fits_dimensions)}"
        if chest_fit_zone:
            reasoning += f". Chest fits in {chest_fit_zone} zone"
        if concerns:
            reasoning += f". Concerns: {', '.join(concerns[:2])}"  # Limit concerns for readability
        
        return SizeAnalysis(
            size_label=size_label,
            overall_fit_score=overall_fit_score,
            dimension_analysis=dimension_analysis,
            chest_fit_zone=chest_fit_zone,
            fits_all_dimensions=len(concerns) == 0,
            concerns=concerns,
            reasoning=reasoning
        )

    def _analyze_chest_with_fit_zones(
        self, 
        garment_measurement: float, 
        chest_fit_zones: Dict[str, Tuple[float, float]], 
        user_fit_preference: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze chest measurement against fit zones"""
        
        tolerance = 0.5  # Same as unified engine
        
        # Check which zones this measurement fits
        zone_matches = {}
        for zone_name, (zone_min, zone_max) in chest_fit_zones.items():
            if zone_min <= garment_measurement <= zone_max + tolerance:
                # Calculate fit score within zone
                zone_center = (zone_min + zone_max) / 2
                distance_from_center = abs(garment_measurement - zone_center)
                zone_width = zone_max - zone_min
                
                if zone_width > 0:
                    fit_score = max(0.1, 1.0 - (distance_from_center / (zone_width / 2)))
                else:
                    fit_score = 0.8
                
                zone_matches[zone_name] = fit_score
        
        if not zone_matches:
            return None
        
        # Prefer the user's fit preference, then best scoring zone
        user_pref_lower = user_fit_preference.lower()
        if user_pref_lower in zone_matches:
            best_zone = user_pref_lower
            score = zone_matches[best_zone]
        else:
            # Use the best scoring zone
            best_zone = max(zone_matches.keys(), key=lambda z: zone_matches[z])
            score = zone_matches[best_zone] * 0.8  # Slight penalty for not matching preference
        
        # Determine if there's a concern
        concern = None
        if garment_measurement < chest_fit_zones['tight'][0]:
            concern = "too small"
        elif garment_measurement > chest_fit_zones['relaxed'][1]:
            concern = "too large"
        
        return {
            'fit_zone': best_zone,
            'score': score,
            'garment_measurement': garment_measurement,
            'zone_range': f"{chest_fit_zones[best_zone][0]}-{chest_fit_zones[best_zone][1]}\"",
            'matches_preference': best_zone == user_pref_lower,
            'concern': concern,
            'explanation': f"Chest: {garment_measurement}\" fits in {best_zone} zone ({chest_fit_zones[best_zone][0]}-{chest_fit_zones[best_zone][1]}\")"
        }

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

    def _parse_min_max_values(self, min_val: Optional[float], max_val: Optional[float], range_str: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
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

    def get_fit_zone_recommendations(self, user_id: int, brand_name: str, category: str = "Tops", user_fit_preference: str = "Standard") -> List[str]:
        """
        Get simple fit zone recommendations in the format: ["Good Fit - L", "Relaxed Fit - XL"]
        This is the main method for the scan endpoint
        """
        try:
            analyses = self.analyze_all_sizes(user_id, brand_name, category, user_fit_preference)
            
            recommendations = []
            for analysis in analyses:
                # STRICT FILTERING: Only recommend sizes that fit ALL dimensions well
                if (analysis.overall_fit_score >= 0.5 and  # Higher threshold for quality
                    analysis.fits_all_dimensions and       # Must fit ALL dimensions
                    len(analysis.concerns) == 0):          # No fit concerns
                    
                    if analysis.chest_fit_zone:
                        # Use chest fit zone for recommendation label
                        zone_display = {
                            'tight': 'Tight Fit',
                            'standard': 'Good Fit', 
                            'relaxed': 'Relaxed Fit'
                        }.get(analysis.chest_fit_zone, 'Good Fit')
                        
                        recommendations.append(f"{zone_display} - {analysis.size_label}")
                    else:
                        # No chest fit zone, just use "Good Fit"
                        recommendations.append(f"Good Fit - {analysis.size_label}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting fit zone recommendations: {str(e)}")
            return []