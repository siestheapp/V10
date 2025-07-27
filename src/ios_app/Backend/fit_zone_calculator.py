import statistics
import math
import psycopg2
from psycopg2.extras import RealDictCursor

class FitZoneCalculator:
    def __init__(self, user_id: str, db_connection=None):
        self.user_id = user_id
        self.db_conn = db_connection
    
    def calculate_chest_fit_zone(self, garments: list) -> dict:
        """Calculate chest fit zones using statistical methods + confidence weighting"""
        print(f"Starting statistical calculation with garments: {garments}")
        
        # Convert garments to weighted measurements
        weighted_measurements = []
        for garment in garments:
            try:
                # Parse chest range into min and max
                chest_range = self._parse_chest_range(garment['chest_range'])
                if not chest_range:
                    print(f"Skipping garment with invalid chest range: {garment}")
                    continue
                
                # Use average of range for more stable calculations
                chest_avg = (chest_range['min'] + chest_range['max']) / 2
                
                # Get confidence weight combining feedback quality + measurement methodology
                brand_name = garment.get('brand', 'Unknown')
                fit_feedback = garment.get('fit_feedback', 'Unknown')
                overall_weight = self._get_combined_confidence(fit_feedback, brand_name)
                
                # Get specific chest feedback if available (more reliable than overall)
                chest_feedback = garment.get('chest_feedback')
                if chest_feedback:
                    chest_weight = self._get_combined_confidence(chest_feedback, brand_name)
                    # Use chest-specific feedback if available, otherwise overall
                    final_weight = chest_weight
                    final_feedback = chest_feedback
                else:
                    final_weight = overall_weight
                    final_feedback = fit_feedback
                
                weighted_measurements.append({
                    'value': chest_avg,
                    'weight': final_weight,
                    'feedback': final_feedback,
                    'garment': f"{garment.get('brand', 'Unknown')} {garment.get('size', 'Unknown')}"
                })
                
                print(f"Added measurement: {chest_avg}\" (weight: {final_weight}, feedback: {final_feedback})")
                
            except Exception as e:
                print(f"Error processing garment {garment}: {str(e)}")
                continue
        
        if len(weighted_measurements) < 2:
            print("Insufficient data for statistical analysis, using fallback")
            return self._generate_fallback_zones(weighted_measurements)
        
        # Calculate statistical zones
        statistical_zones = self._calculate_statistical_zones(weighted_measurements)
        
        # Convert to practical shopping ranges
        practical_zones = self._make_practical_ranges(statistical_zones)
        
        print(f"Statistical zones: {statistical_zones}")
        print(f"Practical shopping zones: {practical_zones}")
        
        return practical_zones
    
    def _make_practical_ranges(self, statistical_zones: dict) -> dict:
        """Convert precise statistical ranges into practical shopping ranges"""
        practical_zones = {}
        
        for zone_name, zone_data in statistical_zones.items():
            if zone_data['min'] is not None and zone_data['max'] is not None:
                # Round to practical shopping increments (whole or half inches)
                practical_min = self._round_to_shopping_increment(zone_data['min'], 'down')
                practical_max = self._round_to_shopping_increment(zone_data['max'], 'up')
                
                # Ensure minimum viable range (at least 1 inch for tight/good, 2 inches for relaxed)
                min_range = 1.0 if zone_name != 'relaxed' else 2.0
                if practical_max - practical_min < min_range:
                    center = (practical_min + practical_max) / 2
                    practical_min = center - min_range/2
                    practical_max = center + min_range/2
                    # Re-round after adjustment
                    practical_min = self._round_to_shopping_increment(practical_min, 'down')
                    practical_max = self._round_to_shopping_increment(practical_max, 'up')
                
                practical_zones[zone_name] = {
                    'min': practical_min,
                    'max': practical_max
                }
            else:
                practical_zones[zone_name] = zone_data
        
        # Final validation - ensure zones make sense and don't overlap inappropriately
        self._validate_practical_zones(practical_zones)
        
        return practical_zones
    
    def _round_to_shopping_increment(self, value: float, direction: str) -> float:
        """Round to practical shopping increments (whole or half inches)"""
        if direction == 'down':
            # Round down to nearest half inch
            return math.floor(value * 2) / 2
        else:  # direction == 'up'
            # Round up to nearest half inch
            return math.ceil(value * 2) / 2
    
    def _validate_practical_zones(self, zones: dict):
        """Ensure practical zones make shopping sense"""
        # Ensure tight < good < relaxed with no gaps
        if (zones.get('tight', {}).get('max') is not None and 
            zones.get('good', {}).get('min') is not None):
            
            tight_max = zones['tight']['max']
            good_min = zones['good']['min']
            
            # If there's a gap, close it
            if good_min > tight_max + 0.5:
                zones['tight']['max'] = good_min
            # If they overlap, separate them
            elif tight_max >= good_min:
                zones['tight']['max'] = good_min - 0.5
        
        # DISABLED: Gap-filling logic that artificially extends zones
        # This was causing good zones to be extended to 46" when there's no data
        # between the actual good-fit measurements (41.5") and loose measurements (46.5")
        
        # Same logic for good/relaxed boundary - COMMENTED OUT
        # if (zones.get('good', {}).get('max') is not None and 
        #     zones.get('relaxed', {}).get('min') is not None):
        #     
        #     good_max = zones['good']['max']
        #     relaxed_min = zones['relaxed']['min']
        #     
        #     if relaxed_min > good_max + 0.5:
        #         zones['good']['max'] = relaxed_min
        #     elif good_max >= relaxed_min:
        #         zones['good']['max'] = relaxed_min - 0.5
    
    def _get_confidence_weight(self, feedback: str) -> float:
        """Weight feedback by confidence level"""
        if not feedback:
            return 0.3
            
        weights = {
            'Good Fit': 1.0,           # Highest confidence - this is the target
            'Tight but I Like It': 0.9, # High confidence - user likes this fit
            'Loose but I Like It': 0.8, # Good confidence - user likes loose
            'Slightly Tight': 0.7,     # Moderate confidence
            'Slightly Loose': 0.7,     # Moderate confidence  
            'Too Tight': 0.4,          # Lower confidence - extreme
            'Too Loose': 0.4,          # Lower confidence - extreme
            'Unknown': 0.2             # Very low confidence
        }
        return weights.get(feedback, 0.5)

    def _get_care_adjusted_confidence(self, feedback: str, brand_name: str) -> float:
        """Adjust confidence based on known brand care instruction issues"""
        base_confidence = self._get_confidence_weight(feedback)
        
        # NN.07 care instruction issue: Users ignore "Do Not Tumble Dry" 
        # causing cotton/modal blends to shrink and feel tighter over time
        if brand_name == 'NN.07' and feedback in ['Tight but I Like It', 'Too Tight']:
            print(f"  Reducing confidence for NN.07 tight rating (likely care-damaged): {base_confidence:.2f} → {base_confidence * 0.3:.2f}")
            return base_confidence * 0.3  # Heavily discount tight ratings from NN.07
        
        return base_confidence
    
    def _get_measurement_methodology_confidence(self, brand_name: str, dimension: str = 'chest') -> float:
        """Get measurement confidence from methodology table"""
        if not self.db_conn:
            return 1.0  # Default confidence if no DB connection
        
        try:
            cur = self.db_conn.cursor()
            cur.execute("""
                SELECT final_confidence 
                FROM measurement_methodology_with_final_confidence 
                WHERE brand_name = %s AND dimension = %s
                LIMIT 1
            """, (brand_name, dimension))
            
            result = cur.fetchone()
            cur.close()
            
            if result and result['final_confidence']:
                return float(result['final_confidence'])
            else:
                return 0.95  # Default for brands without methodology data
                
        except Exception as e:
            print(f"Error getting methodology confidence for {brand_name}: {e}")
            return 0.95  # Safe default
    
    def _get_combined_confidence(self, feedback: str, brand_name: str) -> float:
        """Combine feedback confidence with measurement methodology confidence"""
        feedback_confidence = self._get_care_adjusted_confidence(feedback, brand_name)
        methodology_confidence = self._get_measurement_methodology_confidence(brand_name)
        
        # Multiply confidences: both feedback quality AND measurement quality matter
        combined_confidence = feedback_confidence * methodology_confidence
        
        print(f"  Confidence: {feedback} ({feedback_confidence:.2f}) × {brand_name} methodology ({methodology_confidence:.2f}) = {combined_confidence:.2f}")
        
        return combined_confidence
    
    def _calculate_statistical_zones(self, weighted_measurements: list) -> dict:
        """Calculate fit zones using weighted statistics, not min/max"""
        
        # Separate measurements by feedback type for zone assignment
        good_measurements = []
        tight_measurements = []
        loose_measurements = []
        
        for m in weighted_measurements:
            feedback = m['feedback']
            if 'Good Fit' in feedback:
                good_measurements.append(m)
            elif 'Tight' in feedback:
                tight_measurements.append(m)
            elif 'Loose' in feedback:
                loose_measurements.append(m)
            else:
                # Default to good for unknown feedback
                good_measurements.append(m)
        
        zones = {
            'tight': {'min': None, 'max': None},
            'good': {'min': None, 'max': None},
            'relaxed': {'min': None, 'max': None}
        }
        
        # Calculate good zone first (this is our anchor)
        if good_measurements:
            good_values = [m['value'] for m in good_measurements]
            good_weights = [m['weight'] for m in good_measurements]
            
            # Weighted average and standard deviation
            good_center = self._weighted_average(good_values, good_weights)
            good_std = self._weighted_std(good_values, good_weights, good_center)
            
            # Good zone: center ± 0.5 standard deviations (conservative)
            zones['good'] = {
                'min': good_center - 0.5 * good_std,
                'max': good_center + 0.5 * good_std
            }
            
            print(f"Good zone stats - center: {good_center:.1f}, std: {good_std:.1f}")
        
        # Calculate tight zone
        if tight_measurements:
            tight_values = [m['value'] for m in tight_measurements]
            tight_weights = [m['weight'] for m in tight_measurements]
            tight_center = self._weighted_average(tight_values, tight_weights)
            tight_std = self._weighted_std(tight_values, tight_weights, tight_center) if len(tight_values) > 1 else 1.0
            
            zones['tight'] = {
                'min': tight_center - tight_std,
                'max': tight_center + 0.5 * tight_std
            }
        elif zones['good']['min'] is not None:
            # No tight data, estimate from good zone
            zones['tight'] = {
                'min': zones['good']['min'] - 2.0,
                'max': zones['good']['min']
            }
        
        # Calculate relaxed zone  
        if loose_measurements:
            loose_values = [m['value'] for m in loose_measurements]
            loose_weights = [m['weight'] for m in loose_measurements]
            loose_center = self._weighted_average(loose_values, loose_weights)
            loose_std = self._weighted_std(loose_values, loose_weights, loose_center) if len(loose_values) > 1 else 1.0
            
            zones['relaxed'] = {
                'min': loose_center - 0.5 * loose_std,
                'max': loose_center + loose_std
            }
        elif zones['good']['max'] is not None:
            # No loose data, estimate from good zone
            zones['relaxed'] = {
                'min': zones['good']['max'],
                'max': zones['good']['max'] + 3.0
            }
        
        # Ensure zones don't overlap inappropriately
        self._adjust_zone_boundaries(zones)
        
        return zones
    
    def _weighted_average(self, values: list, weights: list) -> float:
        """Calculate weighted average"""
        if not values or not weights:
            return 0.0
        
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        weight_sum = sum(weights)
        
        return weighted_sum / weight_sum if weight_sum > 0 else statistics.mean(values)
    
    def _weighted_std(self, values: list, weights: list, mean: float) -> float:
        """Calculate weighted standard deviation"""
        if len(values) < 2:
            return 1.0  # Default spread for single measurement
        
        if not weights:
            return statistics.stdev(values)
        
        # Weighted variance calculation
        weighted_variance = sum(w * (v - mean) ** 2 for v, w in zip(values, weights))
        weight_sum = sum(weights)
        
        if weight_sum == 0:
            return statistics.stdev(values)
        
        variance = weighted_variance / weight_sum
        return math.sqrt(variance)
    
    def _generate_fallback_zones(self, measurements: list) -> dict:
        """Generate reasonable zones when insufficient data"""
        if not measurements:
            # Default zones for someone with no data - practical ranges
            return {
                'tight': {'min': 38.0, 'max': 40.0},
                'good': {'min': 40.0, 'max': 42.0}, 
                'relaxed': {'min': 42.0, 'max': 45.0}
            }
        
        # Use the few measurements we have with practical safety margins
        values = [m['value'] for m in measurements]
        center = statistics.mean(values)
        
        # Round center to practical measurement
        practical_center = round(center)
        
        return {
            'tight': {'min': float(practical_center - 3), 'max': float(practical_center - 1)},
            'good': {'min': float(practical_center - 1), 'max': float(practical_center + 1)},
            'relaxed': {'min': float(practical_center + 1), 'max': float(practical_center + 4)}
        }
    
    def _parse_chest_range(self, range_str):
        """Parse chest range string into min/max dict"""
        if not range_str or range_str == 'N/A':
            return None
            
        try:
            if '-' in range_str:
                parts = range_str.split('-')
                return {
                    'min': float(parts[0]),
                    'max': float(parts[1])
                }
            else:
                val = float(range_str)
                return {'min': val, 'max': val}
        except (ValueError, IndexError):
            print(f"Could not parse range: {range_str}")
            return None
    
    def _adjust_zone_boundaries(self, zones: dict):
        """Adjust zone boundaries to handle overlaps and gaps"""
        # Ensure tight zone doesn't overlap with good zone
        if (zones['tight']['max'] is not None and zones['good']['min'] is not None and
            zones['tight']['max'] > zones['good']['min']):
            zones['tight']['max'] = zones['good']['min']
        
        # Ensure relaxed zone doesn't overlap with good zone  
        if (zones['relaxed']['min'] is not None and zones['good']['max'] is not None and
            zones['relaxed']['min'] < zones['good']['max']):
            zones['relaxed']['min'] = zones['good']['max']
        
        # Fill gaps if zones are missing
        if zones['tight']['max'] is None and zones['good']['min'] is not None:
            zones['tight']['max'] = zones['good']['min']
        
        if zones['relaxed']['min'] is None and zones['good']['max'] is not None:
            zones['relaxed']['min'] = zones['good']['max'] 