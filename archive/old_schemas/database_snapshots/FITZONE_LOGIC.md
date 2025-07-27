# Fit Zone Logic

## Overview
The Fit Zone feature provides users with personalized fit ranges ("Tight", "Good", "Relaxed") for garment categories (e.g., Tops) based on their owned garments and fit feedback. This helps users understand which garment measurements are likely to provide their preferred fit.

---

## Data Flow

1. **Data Storage (Database):**
   - User garments and their feedback are stored in the `user_garments` and `user_fit_feedback` tables.
   - Each garment has associated measurements (e.g., `chest_range`) and fit feedback (e.g., "Good Fit", "Too Tight").
   - The database does **not** calculate fit zones; it only stores raw data.

2. **Backend Logic (Python/FastAPI):**
   - The backend fetches all owned garments and their feedback for a user.
   - The `FitZoneCalculator` class (in `fit_zone_calculator.py`) processes this data.
   - Garments are grouped by fit feedback:
     - **Tight:** "Too Tight", "Tight but I Like It"
     - **Good:** "Good Fit"
     - **Relaxed:** "Loose but I Like It", "Too Loose"
   - For each group, the chest measurement ranges are extracted.
   - The boundaries for each fit zone are calculated:
     - **Tight Range:** Minimum and maximum chest values from "tight" group
     - **Good Range:** Minimum and maximum chest values from "good" group
     - **Relaxed Range:** Minimum and maximum chest values from "relaxed" group
   - The fit zones are returned as part of the `/user/{user_id}/measurements` API response.

3. **Frontend (iOS App):**
   - The app calls the `/user/{user_id}/measurements` endpoint to get fit zones and garment data.
   - Fit zones are displayed visually (e.g., colored bars for each range).
   - Users see which measurements correspond to their preferred fit.

---

## Key Points
- **Fit zone logic is entirely in the backend Python code.**
- **Only chest measurements and their feedback are used for fit zone calculation.**
- **Sleeve, back length, and other measurements are not currently used in fit zone boundaries.**
- **The database only stores raw garment and feedback data.**
- **Changing feedback or adding new garments with different chest measurements/feedback will update the fit zones.**

---

## Example Logic Flow
1. User owns 5 tops with chest measurements and feedback.
2. Backend groups garments by feedback and extracts chest ranges.
3. Fit zones are calculated:
   - Tight: 36.0"–39.0"
   - Good: 39.0"–41.0"
   - Relaxed: 41.0"–47.0"
4. App displays these ranges to the user.

---

## Future Improvements
- Incorporate sleeve, back length, or other measurements into fit zone logic.
- Allow users to select which measurement(s) define their fit zones.
- Add more granular feedback options or weighting.
- Store fit zone history for tracking changes over time. 