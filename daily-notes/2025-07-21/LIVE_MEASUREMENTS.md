# Live Measurements & Fit Zones

This document describes how the Live Measurements tab works, including the data flow between the Swift UI and backend APIs.

## Overview

The Live Measurements feature provides real-time feedback on how garment measurements compare to the user's personalized fit zones. These zones are calculated based on the user's garment history and feedback preferences.

## Data Flow

1. User opens the Live Measurements tab
2. App fetches personalized fit zones from the backend
3. Live measurements from sensors are compared against these zones
4. UI displays measurements with color-coded zones (tight, good, relaxed)

## Backend Endpoints

### Fit Zone Data (app.py - Supabase tailor3 database)

```python
@app.get("/user/{user_id}/measurements")
async def get_user_measurements(user_id: str):
    # Get garments
    garments = get_user_garments(user_id)
    
    # Calculate fit zones
    calculator = FitZoneCalculator(user_id)
    fit_zone = calculator.calculate_chest_fit_zone(garments)
    
    # Format and return response
    response = format_measurements_response(garments, fit_zone)
    return response
```

#### Response Format:
```json
{
  "Tops": {
    "tightRange": {
      "min": 36.0,
      "max": 39.0
    },
    "goodRange": {
      "min": 39.0,
      "max": 41.0
    },
    "relaxedRange": {
      "min": 41.0,
      "max": 47.0
    },
    "garments": [
      {
        "brand": "Theory",
        "garmentName": "Brenan Polo Shirt",
        "chestRange": "36.0-38.0",
        "chestValue": 36.0,
        "size": "S",
        "fitFeedback": "Tight but I Like It",
        "feedback": "Tight but I Like It"
      }
      // Additional garments...
    ]
  }
}
```

### Ideal Measurements (app.py - Supabase tailor3 database)

```python
@app.get("/user/{user_id}/ideal_measurements")
async def get_ideal_measurements(user_id: str):
    # Returns ideal measurements based on fit zones
```

#### Response Format:
```json
[
  {
    "type": "chest",
    "min": 40.0,
    "max": 42.0,
    "unit": "in"
  }
  // Other measurement types...
]
```

### Alternative Implementation (main.py - v10_app database)

```python
@app.get("/user/{user_id}/measurements")
async def get_user_measurements(user_id: str):
    # Retrieves data from fit_feedback table
    # Calculates preferred ranges based on historical feedback
```

## Fit Zone Calculation

Fit zones are calculated in the `FitZoneCalculator` class based on:
1. Historical garments the user owns
2. Feedback provided on those garments (Too Tight, Tight but I Like It, Good, etc.)
3. Actual measurements of those garments

The calculation logic in SQL:

```sql
WITH measurements AS (
    SELECT 
        CASE 
            WHEN ug.chest_range ~ '^[0-9]+(\.[0-9]+)?-[0-9]+(\.[0-9]+)?$' THEN 
                (CAST(split_part(ug.chest_range, '-', 1) AS FLOAT) + 
                 CAST(split_part(ug.chest_range, '-', 2) AS FLOAT)) / 2
            ELSE CAST(ug.chest_range AS FLOAT)
        END as chest_value,
        COALESCE(uff.chest_fit, ug.fit_feedback) as fit_type
    FROM user_garments ug
    LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
    WHERE ug.user_id = USER_ID
    AND ug.owns_garment = true
    AND ug.chest_range IS NOT NULL
),
averages AS (
    SELECT 
        AVG(chest_value) FILTER (WHERE fit_type = 'Tight but I Like It') as tight_avg,
        AVG(chest_value) FILTER (WHERE fit_type = 'Good Fit') as good_avg,
        AVG(chest_value) FILTER (WHERE fit_type = 'Loose but I Like It') as loose_avg
    FROM measurements
)
-- Calculate fit zone ranges based on averages
```

## UI Implementation

The `LiveMeasurementsView.swift` file renders:
1. Current measurements (from sensors)
2. Color-coded fit zones:
   - Tight (yellow): Measurements the user finds "tight but likes"
   - Good (green): Ideal fit range
   - Relaxed (blue): Measurements the user finds "loose but likes"

## Database Tables

The primary tables supporting this feature:

1. `user_garments` - Stores the user's owned garments
2. `user_fit_feedback` - Stores detailed feedback on fit
3. `user_fit_zones` - Stores calculated fit zones per user

## When to Use Which API

- Use `app.py` endpoints for detailed fit analysis with historical garment data
- Use `main.py` endpoints for simpler fit ranges without requiring garment history

## Implementation Notes

- Live measurements are updated in real-time as the user interacts with the app
- Fit zones are recalculated whenever new feedback is provided
- The `recalculate_fit_zones()` trigger in the database ensures zones stay current 