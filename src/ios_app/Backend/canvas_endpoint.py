"""
Canvas Endpoint - Comprehensive Measurement Prediction Diagnostics
Returns detailed data about how the measurement prediction system works internally.
"""

import psycopg2
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json
import logging
from body_measurement_estimator import BodyMeasurementEstimator
from multi_dimensional_fit_analyzer import MultiDimensionalFitAnalyzer
from direct_garment_comparator import DirectGarmentComparator

logger = logging.getLogger(__name__)

class CanvasDataGenerator:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.body_estimator = BodyMeasurementEstimator(db_config)
        self.multi_analyzer = MultiDimensionalFitAnalyzer(db_config)
        self.garment_comparator = DirectGarmentComparator(db_config)
    
    def generate_canvas_data(self, user_id: int) -> Dict[str, Any]:
        """Generate comprehensive canvas data for debugging and analysis"""
        try:
            logger.info(f"Generating canvas data for user {user_id}")
            
            # Get all the raw data and analysis
            summary = self._generate_summary(user_id)
            raw_feedback = self._get_raw_feedback(user_id)
            body_estimates = self._get_body_estimates(user_id)
            fit_zones = self._get_fit_zones(user_id)
            recommendations = self._get_sample_recommendations(user_id)
            algorithm_details = self._get_algorithm_details()
            
            return {
                "summary": summary,
                "raw_feedback": raw_feedback,
                "body_estimates": body_estimates,
                "fit_zones": fit_zones,
                "recommendations": recommendations,
                "algorithm_details": algorithm_details
            }
            
        except Exception as e:
            logger.error(f"Error generating canvas data: {str(e)}")
            raise
    
    def _generate_summary(self, user_id: int) -> Dict[str, Any]:
        """Generate high-level summary statistics"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Get total garments
            cursor.execute("""
                SELECT COUNT(*) FROM user_garments 
                WHERE user_id = %s AND owns_garment = true
            """, (user_id,))
            total_garments = cursor.fetchone()[0]
            
            # Get total feedback entries
            cursor.execute("""
                SELECT COUNT(*) FROM user_garment_feedback ugf
                JOIN user_garments ug ON ugf.user_garment_id = ug.id
                WHERE ug.user_id = %s AND ug.owns_garment = true
            """, (user_id,))
            total_feedback = cursor.fetchone()[0]
            
            # Get dimensions with data
            cursor.execute("""
                SELECT DISTINCT ugf.dimension, COUNT(*) as feedback_count
                FROM user_garment_feedback ugf
                JOIN user_garments ug ON ugf.user_garment_id = ug.id
                WHERE ug.user_id = %s AND ug.owns_garment = true
                GROUP BY ugf.dimension
                ORDER BY feedback_count DESC
            """, (user_id,))
            dimension_data = cursor.fetchall()
            dimensions_with_data = [row[0] for row in dimension_data]
            
            # Calculate overall confidence (weighted by data quality)
            overall_confidence = self._calculate_overall_confidence(dimension_data)
            
            cursor.close()
            conn.close()
            
            return {
                "total_garments": total_garments,
                "total_feedback": total_feedback,
                "dimensions_with_data": dimensions_with_data,
                "overall_confidence": overall_confidence,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                "total_garments": 0,
                "total_feedback": 0,
                "dimensions_with_data": [],
                "overall_confidence": 0.0,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
    
    def _get_raw_feedback(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all raw feedback data with full context"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    CONCAT(ugf.id, '_', ugf.dimension) as id,
                    ug.id as garment_id,
                    b.name as brand,
                    ug.product_name,
                    ug.size_label,
                    ugf.dimension,
                    fc.feedback_text,
                    ugf.created_at,
                    CASE 
                        WHEN fc.feedback_text = 'Good Fit' THEN 0.9
                        WHEN fc.feedback_text LIKE '%Like It' THEN 0.8
                        ELSE 0.7
                    END as confidence
                FROM user_garment_feedback ugf
                JOIN user_garments ug ON ugf.user_garment_id = ug.id
                JOIN brands b ON ug.brand_id = b.id
                JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                WHERE ug.user_id = %s AND ug.owns_garment = true
                ORDER BY ug.created_at DESC, ugf.dimension
            """, (user_id,))
            
            feedback_data = []
            for row in cursor.fetchall():
                feedback_data.append({
                    "id": str(row[0]),
                    "garment_id": row[1],
                    "brand": row[2],
                    "product_name": row[3] or "Unknown Product",
                    "size_label": row[4],
                    "dimension": row[5],
                    "feedback_text": row[6],
                    "feedback_date": row[7].replace(tzinfo=timezone.utc).isoformat() if row[7] else "",
                    "confidence": float(row[8])
                })
            
            cursor.close()
            conn.close()
            
            return feedback_data
            
        except Exception as e:
            logger.error(f"Error getting raw feedback: {str(e)}")
            return []
    
    def _get_body_estimates(self, user_id: int) -> List[Dict[str, Any]]:
        """Get body measurement estimates from all algorithms"""
        estimates = []
        
        # Get chest estimate
        chest_result = self.body_estimator.estimate_chest_measurement(user_id)
        if chest_result:
            estimates.append(self._format_body_estimate("chest", chest_result))
        
        # Get neck estimate
        neck_result = self.body_estimator.estimate_neck_measurement(user_id)
        if neck_result:
            estimates.append(self._format_body_estimate("neck", neck_result))
        
        # Get sleeve estimate
        sleeve_result = self.body_estimator.estimate_sleeve_measurement(user_id)
        if sleeve_result:
            estimates.append(self._format_body_estimate("sleeve", sleeve_result))
        
        # Get waist estimate
        waist_result = self.body_estimator.estimate_waist_measurement(user_id)
        if waist_result:
            estimates.append(self._format_body_estimate("waist", waist_result))
        
        return estimates
    
    def _format_body_estimate(self, dimension: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format body estimate result for canvas display"""
        estimate = result.get('estimate', 0.0)
        confidence = result.get('confidence', 0.0)
        data_points = result.get('data_points', 0)
        
        # Create confidence range (±1 inch based on confidence)
        range_width = 2.0 * (1.0 - confidence)  # Lower confidence = wider range
        
        return {
            "dimension": dimension,
            "estimated_measurement": float(estimate),
            "confidence": float(confidence),
            "data_points": data_points,
            "method": result.get('method', 'Weighted feedback analysis'),
            "confidence_range": {
                "min": float(estimate - range_width/2),
                "max": float(estimate + range_width/2)
            },
            "details": {
                "garment_sources": self._extract_garment_sources(result),
                "feedback_distribution": self._extract_feedback_distribution(result),
                "algorithm_notes": result.get('reasoning', 'Standard body measurement estimation')
            }
        }
    
    def _extract_garment_sources(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract garment source data from body estimate result"""
        sources = []
        garment_details = result.get('garment_details', [])
        
        for garment in garment_details[:5]:  # Show top 5 sources
            sources.append({
                "brand": garment.get('brand', 'Unknown'),
                "product_name": garment.get('product_name', 'Unknown Product'),
                "size": garment.get('size', 'Unknown'),
                "measurement": float(garment.get('measurement_value', 0.0)),
                "feedback": garment.get('feedback', 'Unknown'),
                "weight": float(garment.get('confidence_weight', 1.0))
            })
        
        return sources
    
    def _extract_feedback_distribution(self, result: Dict[str, Any]) -> Dict[str, int]:
        """Extract feedback distribution from body estimate result"""
        distribution = {}
        garment_details = result.get('garment_details', [])
        
        for garment in garment_details:
            feedback = garment.get('feedback', 'Unknown')
            distribution[feedback] = distribution.get(feedback, 0) + 1
        
        return distribution
    
    def _get_fit_zones(self, user_id: int) -> List[Dict[str, Any]]:
        """Get calculated fit zones using multi-dimensional analyzer"""
        try:
            fit_zones_data = self.multi_analyzer.calculate_multi_dimensional_fit_zones(user_id)
            
            zones = []
            for dimension, zone_data in fit_zones_data.items():
                zones.append({
                    "dimension": dimension,
                    "tight_min": float(zone_data.tight_min),
                    "tight_max": float(zone_data.tight_max),
                    "good_min": float(zone_data.good_min),
                    "good_max": float(zone_data.good_max),
                    "relaxed_min": float(zone_data.relaxed_min),
                    "relaxed_max": float(zone_data.relaxed_max),
                    "confidence": float(zone_data.confidence),
                    "data_points": zone_data.data_points,
                    "calculation_method": "Statistical zones with weighted feedback"
                })
            
            return zones
            
        except Exception as e:
            logger.error(f"Error getting fit zones: {str(e)}")
            return []
    
    def _get_sample_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get sample size recommendations to show the logic"""
        # For now, return empty list - this would show live recommendation testing
        return []
    
    def _get_algorithm_details(self) -> Dict[str, Any]:
        """Get detailed information about all algorithms"""
        return {
            "body_measurement_estimator": {
                "name": "Body Measurement Estimator",
                "version": "2.1",
                "description": "Converts garment feedback to estimated body measurements using industry-standard ease calculations",
                "parameters": {
                    "feedback_deltas": {
                        "value": "Too Tight: -2\", Good Fit: 0\", Too Loose: +2\"",
                        "description": "How much to adjust garment measurements based on fit feedback",
                        "impact": "Determines the sensitivity of body measurement estimation"
                    },
                    "ease_amounts": {
                        "value": "Tight: 0.5\", Regular: 1.5\", Loose: 3.0\"",
                        "description": "Standard ease amounts for different fit types",
                        "impact": "Converts garment measurements to body measurements"
                    },
                    "confidence_weights": {
                        "value": "Product-level: 1.0, Category-level: 0.8, Brand-level: 0.6",
                        "description": "Weighting based on size guide specificity",
                        "impact": "Higher weights for more specific measurements"
                    }
                },
                "confidence": 0.9,
                "last_updated": datetime.now(timezone.utc).isoformat()
            },
            "multi_dimensional_analyzer": {
                "name": "Multi-Dimensional Fit Analyzer",
                "version": "1.5",
                "description": "Analyzes fit across chest, neck, sleeve, waist, and other dimensions simultaneously",
                "parameters": {
                    "dimensions": {
                        "value": "chest, neck, sleeve, waist, hip, length",
                        "description": "All dimensions analyzed for fit prediction",
                        "impact": "More dimensions = more accurate fit prediction"
                    },
                    "confidence_thresholds": {
                        "value": "Chest: 0.9, Neck: 0.7, Sleeve: 0.8, Waist: 0.8",
                        "description": "Confidence levels for each dimension analysis",
                        "impact": "Determines reliability of predictions per dimension"
                    }
                },
                "confidence": 0.85,
                "last_updated": datetime.now(timezone.utc).isoformat()
            },
            "direct_garment_comparator": {
                "name": "Direct Garment Comparator",
                "version": "1.2",
                "description": "Compares new garments directly to user's existing ones without estimating body measurements",
                "parameters": {
                    "range_comparison": {
                        "value": "Identical, Similar, Different thresholds",
                        "description": "How closely measurements must match to be considered similar",
                        "impact": "Determines recommendation accuracy and confidence"
                    },
                    "similarity_scoring": {
                        "value": "Weighted by feedback quality and measurement precision",
                        "description": "How similarity scores are calculated",
                        "impact": "Affects ranking of size recommendations"
                    }
                },
                "confidence": 0.8,
                "last_updated": datetime.now(timezone.utc).isoformat()
            },
            "fit_zone_calculator": {
                "name": "Fit Zone Calculator",
                "version": "1.0",
                "description": "Calculates statistical fit zones (tight, good, relaxed) based on user feedback patterns",
                "parameters": {
                    "statistical_method": {
                        "value": "Weighted standard deviation with feedback grouping",
                        "description": "How fit zones are calculated from feedback data",
                        "impact": "Determines the boundaries of fit zones"
                    },
                    "zone_confidence": {
                        "value": "Based on data points and feedback consistency",
                        "description": "How confident the system is in calculated zones",
                        "impact": "Affects recommendation certainty"
                    }
                },
                "confidence": 0.75,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
    
    def _calculate_overall_confidence(self, dimension_data: List[tuple]) -> float:
        """Calculate overall system confidence based on data quality"""
        if not dimension_data:
            return 0.0
        
        total_weight = 0.0
        weighted_confidence = 0.0
        
        for dimension, count in dimension_data:
            # Calculate confidence based on data points
            if count >= 10:
                confidence = 0.9
            elif count >= 5:
                confidence = 0.7
            elif count >= 3:
                confidence = 0.5
            else:
                confidence = 0.3
            
            # Weight by importance (chest is most important)
            if dimension == 'chest':
                weight = 2.0
            elif dimension in ['sleeve', 'waist']:
                weight = 1.5
            elif dimension == 'overall':
                weight = 1.0  # Overall feedback is good but less specific
            else:
                weight = 1.0
            
            weighted_confidence += confidence * weight * count
            total_weight += weight * count
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0 