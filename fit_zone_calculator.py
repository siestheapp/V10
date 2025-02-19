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
        
        # Calculate averages for each fit type
        tight_avg = sum(avg for avg, _ in tight_fits) / len(tight_fits) if tight_fits else None
        good_avg = sum(avg for avg, _ in good_fits) / len(good_fits) if good_fits else None
        relaxed_avg = sum(avg for avg, _ in relaxed_fits) / len(relaxed_fits) if relaxed_fits else None
        
        # Return full fit zone
        return {
            'tight_min': tight_avg * 0.97 if tight_avg else None,
            'perfect_min': good_avg * 0.97 if good_avg else 40.0,
            'perfect_max': good_avg * 1.03 if good_avg else 42.0,
            'relaxed_max': relaxed_avg * 1.03 if relaxed_avg else None
        }
        
    def _parse_chest_range(self, chest_range: str) -> tuple:
        """Parse chest range string into (avg, spread)"""
        if '-' in chest_range:
            min_val, max_val = map(float, chest_range.split('-'))
            return ((min_val + max_val) / 2, max_val - min_val)
        return (float(chest_range), 0) 