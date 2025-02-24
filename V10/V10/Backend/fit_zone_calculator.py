class FitZoneCalculator:
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def calculate_chest_fit_zone(self, garments: list) -> dict:
        """Calculate chest fit zones from user's garments"""
        # Group garments by fit type
        tight_fits = [
            self._parse_chest_range(g['chest_range'])
            for g in garments
            if (g.get('fit_feedback') == 'Tight but I Like It' or g.get('chest_feedback') == 'Tight but I Like It')
            and g.get('chest_range')
        ]
        
        good_fits = [
            self._parse_chest_range(g['chest_range'])
            for g in garments
            if (g.get('fit_feedback') == 'Good Fit' or g.get('chest_feedback') == 'Good Fit')
            and g.get('chest_range')
        ]
        
        relaxed_fits = [
            self._parse_chest_range(g['chest_range'])
            for g in garments
            if (g.get('fit_feedback') == 'Loose but I Like It' or g.get('chest_feedback') == 'Loose but I Like It')
            and g.get('chest_range')
        ]

        # Compute the actual min/max for each category
        tight_min = min(chest for chest, _ in tight_fits) if tight_fits else None
        tight_max = max(chest for chest, _ in tight_fits) if tight_fits else None

        good_min = min(chest for chest, _ in good_fits) if good_fits else None
        good_max = max(chest for chest, _ in good_fits) if good_fits else None

        relaxed_min = min(chest for chest, _ in relaxed_fits) if relaxed_fits else None
        relaxed_max = max(chest for chest, _ in relaxed_fits) if relaxed_fits else None

        # Return full fit zone
        return {
            'tight_min': tight_min,
            'tight_max': tight_max,
            'good_min': good_min,
            'good_max': good_max,
            'relaxed_min': relaxed_min,
            'relaxed_max': relaxed_max
        }

    def _parse_chest_range(self, chest_range: str) -> tuple:
        """Parse chest range string into (avg, spread)"""
        if '-' in chest_range:
            min_val, max_val = map(float, chest_range.split('-'))
            return ((min_val + max_val) / 2, max_val - min_val)  # (average, spread)
        return (float(chest_range), 0)  # Single value, no spread 