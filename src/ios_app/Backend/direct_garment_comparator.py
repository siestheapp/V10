"""
Direct Garment-to-Garment Comparison System
Simpler, more accurate approach that directly compares garment measurements
without estimating body measurements.
"""

import psycopg2
import statistics
import math
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from dataclasses import dataclass

@dataclass
class MeasurementRange:
    """Represents a measurement range (e.g., 16-16.5 inches)"""
    min_val: Optional[float]
    max_val: Optional[float]
    range_str: Optional[str]
    
    @property
    def midpoint(self) -> Optional[float]:
        """Calculate midpoint only when needed for loose comparisons"""
        if self.min_val is not None and self.max_val is not None:
            return (self.min_val + self.max_val) / 2
        return None
    
    @property
    def display_string(self) -> str:
        """How to display this range to users"""
        if self.range_str:
            return f'{self.range_str}"'
        elif self.min_val is not None and self.max_val is not None:
            if self.min_val == self.max_val:
                return f'{self.min_val}"'
            else:
                return f'{self.min_val}-{self.max_val}"'
        elif self.min_val is not None:
            return f'{self.min_val}"'
        elif self.max_val is not None:
            return f'{self.max_val}"'
        return "N/A"
    
    def is_identical_to(self, other: 'MeasurementRange') -> bool:
        """Check if two ranges are identical"""
        return (self.min_val == other.min_val and 
                self.max_val == other.max_val)
    
    def compare_to(self, other: 'MeasurementRange') -> Dict[str, Any]:
        """Compare this range to another range"""
        if self.is_identical_to(other):
            return {
                'type': 'identical',
                'description': f'Identical range ({self.display_string})',
                'difference': 0
            }
        
        # Calculate meaningful difference
        self_mid = self.midpoint
        other_mid = other.midpoint
        
        if self_mid is not None and other_mid is not None:
            diff = abs(self_mid - other_mid)
            
            if diff <= 0.5:
                return {
                    'type': 'very_similar',
                    'description': f'Very similar: {other.display_string} vs your {self.display_string}',
                    'difference': diff
                }
            elif diff <= 1.0:
                return {
                    'type': 'similar', 
                    'description': f'Similar: {other.display_string} vs your {self.display_string}',
                    'difference': diff
                }
            elif diff <= 2.0:
                return {
                    'type': 'different',
                    'description': f'Different: {other.display_string} vs your {self.display_string}',
                    'difference': diff
                }
            else:
                return {
                    'type': 'very_different',
                    'description': f'Very different: {other.display_string} vs your {self.display_string}',
                    'difference': diff
                }
        
        return {
            'type': 'unknown',
            'description': f'{other.display_string} vs your {self.display_string}',
            'difference': None
        }

@dataclass
class GarmentReference:
    """A user's owned garment that serves as a fit reference"""
    brand: str
    product_name: str
    size_label: str
    measurements: Dict[str, MeasurementRange]  # dimension -> measurement_range
    feedback: Dict[str, str]  # dimension -> feedback_text
    confidence: float  # How reliable this reference is
    
@dataclass
class DirectSizeRecommendation:
    """Size recommendation based on direct garment comparison"""
    size_label: str
    overall_fit_score: float
    dimension_comparisons: Dict[str, Dict[str, Any]]  # dimension -> comparison details
    reference_garments: List[GarmentReference]  # Which garments this is based on
    confidence: float
    reasoning: str

class DirectGarmentComparator:
    """
    Compares new garments directly against user's existing garments
    without estimating body measurements. Much simpler and more accurate.
    """
    
    # Dimension importance for overall scoring
    DIMENSION_WEIGHTS = {
        'chest': 1.0,
        'waist': 0.9, 
        'neck': 0.8,
        'sleeve': 0.7,
        'hip': 0.6
    }
    
    # How much measurement difference is acceptable for each fit type
    FIT_TOLERANCE = {
        'identical': 0.5,      # Within 0.5" = virtually identical
        'very_similar': 1.0,   # Within 1" = very similar fit expected
        'similar': 2.0,        # Within 2" = similar fit expected  
        'different': 4.0,      # Within 4" = different but predictable
        'very_different': float('inf')  # More than 4" = very different
    }
    
    # Brand similarity groups (brands that size similarly)
    BRAND_SIMILARITY = {
        'premium_contemporary': ['J.Crew', 'Banana Republic', 'Theory', 'Reiss'],
        'athletic': ['Lululemon', 'Patagonia'],
        'european': ['NN.07', 'Reiss'],
        'heritage': ['Faherty', 'J.Crew']
    }

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
        
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def get_user_reference_garments(self, user_id: int, target_brand: str = None) -> List[GarmentReference]:
        """
        Get user's owned garments that can serve as fit references
        Prioritizes same brand, then similar brands
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get all user's garments with measurements and feedback
            query = """
                SELECT 
                    b.name as brand,
                    ug.product_name,
                    ug.size_label,
                    -- Measurements
                    sge.chest_min, sge.chest_max, sge.chest_range,
                    sge.neck_min, sge.neck_max, sge.neck_range,
                    sge.waist_min, sge.waist_max, sge.waist_range,
                    sge.sleeve_min, sge.sleeve_max, sge.sleeve_range,
                    sge.hip_min, sge.hip_max, sge.hip_range,
                    -- Feedback by dimension
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest' 
                     ORDER BY ugf.created_at DESC LIMIT 1) as chest_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'neck' 
                     ORDER BY ugf.created_at DESC LIMIT 1) as neck_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'waist' 
                     ORDER BY ugf.created_at DESC LIMIT 1) as waist_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'sleeve' 
                     ORDER BY ugf.created_at DESC LIMIT 1) as sleeve_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'hip' 
                     ORDER BY ugf.created_at DESC LIMIT 1) as hip_feedback,
                    (SELECT fc.feedback_text FROM user_garment_feedback ugf 
                     JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
                     WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'overall' 
                     ORDER BY ugf.created_at DESC LIMIT 1) as overall_feedback,
                    -- Add brand priority for ordering
                    CASE WHEN b.name = %s THEN 1 ELSE 2 END as brand_priority
                FROM user_garments ug
                JOIN brands b ON ug.brand_id = b.id
                LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
                WHERE ug.user_id = %s AND ug.owns_garment = true
                AND sge.id IS NOT NULL  -- Must have measurements
                ORDER BY 
                    brand_priority,  -- Same brand first
                    b.name, ug.size_label
            """
            
            cursor.execute(query, (target_brand or '', user_id))
            rows = cursor.fetchall()
            
            references = []
            for row in rows:
                (brand, product_name, size_label,
                 chest_min, chest_max, chest_range,
                 neck_min, neck_max, neck_range,
                 waist_min, waist_max, waist_range,
                 sleeve_min, sleeve_max, sleeve_range,
                 hip_min, hip_max, hip_range,
                 chest_feedback, neck_feedback, waist_feedback, 
                 sleeve_feedback, hip_feedback, overall_feedback, brand_priority) = row
                
                # Parse measurements for each dimension
                measurements = {}
                if chest_min is not None or chest_max is not None or chest_range is not None:
                    measurements['chest'] = self._parse_measurement(chest_min, chest_max, chest_range)
                if neck_min is not None or neck_max is not None or neck_range is not None:
                    measurements['neck'] = self._parse_measurement(neck_min, neck_max, neck_range)
                if waist_min is not None or waist_max is not None or waist_range is not None:
                    measurements['waist'] = self._parse_measurement(waist_min, waist_max, waist_range)
                if sleeve_min is not None or sleeve_max is not None or sleeve_range is not None:
                    measurements['sleeve'] = self._parse_measurement(sleeve_min, sleeve_max, sleeve_range)
                if hip_min is not None or hip_max is not None or hip_range is not None:
                    measurements['hip'] = self._parse_measurement(hip_min, hip_max, hip_range)
                
                # Collect feedback, preferring specific dimension feedback over overall
                feedback = {}
                for dim in ['chest', 'neck', 'waist', 'sleeve', 'hip']:
                    specific_feedback = locals().get(f'{dim}_feedback')
                    if specific_feedback:
                        feedback[dim] = specific_feedback
                    elif overall_feedback == 'Good Fit':
                        feedback[dim] = 'Good Fit'  # Infer from overall
                
                # Calculate confidence based on brand match and feedback quality
                confidence = self._calculate_reference_confidence(brand, target_brand, feedback)
                
                references.append(GarmentReference(
                    brand=brand,
                    product_name=product_name or "Unknown Product",
                    size_label=size_label,
                    measurements=measurements,
                    feedback=feedback,
                    confidence=confidence
                ))
            
            cursor.close()
            conn.close()
            
            self.logger.info(f"Found {len(references)} reference garments for user {user_id}")
            if target_brand:
                same_brand_count = len([r for r in references if r.brand == target_brand])
                self.logger.info(f"  - {same_brand_count} from same brand ({target_brand})")
            
            return references
            
        except Exception as e:
            self.logger.error(f"Error getting reference garments: {str(e)}")
            return []

    def get_direct_size_recommendations(
        self, 
        user_id: int, 
        brand_name: str, 
        category: str = "Tops"
    ) -> List[DirectSizeRecommendation]:
        """
        Get size recommendations using direct garment-to-garment comparison
        """
        try:
            # Get user's reference garments
            references = self.get_user_reference_garments(user_id, brand_name)
            
            if not references:
                self.logger.warning(f"No reference garments found for user {user_id}")
                return []
            
            # Get target brand's size guide
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
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
                        WHEN 'XS' THEN 1 WHEN 'S' THEN 2 WHEN 'M' THEN 3 
                        WHEN 'L' THEN 4 WHEN 'XL' THEN 5 WHEN 'XXL' THEN 6
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
                (size_label, chest_min, chest_max, chest_range,
                 neck_min, neck_max, neck_range,
                 waist_min, waist_max, waist_range,
                 sleeve_min, sleeve_max, sleeve_range,
                 hip_min, hip_max, hip_range) = size_entry
                
                # Parse target garment measurements
                target_measurements = {}
                if chest_min is not None or chest_max is not None or chest_range is not None:
                    target_measurements['chest'] = self._parse_measurement(chest_min, chest_max, chest_range)
                if neck_min is not None or neck_max is not None or neck_range is not None:
                    target_measurements['neck'] = self._parse_measurement(neck_min, neck_max, neck_range)
                if waist_min is not None or waist_max is not None or waist_range is not None:
                    target_measurements['waist'] = self._parse_measurement(waist_min, waist_max, waist_range)
                if sleeve_min is not None or sleeve_max is not None or sleeve_range is not None:
                    target_measurements['sleeve'] = self._parse_measurement(sleeve_min, sleeve_max, sleeve_range)
                if hip_min is not None or hip_max is not None or hip_range is not None:
                    target_measurements['hip'] = self._parse_measurement(hip_min, hip_max, hip_range)
                
                # Compare against reference garments
                dimension_comparisons, overall_score, best_references = self._compare_against_references(
                    target_measurements, references
                )
                
                if dimension_comparisons:
                    reasoning = self._generate_direct_reasoning(dimension_comparisons, best_references)
                    confidence = self._calculate_direct_confidence(dimension_comparisons, best_references)
                    
                    recommendations.append(DirectSizeRecommendation(
                        size_label=size_label,
                        overall_fit_score=overall_score,
                        dimension_comparisons=dimension_comparisons,
                        reference_garments=best_references,
                        confidence=confidence,
                        reasoning=reasoning
                    ))
            
            # Sort by overall fit score
            recommendations.sort(key=lambda x: x.overall_fit_score, reverse=True)
            
            self.logger.info(f"Generated {len(recommendations)} direct size recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting direct size recommendations: {str(e)}")
            return []

    def _compare_against_references(
        self, 
        target_measurements: Dict[str, MeasurementRange], 
        references: List[GarmentReference]
    ) -> Tuple[Dict[str, Dict], float, List[GarmentReference]]:
        """
        Compare target garment against reference garments
        Returns dimension comparisons, overall score, and best reference garments used
        """
        dimension_comparisons = {}
        dimension_scores = []
        best_references = []
        
        for dimension, target_range in target_measurements.items():
            if target_range is None:
                continue
                
            # Find references with this dimension
            relevant_refs = [r for r in references if dimension in r.measurements and dimension in r.feedback]
            
            if not relevant_refs:
                continue
            
            # Find the best matching reference for this dimension
            best_match = None
            best_score = 0
            
            for ref in relevant_refs:
                ref_range = ref.measurements[dimension]
                ref_feedback = ref.feedback[dimension]
                
                # Calculate similarity score using range comparison
                range_comparison = target_range.compare_to(ref_range)
                similarity_score = self._calculate_range_similarity_score(range_comparison, ref_feedback)
                weighted_score = similarity_score * ref.confidence
                
                if weighted_score > best_score:
                    best_score = weighted_score
                    best_match = ref
            
            if best_match:
                ref_range = best_match.measurements[dimension]
                range_comparison = target_range.compare_to(ref_range)
                
                dimension_comparisons[dimension] = {
                    'target_measurement': target_range.display_string,
                    'reference_measurement': ref_range.display_string,
                    'reference_feedback': best_match.feedback[dimension],
                    'reference_brand': best_match.brand,
                    'reference_size': best_match.size_label,
                    'range_comparison': range_comparison,
                    'similarity_score': best_score,
                    'predicted_fit': self._predict_fit_from_range_comparison(
                        range_comparison, best_match.feedback[dimension]
                    )
                }
                
                dimension_scores.append(best_score * self.DIMENSION_WEIGHTS.get(dimension, 0.5))
                
                if best_match not in best_references:
                    best_references.append(best_match)
        
        # Calculate overall score
        if dimension_scores:
            total_weight = sum(self.DIMENSION_WEIGHTS.get(dim, 0.5) for dim in dimension_comparisons.keys())
            overall_score = sum(dimension_scores) / total_weight if total_weight > 0 else 0
        else:
            overall_score = 0
        
        return dimension_comparisons, overall_score, best_references

    def _calculate_range_similarity_score(self, range_comparison: Dict[str, Any], reference_feedback: str) -> float:
        """Calculate how similar two garments are based on range comparison"""
        
        # Base similarity score from range comparison type
        comparison_type = range_comparison['type']
        if comparison_type == 'identical':
            base_score = 1.0
        elif comparison_type == 'very_similar':
            base_score = 0.9
        elif comparison_type == 'similar':
            base_score = 0.7
        elif comparison_type == 'different':
            base_score = 0.5
        else:
            base_score = 0.2
        
        # Adjust based on reference feedback quality
        feedback_multiplier = {
            'Good Fit': 1.0,
            'Tight but I Like It': 0.9,
            'Loose but I Like It': 0.9,
            'Too Tight': 0.7,
            'Too Loose': 0.7,
            'Slightly Loose': 0.8,
            'Slightly Tight': 0.8
        }.get(reference_feedback, 0.5)
        
        return base_score * feedback_multiplier

    def _predict_fit_from_range_comparison(self, range_comparison: Dict[str, Any], reference_feedback: str) -> str:
        """Predict how target will fit based on range comparison to reference"""
        
        comparison_type = range_comparison['type']
        
        # If ranges are identical or very similar, expect same or very similar fit
        if comparison_type == 'identical':
            return reference_feedback
        elif comparison_type == 'very_similar':
            return reference_feedback  # Close enough to expect same fit
        
        # For different ranges, we can only make general predictions
        # The key insight is that ranges capture the inherent uncertainty,
        # so we should be more conservative about predicting major changes
        elif comparison_type == 'similar':
            # Similar ranges likely mean similar fit, but could be slightly different
            if reference_feedback == 'Good Fit':
                return 'Good Fit'  # Similar range, likely still good
            else:
                return reference_feedback  # Keep original prediction
        else:
            # For different or very different ranges, we can't reliably predict
            # Just note that it's different from the reference
            return f"Different from your {reference_feedback.lower()} reference"
        
        return reference_feedback  # Fallback

    def _calculate_reference_confidence(self, brand: str, target_brand: str, feedback: Dict[str, str]) -> float:
        """Calculate confidence in a reference garment"""
        
        # Same brand gets highest confidence
        if brand == target_brand:
            brand_confidence = 1.0
        elif self._are_brands_similar(brand, target_brand):
            brand_confidence = 0.8
        else:
            brand_confidence = 0.6
        
        # More feedback dimensions = higher confidence
        feedback_confidence = min(1.0, len(feedback) / 3.0)  # 3+ dimensions = full confidence
        
        # Quality of feedback matters
        good_feedback_count = len([f for f in feedback.values() if f in ['Good Fit', 'Tight but I Like It', 'Loose but I Like It']])
        quality_confidence = good_feedback_count / len(feedback) if feedback else 0.5
        
        return brand_confidence * feedback_confidence * quality_confidence

    def _are_brands_similar(self, brand1: str, brand2: str) -> bool:
        """Check if two brands have similar sizing"""
        for group in self.BRAND_SIMILARITY.values():
            if brand1 in group and brand2 in group:
                return True
        return False

    def _calculate_direct_confidence(self, dimension_comparisons: Dict, best_references: List[GarmentReference]) -> float:
        """Calculate confidence in the direct recommendation"""
        
        if not dimension_comparisons:
            return 0.0
        
        # Average similarity scores across dimensions
        similarity_scores = [comp['similarity_score'] for comp in dimension_comparisons.values()]
        avg_similarity = statistics.mean(similarity_scores)
        
        # Reference quality (average confidence of references used)
        if best_references:
            ref_confidence = statistics.mean([ref.confidence for ref in best_references])
        else:
            ref_confidence = 0.5
        
        # Number of dimensions compared
        dimension_confidence = min(1.0, len(dimension_comparisons) / 3.0)
        
        return avg_similarity * ref_confidence * dimension_confidence

    def _generate_direct_reasoning(self, dimension_comparisons: Dict, best_references: List[GarmentReference]) -> str:
        """Generate human-readable reasoning for direct comparison"""
        
        if not dimension_comparisons:
            return "No comparable measurements found"
        
        reasoning_parts = []
        
        # Group by similarity
        identical = []
        similar = []
        different = []
        
        for dim, comp in dimension_comparisons.items():
            range_comp = comp['range_comparison']
            comparison_type = range_comp['type']
            ref_brand = comp['reference_brand']
            ref_size = comp['reference_size']
            predicted_fit = comp['predicted_fit']
            
            comparison_text = f"{dim}: {predicted_fit.lower()}"
            reference_text = f"(vs {ref_brand} {ref_size})"
            
            if comparison_type == 'identical':
                identical.append(f"{comparison_text} {reference_text}")
            elif comparison_type in ['very_similar', 'similar']:
                similar.append(f"{comparison_text} {reference_text}")
            else:
                different.append(f"{comparison_text} {reference_text}")
        
        if identical:
            reasoning_parts.append(f"Identical ranges: {', '.join(identical)}")
        if similar:
            reasoning_parts.append(f"Similar ranges: {', '.join(similar)}")
        if different:
            reasoning_parts.append(f"Different ranges: {', '.join(different)}")
        
        return "; ".join(reasoning_parts)

    def _parse_measurement(self, min_val: Optional[float], max_val: Optional[float], range_str: Optional[str]) -> Optional[MeasurementRange]:
        """Parse measurement to get range object"""
        try:
            # Convert Decimal to float to avoid type issues
            parsed_min = float(min_val) if min_val is not None else None
            parsed_max = float(max_val) if max_val is not None else None
            
            if range_str is not None and range_str.strip():
                if '-' in range_str:
                    parts = range_str.split('-')
                    parsed_min = float(parts[0].strip())
                    parsed_max = float(parts[1].strip())
                else:
                    # Single value in range_str
                    val = float(range_str.strip())
                    parsed_min = parsed_max = val
            
            # Create range object if we have any data
            if parsed_min is not None or parsed_max is not None or range_str is not None:
                return MeasurementRange(
                    min_val=parsed_min,
                    max_val=parsed_max,
                    range_str=range_str
                )
            else:
                return None
        except (ValueError, IndexError, TypeError):
            return None 