class FitZoneCalculator:
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def calculate_chest_fit_zone(self, garments: list) -> dict:
        """Calculate chest fit zones from user's garments with sophisticated range handling"""
        print(f"Starting calculation with garments: {garments}")
        
        fit_groups = {
            'tight': [],    # Too Tight, Tight but I Like It
            'good': [],     # Good Fit
            'relaxed': []   # Loose but I Like It, Too Loose
        }
        
        for garment in garments:
            try:
                # Parse chest range into min and max
                chest_range = self._parse_chest_range(garment['chest_range'])
                if not chest_range:
                    print(f"Skipping garment with invalid chest range: {garment}")
                    continue
                    
                # Use fit_feedback directly
                fit_type = garment.get('fit_feedback')
                print(f"Processing garment with fit_type: {fit_type}, chest_range: {chest_range}")
                
                # Match exact values from database constraint
                if fit_type in ['Too Tight', 'Tight but I Like It']:
                    fit_groups['tight'].append(chest_range)
                elif fit_type == 'Good Fit':
                    fit_groups['good'].append(chest_range)
                elif fit_type in ['Loose but I Like It', 'Too Loose']:
                    fit_groups['relaxed'].append(chest_range)
                else:
                    print(f"Unknown fit type '{fit_type}', assuming 'good' for garment: {garment}")
                    fit_groups['good'].append(chest_range)
                    
            except Exception as e:
                print(f"Error processing garment {garment}: {str(e)}")
                continue
        
        print(f"Grouped measurements: {fit_groups}")
        zones = self._calculate_zones(fit_groups)
        print(f"Calculated zones: {zones}")
        
        return {
            'tight_range': {
                'min': zones['tight']['min'],
                'max': zones['good']['min']  # Tight range ends where good begins
            },
            'good_range': {
                'min': zones['good']['min'],
                'max': zones['good']['max']
            },
            'relaxed_range': {
                'min': zones['good']['max'],  # Relaxed range starts where good ends
                'max': zones['relaxed']['max']
            }
        }
    
    def _parse_chest_range(self, chest_range: str) -> dict:
        """Parse chest range string into min/max values"""
        try:
            if '-' in chest_range:
                min_val, max_val = map(float, chest_range.split('-'))
                return {
                    'min': min_val,
                    'max': max_val,
                    'avg': (min_val + max_val) / 2
                }
            else:
                value = float(chest_range)
                return {
                    'min': value,
                    'max': value,
                    'avg': value
                }
        except (ValueError, TypeError):
            return None
    
    def _calculate_zones(self, fit_groups: dict) -> dict:
        """Calculate fit zones using sophisticated analysis of ranges"""
        zones = {
            'tight': {'min': None, 'max': None},
            'good': {'min': None, 'max': None},
            'relaxed': {'min': None, 'max': None}
        }
        
        # Calculate tight zone
        if fit_groups['tight']:
            tight_mins = [r['min'] for r in fit_groups['tight'] if r]
            tight_maxs = [r['max'] for r in fit_groups['tight'] if r]
            if tight_mins and tight_maxs:
                zones['tight']['min'] = min(tight_mins)
                zones['tight']['max'] = max(tight_maxs)
        
        # Calculate good zone
        if fit_groups['good']:
            good_mins = [r['min'] for r in fit_groups['good'] if r]
            good_maxs = [r['max'] for r in fit_groups['good'] if r]
            if good_mins and good_maxs:
                zones['good']['min'] = min(good_mins)
                zones['good']['max'] = max(good_maxs)
        
        # Calculate relaxed zone
        if fit_groups['relaxed']:
            relaxed_mins = [r['min'] for r in fit_groups['relaxed'] if r]
            relaxed_maxs = [r['max'] for r in fit_groups['relaxed'] if r]
            if relaxed_mins and relaxed_maxs:
                zones['relaxed']['min'] = min(relaxed_mins)
                zones['relaxed']['max'] = max(relaxed_maxs)
        
        # Handle overlaps and gaps between zones
        self._adjust_zone_boundaries(zones)
        
        return zones
    
    def _adjust_zone_boundaries(self, zones: dict):
        """Adjust zone boundaries to handle overlaps and gaps"""
        # If we have good fit data, use it as anchor
        if zones['good']['min'] is not None and zones['good']['max'] is not None:
            # Adjust tight zone if it overlaps with good
            if (zones['tight']['max'] is not None and 
                zones['tight']['max'] > zones['good']['min']):
                zones['tight']['max'] = zones['good']['min']
            
            # Adjust relaxed zone if it overlaps with good
            if (zones['relaxed']['min'] is not None and 
                zones['relaxed']['min'] < zones['good']['max']):
                zones['relaxed']['min'] = zones['good']['max']
        
        # If we're missing some zones, interpolate
        if zones['tight']['max'] is None and zones['good']['min'] is not None:
            zones['tight']['max'] = zones['good']['min']
        
        if zones['relaxed']['min'] is None and zones['good']['max'] is not None:
            zones['relaxed']['min'] = zones['good']['max'] 