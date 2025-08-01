"""
Unified Fit Recommendation Engine
The brain that powers both shopping and scanning with consistent multi-dimensional analysis.

This captures the original Sies vision: "Take a picture of a shirt tag and get personalized 
size recommendations based on your order history, body measurements, and fit preferences."

Key Enhancement: Returns ALL sizes that match user's fit zones with clear labels:
- "Good Fit - L" (size L falls in user's standard/good zone)  
- "Tight Fit - S" (size S falls in user's tight zone)
- "Relaxed Fit - XL" (size XL falls in user's relaxed zone)
"""

import psycopg2
import statistics
import math
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FitZoneMatch:
    """Represents how well a size matches a specific fit zone"""
    size_label: str
    fit_zone: str  # "tight", "standard", "relaxed"
    fit_zone_display: str  # "Tight Fit", "Good Fit", "Relaxed Fit"
    overall_match_score: float  # 0.0 to 1.0
    dimension_matches: Dict[str, Dict[str, Any]]  # per-dimension analysis
    confidence: float
    primary_concerns: List[str]
    explanation: str

@dataclass
class UnifiedFitRecommendation:
    """Complete recommendation showing all matching fit zones for a brand"""
    brand_name: str
    category: str
    user_id: int
    user_fit_preference: str  # User's selected preference
    
    # All sizes that match any fit zone
    matching_sizes: List[FitZoneMatch]  # Sorted by match quality
    
    # Quick summary for UI
    best_matches: List[str]  # ["Good Fit - L", "Tight Fit - S", "Relaxed Fit - XL"]
    
    # Analysis metadata
    dimensions_analyzed: List[str]
    reference_garments_count: int
    confidence_level: str  # "High", "Medium", "Low"
    
    # Reasoning
    recommendation_summary: str
    detailed_analysis: Dict[str, Any]

class UnifiedFitRecommendationEngine:
    """
    The unified brain for both shopping and scanning recommendations.
    
    Core Philosophy:
    1. Show ALL sizes that match user's fit zones, not just one "best" size
    2. Clear labeling: "Good Fit - L", "Tight Fit - S", etc.
    3. Multi-dimensional analysis across chest, neck, sleeve, waist, hip
    4. Consistent experience between shopping and scanning
    5. Clear reasoning based on user's actual garment history
    """
    
    # Enhanced dimension weights (based on user research and shirt fitting)
    DIMENSION_WEIGHTS = {
        'chest': 1.0,      # Most critical for overall fit
        'neck': 0.9,       # Critical for dress shirts
        'sleeve': 0.8,     # Important for appearance and comfort
        'waist': 0.7,      # Important for fit, but less critical for loose shirts
        'hip': 0.5         # Less critical for most tops
    }
    
    # Fit zone display names
    FIT_ZONE_DISPLAY = {
        'tight': 'Tight Fit',
        'standard': 'Good Fit', 
        'relaxed': 'Relaxed Fit'
    }
    
    # Minimum match threshold for including a size (at least one dimension must match strongly)
    MIN_MATCH_THRESHOLD = 0.1  # Lowered to include more matches during development
    
    # Zone tolerance - how close measurements need to be to "count" as in a zone
    ZONE_TOLERANCE = 1.0  # inches - increased for more forgiving matching

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
        
        # Initialize component services
        from fit_zone_service import FitZoneService
        self.fit_zone_service = FitZoneService(db_config)
        
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def get_all_matching_sizes(
        self,
        user_id: int,
        brand_name: str,
        category: str = "Tops",
        user_fit_preference: str = "Standard"
    ) -> UnifiedFitRecommendation:
        """
        Get ALL sizes that match user's fit zones with clear zone labels.
        
        This is the main method that implements your enhanced vision:
        Instead of "Size L recommended", return:
        - "Good Fit - L" 
        - "Tight Fit - S"
        - "Relaxed Fit - XL"
        
        Args:
            user_id: User's ID
            brand_name: Target brand name
            category: Garment category (e.g., "Tops")
            user_fit_preference: User's current preference ("Tight", "Standard", "Relaxed")
            
        Returns:
            UnifiedFitRecommendation with all matching sizes and their fit zones
        """
        try:
            self.logger.info(f"🎯 Getting ALL matching sizes: user={user_id}, brand={brand_name}, preference={user_fit_preference}")
            
            # Step 1: Get user's established fit zones from their closet data
            user_fit_zones = self._get_user_fit_zones(user_id, category)
            if not user_fit_zones:
                self.logger.warning(f"No fit zones found for user {user_id}, calculating now...")
                self.fit_zone_service.calculate_and_store_fit_zones(user_id)
                user_fit_zones = self._get_user_fit_zones(user_id, category)
                
                if not user_fit_zones:
                    self.logger.error(f"Could not establish fit zones for user {user_id}")
                    return self._create_empty_recommendation(user_id, brand_name, category, user_fit_preference)
            
            # Step 2: Get all available sizes for this brand
            size_guide_entries = self._get_brand_size_guide(brand_name, category)
            if not size_guide_entries:
                self.logger.error(f"No size guide found for {brand_name} {category}")
                return self._create_empty_recommendation(user_id, brand_name, category, user_fit_preference)
            
            # Step 3: Check each size against all fit zones
            matching_sizes = []
            dimensions_analyzed = []
            
            for size_entry in size_guide_entries:
                size_label = size_entry['size_label']
                
                # Check this size against each fit zone (tight, standard, relaxed)
                for zone_type in ['tight', 'standard', 'relaxed']:
                    zone_match = self._analyze_size_against_zone(
                        size_entry=size_entry,
                        zone_type=zone_type,
                        user_fit_zones=user_fit_zones,
                        user_id=user_id
                    )
                    
                    if zone_match and zone_match.overall_match_score >= self.MIN_MATCH_THRESHOLD:
                        matching_sizes.append(zone_match)
                        
                        # Track which dimensions we analyzed
                        for dim in zone_match.dimension_matches.keys():
                            if dim not in dimensions_analyzed:
                                dimensions_analyzed.append(dim)
            
            # Step 4: Sort by match quality and remove duplicates (prefer higher scores)
            matching_sizes = self._deduplicate_and_sort_matches(matching_sizes)
            
            # Step 5: Create summary for UI
            best_matches = [
                f"{match.fit_zone_display} - {match.size_label}" 
                for match in matching_sizes[:6]  # Top 6 matches for UI
            ]
            
            # Step 6: Calculate metadata
            reference_garments_count = self._count_reference_garments(user_id)
            confidence_level = self._determine_confidence_level(
                len(matching_sizes), reference_garments_count, len(dimensions_analyzed)
            )
            
            # Step 7: Generate summary
            recommendation_summary = self._generate_recommendation_summary(
                matching_sizes, user_fit_preference, brand_name
            )
            
            # Step 8: Create detailed analysis
            detailed_analysis = self._create_detailed_analysis(
                matching_sizes, user_fit_zones, dimensions_analyzed
            )
            
            recommendation = UnifiedFitRecommendation(
                brand_name=brand_name,
                category=category,
                user_id=user_id,
                user_fit_preference=user_fit_preference,
                matching_sizes=matching_sizes,
                best_matches=best_matches,
                dimensions_analyzed=dimensions_analyzed,
                reference_garments_count=reference_garments_count,
                confidence_level=confidence_level,
                recommendation_summary=recommendation_summary,
                detailed_analysis=detailed_analysis
            )
            
            self.logger.info(f"✅ Found {len(matching_sizes)} matching sizes across {len(dimensions_analyzed)} dimensions")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error getting matching sizes: {str(e)}")
            return self._create_empty_recommendation(user_id, brand_name, category, user_fit_preference)

    def _get_user_fit_zones(self, user_id: int, category: str) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Get user's established fit zones from database"""
        try:
            stored_zones = self.fit_zone_service.get_stored_fit_zones(user_id, category)
            
            if not stored_zones:
                return {}
            
            # Convert to the format we need: dimension -> {zone_type: (min, max)}
            formatted_zones = {}
            for dimension, zones in stored_zones.items():
                if isinstance(zones, dict):
                    # FitZoneService returns: {'tight': {'min': X, 'max': Y}, 'good': {...}, 'relaxed': {...}}
                    formatted_zones[dimension] = {
                        'tight': (
                            zones.get('tight', {}).get('min', 0), 
                            zones.get('tight', {}).get('max', 0)
                        ),
                        'standard': (
                            zones.get('good', {}).get('min', 0), 
                            zones.get('good', {}).get('max', 0)
                        ),
                        'relaxed': (
                            zones.get('relaxed', {}).get('min', 0), 
                            zones.get('relaxed', {}).get('max', 0)
                        )
                    }
            
            self.logger.info(f"Retrieved fit zones for {len(formatted_zones)} dimensions: {formatted_zones}")
            return formatted_zones
            
        except Exception as e:
            self.logger.error(f"Error getting user fit zones: {str(e)}")
            return {}

    def _get_brand_size_guide(self, brand_name: str, category: str) -> List[Dict[str, Any]]:
        """Get all available sizes for this brand"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    sge.id,
                    sge.size_label,
                    sge.chest_min, sge.chest_max, sge.chest_range,
                    sge.neck_min, sge.neck_max, sge.neck_range,
                    sge.waist_min, sge.waist_max, sge.waist_range,
                    sge.sleeve_min, sge.sleeve_max, sge.sleeve_range,
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
                    'id', 'size_label',
                    'chest_min', 'chest_max', 'chest_range',
                    'neck_min', 'neck_max', 'neck_range',
                    'waist_min', 'waist_max', 'waist_range',
                    'sleeve_min', 'sleeve_max', 'sleeve_range',
                    'hip_min', 'hip_max', 'hip_range'
                ], entry))
                
                size_entries.append(entry_dict)
            
            self.logger.info(f"Found {len(size_entries)} sizes for {brand_name} {category}")
            return size_entries
            
        except Exception as e:
            self.logger.error(f"Error getting brand size guide: {str(e)}")
            return []

    def _analyze_size_against_zone(
        self,
        size_entry: Dict[str, Any],
        zone_type: str,
        user_fit_zones: Dict[str, Dict[str, Tuple[float, float]]],
        user_id: int
    ) -> Optional[FitZoneMatch]:
        """
        Check if a specific size matches a specific fit zone (tight/standard/relaxed).
        
        Returns FitZoneMatch if size fits well in this zone, None otherwise.
        """
        try:
            size_label = size_entry['size_label']
            dimension_matches = {}
            dimension_scores = []
            primary_concerns = []
            
            # Check each dimension against this fit zone
            for dimension in ['chest', 'neck', 'sleeve', 'waist', 'hip']:
                if dimension not in user_fit_zones:
                    continue
                    
                # Get garment measurement for this dimension
                garment_measurement = self._parse_measurement(
                    size_entry.get(f'{dimension}_min'),
                    size_entry.get(f'{dimension}_max'),
                    size_entry.get(f'{dimension}_range')
                )
                
                if garment_measurement is None:
                    continue
                
                # Get user's zone range for this dimension
                zone_range = user_fit_zones[dimension].get(zone_type)
                if not zone_range or zone_range == (0, 0):
                    continue
                
                # Check if garment measurement fits in this zone
                zone_min, zone_max = zone_range
                
                # Allow some tolerance for zone boundaries
                fits_in_zone = (zone_min - self.ZONE_TOLERANCE) <= garment_measurement <= (zone_max + self.ZONE_TOLERANCE)
                
                if fits_in_zone:
                    # Calculate how well it fits (closer to center = better)
                    zone_center = (zone_min + zone_max) / 2
                    distance_from_center = abs(garment_measurement - zone_center)
                    zone_width = zone_max - zone_min
                    
                    # Score: 1.0 at center, decreases toward edges
                    if zone_width > 0:
                        fit_score = max(0.0, 1.0 - (distance_from_center / (zone_width / 2)))
                    else:
                        fit_score = 1.0 if distance_from_center <= self.ZONE_TOLERANCE else 0.0
                    
                    dimension_matches[dimension] = {
                        'garment_measurement': garment_measurement,
                        'zone_range': zone_range,
                        'fits_in_zone': True,
                        'fit_score': fit_score,
                        'distance_from_center': distance_from_center,
                        'explanation': f"{dimension.title()}: {garment_measurement}\" fits in {zone_type} zone ({zone_min}-{zone_max}\")"
                    }
                    
                    # Add to dimension scores (don't weight here, we'll weight during overall calc)
                    dimension_scores.append(fit_score)
                
                else:
                    # Check if it's close enough to be a concern
                    if garment_measurement < zone_min - 1.0:
                        primary_concerns.append(f"{dimension} too small")
                    elif garment_measurement > zone_max + 1.0:
                        primary_concerns.append(f"{dimension} too large")
            
            # Only create a match if we have at least one good dimension match
            if not dimension_matches:
                return None
            
            # Calculate overall match score (simple average for now)
            if dimension_scores:
                overall_match_score = sum(dimension_scores) / len(dimension_scores)
            else:
                overall_match_score = 0
            
            # Calculate confidence based on number of matching dimensions
            confidence = min(1.0, len(dimension_matches) / 3.0)  # Full confidence with 3+ dimensions
            
            # Generate explanation
            matching_dims = list(dimension_matches.keys())
            explanation = f"Size {size_label} fits your {zone_type} preference in {len(matching_dims)} dimension(s): {', '.join(matching_dims)}"
            
            if primary_concerns:
                explanation += f". Potential concerns: {', '.join(primary_concerns)}"
            
            return FitZoneMatch(
                size_label=size_label,
                fit_zone=zone_type,
                fit_zone_display=self.FIT_ZONE_DISPLAY[zone_type],
                overall_match_score=overall_match_score,
                dimension_matches=dimension_matches,
                confidence=confidence,
                primary_concerns=primary_concerns,
                explanation=explanation
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing size {size_entry.get('size_label', 'Unknown')} against {zone_type} zone: {str(e)}")
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

    def _deduplicate_and_sort_matches(self, matching_sizes: List[FitZoneMatch]) -> List[FitZoneMatch]:
        """Remove duplicate sizes and sort by match quality"""
        # Group by size label
        size_groups = {}
        for match in matching_sizes:
            if match.size_label not in size_groups:
                size_groups[match.size_label] = []
            size_groups[match.size_label].append(match)
        
        # Keep the best match for each size
        deduplicated = []
        for size_label, matches in size_groups.items():
            # Sort by overall match score, then by confidence
            matches.sort(key=lambda m: (m.overall_match_score, m.confidence), reverse=True)
            best_match = matches[0]
            deduplicated.append(best_match)
        
        # Sort all matches by quality
        deduplicated.sort(key=lambda m: (
            m.overall_match_score,
            m.confidence,
            len(m.dimension_matches)
        ), reverse=True)
        
        return deduplicated

    def _count_reference_garments(self, user_id: int) -> int:
        """Count how many reference garments user has"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*)
                FROM user_garments ug
                WHERE ug.user_id = %s AND ug.owns_garment = true
            """, (user_id,))
            
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            return count
            
        except Exception as e:
            self.logger.error(f"Error counting reference garments: {str(e)}")
            return 0

    def _determine_confidence_level(self, matches_count: int, reference_garments_count: int, dimensions_count: int) -> str:
        """Determine overall confidence level"""
        if reference_garments_count >= 5 and dimensions_count >= 3 and matches_count > 0:
            return "High"
        elif reference_garments_count >= 2 and dimensions_count >= 2 and matches_count > 0:
            return "Medium"
        else:
            return "Low"

    def _generate_recommendation_summary(self, matching_sizes: List[FitZoneMatch], user_fit_preference: str, brand_name: str) -> str:
        """Generate a summary of recommendations"""
        if not matching_sizes:
            return f"No sizes found that match your fit preferences for {brand_name}"
        
        # Group by fit zone
        zone_groups = {}
        for match in matching_sizes:
            if match.fit_zone not in zone_groups:
                zone_groups[match.fit_zone] = []
            zone_groups[match.fit_zone].append(match.size_label)
        
        summary_parts = []
        for zone_type in ['tight', 'standard', 'relaxed']:
            if zone_type in zone_groups:
                zone_display = self.FIT_ZONE_DISPLAY[zone_type]
                sizes = zone_groups[zone_type]
                if len(sizes) == 1:
                    summary_parts.append(f"{zone_display}: {sizes[0]}")
                else:
                    summary_parts.append(f"{zone_display}: {', '.join(sizes)}")
        
        if summary_parts:
            return f"Found {len(matching_sizes)} matching sizes for {brand_name}: " + " | ".join(summary_parts)
        else:
            return f"Found {len(matching_sizes)} potential sizes for {brand_name}"

    def _create_detailed_analysis(self, matching_sizes: List[FitZoneMatch], user_fit_zones: Dict, dimensions_analyzed: List[str]) -> Dict[str, Any]:
        """Create detailed analysis for API response"""
        return {
            'total_matches': len(matching_sizes),
            'dimensions_analyzed': dimensions_analyzed,
            'fit_zones_available': list(user_fit_zones.keys()),
            'match_breakdown': {
                match.size_label: {
                    'fit_zone': match.fit_zone,
                    'fit_zone_display': match.fit_zone_display,
                    'overall_score': round(match.overall_match_score, 3),
                    'confidence': round(match.confidence, 3),
                    'matching_dimensions': list(match.dimension_matches.keys()),
                    'concerns': match.primary_concerns
                }
                for match in matching_sizes
            }
        }

    def _create_empty_recommendation(self, user_id: int, brand_name: str, category: str, user_fit_preference: str) -> UnifiedFitRecommendation:
        """Create empty recommendation when no matches found"""
        return UnifiedFitRecommendation(
            brand_name=brand_name,
            category=category,
            user_id=user_id,
            user_fit_preference=user_fit_preference,
            matching_sizes=[],
            best_matches=[],
            dimensions_analyzed=[],
            reference_garments_count=0,
            confidence_level="Low",
            recommendation_summary=f"No size recommendations available for {brand_name}",
            detailed_analysis={'total_matches': 0, 'error': 'No fit zones or size guide data available'}
        )

    def get_quick_scan_recommendations(self, user_id: int, brand_name: str) -> List[str]:
        """
        Quick method for scan screen - just return the best match labels
        
        Returns list like: ["Good Fit - L", "Tight Fit - S", "Relaxed Fit - XL"]
        """
        try:
            recommendation = self.get_all_matching_sizes(user_id, brand_name)
            return recommendation.best_matches
        except Exception as e:
            self.logger.error(f"Error getting quick scan recommendations: {str(e)}")
            return []