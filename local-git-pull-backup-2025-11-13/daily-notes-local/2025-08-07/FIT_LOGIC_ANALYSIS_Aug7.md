# Fit Logic Analysis: Theory Polo Contradiction

## 🎯 Problem Summary

**Issue**: User's actual garment feedback contradicts the fit zone calculations, leading to incorrect size recommendations.

**Specific Case**: 
- User owns Theory Blue polo (Size M, 38-40" chest)
- User marked it as "Good Fit" 
- But app's fit zones show user preference as 39.5-42.5"
- This causes Size M (38-40") to be classified as "too tight" in recommendations
- **Contradiction**: How can 38-40" be "too tight" when user already owns and likes a 38-40" garment?

## 📊 Current Data State

### User's Actual Garments (from database query):
```
Theory Brenan Polo (Size S): 36-38" chest → "Tight but I Like It"
Theory Blue polo (Size M): 38-40" chest → "Good Fit" ⭐
Theory Burgundy shirt (Size M): 38-40" chest → "Good Fit" ⭐
Lululemon polo (Size M): 39-40" chest → "Good Fit"
Reiss shirt (Size L): 40" chest → "Good Fit"
NN.07 Tee (Size M): 41" chest → "Tight but I Like It"
Banana Republic shirt (Size L): 41-44" chest → "Good Fit"
```

### Calculated Fit Zones:
```
User's "Good" zone: 39.5-42.5"
```

### The Problem:
- **Multiple garments** in 38-40" range marked as "Good Fit"
- **Fit zone calculation** excludes 38-40" from "good" range
- **Result**: Algorithm recommends against sizes that user actually likes

## 🔍 Root Cause Analysis

### Potential Issues in Fit Zone Calculation:

1. **Insufficient Weight on "Good Fit" Feedback**
   - Theory Blue polo (38-40") = "Good Fit" should expand good zone to include 38"
   - Theory Burgundy shirt (38-40") = "Good Fit" reinforces this
   - Algorithm may not be properly incorporating this feedback

2. **Outlier Influence**
   - Larger garments (41-44") might be pulling the "good" range upward
   - Algorithm might be averaging instead of creating inclusive ranges

3. **Feedback Categorization Issues**
   - "Tight but I Like It" vs "Good Fit" distinction
   - Should "Tight but I Like It" be considered acceptable/good?

4. **Statistical Method Problems**
   - Using mean/median instead of inclusive range
   - Not accounting for user's tolerance across different fit types

## 🔧 Current Implementation Analysis

### Backend Files to Investigate:

1. **`fit_zone_calculator.py`** - Core fit zone calculation logic
2. **`simple_multi_dimensional_analyzer.py`** - Size recommendation logic  
3. **`app.py`** - API endpoints and data processing

### Key Functions:
```python
# fit_zone_calculator.py
def calculate_chest_fit_zone(self, garments: list) -> dict:
    # How does this handle "Good Fit" feedback?
    # Does it properly include 38-40" range?

# simple_multi_dimensional_analyzer.py  
def _analyze_chest_with_fit_zones(self, garment_measurement: float, chest_fit_zones: Dict, user_fit_preference: str):
    # How does this classify 38-40" measurements?
    # Why is it marked as "too tight"?
```

## 🎯 Expected Behavior

### What Should Happen:
1. **User has 38-40" garments marked "Good Fit"** 
   → Good zone should include 38-40"
2. **Recommended good zone should be 38-42.5"** (or similar inclusive range)
3. **Size M recommendations should be positive** since user likes 38-40" measurements

### Current vs Expected:
```
Current:  Good zone = 39.5-42.5" → Size M (38-40") = "too tight" ❌
Expected: Good zone = 38-42.5"   → Size M (38-40") = "good fit" ✅
```

## 🔬 Investigation Steps

### 1. Database Verification
```sql
-- Verify user's garment feedback
SELECT b.name, ug.product_name, ug.size_label, 
       sge.chest_min, sge.chest_max,
       (SELECT fc.feedback_text FROM user_garment_feedback ugf 
        JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
        WHERE ugf.user_garment_id = ug.id AND ugf.dimension = 'chest') as chest_feedback
FROM user_garments ug
JOIN brands b ON ug.brand_id = b.id  
LEFT JOIN size_guide_entries_with_brand sge ON ug.size_guide_entry_id = sge.id
WHERE ug.user_id = 1 AND ug.owns_garment = true
ORDER BY sge.chest_min;
```

### 2. Fit Zone Calculation Debug
```python
# Test fit zone calculation with user 1's data
from fit_zone_calculator import FitZoneCalculator
calculator = FitZoneCalculator(user_id=1)
zones = calculator.calculate_chest_fit_zone(user_garments)
print("Calculated zones:", zones)
print("Input garments:", user_garments)
```

### 3. Recommendation Logic Debug  
```python
# Test size recommendation logic
from simple_multi_dimensional_analyzer import SimpleMultiDimensionalAnalyzer
analyzer = SimpleMultiDimensionalAnalyzer(db_config)
result = analyzer._analyze_chest_with_fit_zones(
    garment_measurement=39.0,  # Size M average
    chest_fit_zones=calculated_zones,
    user_fit_preference="good"
)
print("Size M analysis:", result)
```

## 🛠️ Potential Fixes

### Option 1: Inclusive Range Calculation
```python
# Instead of statistical mean, use inclusive range
def calculate_inclusive_good_range(good_fit_garments):
    min_good = min(garment.chest_min for garment in good_fit_garments)
    max_good = max(garment.chest_max for garment in good_fit_garments)
    return {"min": min_good, "max": max_good}
```

### Option 2: Weighted Feedback Integration
```python
# Give higher weight to explicit "Good Fit" feedback
def calculate_weighted_zones(garments):
    good_fit_weight = 2.0  # Higher weight for "Good Fit"
    tight_but_like_weight = 1.5  # Some weight for "Tight but I Like It"
    # Apply weights in zone calculation
```

### Option 3: Multi-Modal Range Detection
```python
# Detect multiple acceptable ranges instead of single zone
def detect_acceptable_ranges(garments):
    # Could return: tight_acceptable (36-40), good (38-43), relaxed (41-45)
    # Overlapping ranges for user flexibility
```

## 📋 Action Items

### Immediate Investigation:
- [ ] Run database query to confirm user 1's garment feedback
- [ ] Debug fit zone calculation with actual user data  
- [ ] Trace size recommendation logic for Size M classification
- [ ] Identify specific line of code causing 38-40" to be "too tight"

### Potential Solutions:
- [ ] Modify fit zone calculation to be more inclusive of "Good Fit" feedback
- [ ] Adjust thresholds in size recommendation logic
- [ ] Implement weighted feedback system
- [ ] Add logging to track decision-making process

### Testing:
- [ ] Verify fix doesn't break other users' recommendations
- [ ] Test edge cases (users with only tight/loose preferences)
- [ ] Validate against multiple garment types and brands

## 🔗 Related Files

- `src/ios_app/Backend/fit_zone_calculator.py` - Core calculation logic
- `src/ios_app/Backend/simple_multi_dimensional_analyzer.py` - Recommendation engine
- `src/ios_app/Backend/app.py` - API endpoints and data flow
- `database/schemas/` - User garment and feedback table structures
- `docs/database/` - Database documentation and constraints

## 💡 Future Considerations

1. **User Feedback Loop**: Allow users to correct fit zone calculations
2. **Machine Learning**: Train model on user preferences over time  
3. **Brand-Specific Adjustments**: Different brands may fit differently
4. **Seasonal Preferences**: User might prefer different fits for different garment types

---

**Created**: 2025-01-20  
**Status**: Investigation needed  
**Priority**: High (affects core recommendation accuracy)

---

# Aug 7 Fit Logic – Current Issue and Next Steps

## Current issue
- The app must pick one size confidently when the user’s “Good” ranges span different sizes (e.g., BR M 38–40 and BR L 41–44 both marked Good).
- Prior logic produced contradictory messages in “Why other sizes don’t work” (e.g., “M chest too tight … like your Theory M”), and midpoint scoring under-represented multi‑modal preferences.
- During live test for Banana Republic “Boxy Linen‑Cotton T‑Shirt”, the backend recommended L correctly, but iOS device calls intermittently timed out while hitting `/user/{id}/measurements`. Local `/docs` also timed out despite the process listening.

## What we implemented today
- Tie‑breakers (no schema changes):
  - Brand-size prior: favor sizes with past “Good Fit” for the same brand
  - Neck strictness: strong penalty if below Good zone without neck tolerance history
- Clearer alternative-size explanations:
  - Replace vague “too tight” with dimension-specific reasons (neck below preferred range; chest slimmer/roomier than Good zone)
- Branch created: `fit-logic-experiment`

## Why L wins for BR Boxy Linen‑Cotton Tee
- Chest: Good 39.5–42.5 overlaps more with L 41–44 than M 38–40
- Neck: Good 16.0–16.5; L = 16–16.5 inside, M = 15–15.5 below, and no neck tolerance history
- Sleeve: Good center ≈34.7; L=35 closer than M=34
- Brand prior: BR L previously marked Good

## Backend instability to fix
- Symptoms:
  - iOS timeouts to `http://<host>:8006/user/1/measurements`
  - `/docs` timing out locally
  - pgbouncer warning about prepared statements during scan logging
- Likely causes:
  - Lifespan/DB pool blocking requests or stuck connections
  - Prepared statements with pgbouncer (transaction/statement mode)

## Immediate action items
- Add health endpoints:
  - `/healthz`: returns 200 without DB
  - `/readyz`: lightweight DB ping with timeout
- Make server startup modes configurable:
  - `APP_RELOAD` to disable auto-reload (done)
  - `APP_DISABLE_DB` to run without pool for UI testing
  - Optional `APP_PORT` fallback (e.g., 8010)
- AsyncPG + pgbouncer:
  - Set `statement_cache_size=0` when pgbouncer is used
  - Avoid prepared statements in logging code path
- Add request timeout/logging wrappers around `/user/{id}/measurements`

## Fit-logic roadmap (MVP → V1)
- MVP (landed):
  - Brand-size prior + neck strictness tie‑breakers
  - Non-contradictory “other sizes” explanations
- Next (no schema changes):
  - Subcategory prior (e.g., T‑shirts)
  - Product “fit intent” bias (Slim/Boxy/Relaxed)
  - Multi-interval chest “Good” ranges and overlap‑based scoring
  - Concise “why winner” line on primary card (neck+chest+sleeve)
- Later (optional persistence):
  - Cache priors/materialized views (feature‑flag + reversible migration)
  - Learn weights from outcomes (user tries both sizes)

## Testing plan
- Continue live tests by scanning borderline products and saving outcomes
- Validate neck/sleeve tie‑breakers across multiple brands
- Monitor explanation readability and perceived value

## Status
- Logic and copy improvements are in place on `fit-logic-experiment`.
- Server stability pending: implement health endpoints and pgbouncer-safe settings next session.
