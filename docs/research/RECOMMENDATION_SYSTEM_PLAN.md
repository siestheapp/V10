# V10 Recommendation System Plan

## Database Optimization Recommendations - 2025-06-28 00:05

### 🔍 Current Database Analysis:
- **1 user** with good profile data
- **4 garments** with detailed fit feedback  
- **11 brands** with size guides
- **61 size guide records** (good coverage)
- **0 user_body_measurements** (critical gap)
- **1 product_measurements** (very limited)

### 🚀 Optimization Recommendations:

#### 1. IMMEDIATE Data Quality Improvements:
**A. Implement Automatic Measurement Calculation:**
The app should automatically calculate user measurements from their fit feedback and brand size guides:

```python
# Logic: When user provides fit feedback on a garment
def calculate_user_measurements_from_feedback(user_id, garment_id, fit_feedback):
    # 1. Get the garment's size guide data
    size_guide = get_brand_size_guide(garment.brand_id, garment.size_label)
    
    # 2. Based on fit feedback, estimate user's actual measurements
    if fit_feedback == "Good Fit":
        # User's measurement is within the size guide range
        user_chest = (size_guide.chest_min + size_guide.chest_max) / 2
    elif fit_feedback == "Too Tight":
        # User's measurement is larger than the size guide
        user_chest = size_guide.chest_max + 1.0  # Estimate they need 1" more
    elif fit_feedback == "Too Loose":
        # User's measurement is smaller than the size guide
        user_chest = size_guide.chest_min - 1.0  # Estimate they need 1" less
    
    # 3. Store calculated measurements
    insert_user_measurement(user_id, 'chest', user_chest - 0.5, user_chest + 0.5)
```

**B. Add Measurement Calculation Endpoint:**
```python
@app.post("/calculate-measurements")
async def calculate_user_measurements(user_id: int):
    """Calculate user measurements from their fit feedback"""
    # Get all user garments with fit feedback
    garments = get_user_garments_with_feedback(user_id)
    
    measurements = {}
    for garment in garments:
        if garment.fit_feedback:
            # Calculate measurements based on size guide + feedback
            calculated = calculate_measurement_from_feedback(garment)
            measurements.update(calculated)
    
    # Store calculated measurements
    store_user_measurements(user_id, measurements)
    
    return {"measurements": measurements, "confidence": calculate_confidence(measurements)}
```

**C. Update Recommendation Logic:**
```python
def get_recommendations(user_id):
    # 1. Calculate user measurements from their feedback
    user_measurements = calculate_or_get_user_measurements(user_id)
    
    # 2. Find products with matching measurements
    if user_measurements:
        return find_products_by_measurements(user_measurements)
    else:
        # Fallback to brand/size matching
        return find_products_by_brand_size(user_id)
```

#### 2. Schema Optimizations:
**A. Add Performance Indexes:**
```sql
CREATE INDEX idx_user_garments_user_id ON user_garments(user_id);
CREATE INDEX idx_user_garments_brand_category ON user_garments(brand_id, category);
CREATE INDEX idx_user_fit_feedback_garment_id ON user_fit_feedback(garment_id);
CREATE INDEX idx_user_body_measurements_user_type ON user_body_measurements(user_id, measurement_type);
```

**B. Add Data Integrity Constraints:**
```sql
ALTER TABLE user_fit_feedback 
ADD CONSTRAINT valid_overall_fit 
CHECK (overall_fit IN ('Too Tight', 'Tight but I Like It', 'Good Fit', 'Loose but I Like It', 'Too Loose'));
```

#### 3. Performance Optimizations:
**A. Optimize Fit Zone Calculation:**
```sql
CREATE MATERIALIZED VIEW user_fit_zones_cached AS
SELECT user_id, category, measurement_type, AVG(calculated_min) as avg_min, AVG(calculated_max) as avg_max
FROM user_body_measurements GROUP BY user_id, category, measurement_type;
```

#### 4. Feature Enhancements:
**A. Add Brand Preferences:**
```sql
CREATE TABLE user_brand_preferences (
    user_id INTEGER REFERENCES users(id),
    brand_id INTEGER REFERENCES brands(id),
    preference_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. Data Quality Improvements:
**A. Normalize Measurement Data:**
```sql
ALTER TABLE user_garments ADD COLUMN chest_min NUMERIC, ADD COLUMN chest_max NUMERIC;
UPDATE user_garments SET chest_min = SPLIT_PART(chest_range, '-', 1)::NUMERIC, chest_max = SPLIT_PART(chest_range, '-', 2)::NUMERIC WHERE chest_range LIKE '%-%';
```

### 🎯 Priority Action Plan:
1. **Week 1**: Populate `user_body_measurements` table with actual measurements
2. **Week 2**: Add performance indexes and constraints  
3. **Week 3**: Implement measurement-based recommendation logic
4. **Week 4**: Add usage tracking and analytics

---

## Goal
Build an app that finds a user's measurements and recommends garments that match those measurements. If measurement-based matching isn't possible, default to recommending garments of the same size from the same brand that the user already likes.

---

## Current State
- **User measurements:** `user_body_measurements`
- **User garments:** `user_garments`
- **Fit feedback:** `user_fit_feedback`
- **Brands/products:** `brands`, `product_measurements`
- **Backend endpoints:** Some recommendation logic exists, but needs improvement.

---

## Recommendation Logic

### 1. **Primary: Measurement-Based Matching**
- If the user has a "Good Fit" garment **and** you have measurement data for that garment (e.g., chest, sleeve, etc.):
  - Recommend garments (from your catalog) with similar measurements (within a tolerance).
  - Use `product_measurements` to find matches.

### 2. **Fallback: Size/Brand Matching**
- If you don't have measurement data:
  - Recommend garments from the **same brand** and **same size** as the "Good Fit" garment.
  - This is a safe, user-friendly default.

### 3. **(Optional) Broaden Recommendations**
- Same size, different brand (with a warning: "Fit may vary by brand")
- Neighboring sizes from the same brand (if user wants to experiment)

---

## UI/UX
- In the Shop tab:
  - Show a "Recommended for You" section.
  - Clearly label why each item is recommended ("Based on your L in Lululemon", "Measurement match", etc.).
  - Allow users to give feedback on recommendations to improve future results.

---

## Technical Steps (Checklist)

- [ ] **Backend:** Update `/shop/recommendations` endpoint to:
  - [ ] Accept user ID
  - [ ] Look up user's "Good Fit" garments
  - [ ] Try to match by measurements first
  - [ ] If not possible, match by brand/size
  - [ ] Return a reason for each recommendation
- [ ] **Frontend:**
  - [ ] Display recommendations with context ("Why is this recommended?")
  - [ ] Allow users to give feedback on recommendations
- [ ] **Data Quality:**
  - [ ] Review product catalog and measurement data for completeness
  - [ ] Add more product measurements if possible

---

## Example Recommendation Logic (Pseudocode)

```python
def recommend_garments(user_id):
    good_fit_garments = get_user_good_fit_garments(user_id)
    if not good_fit_garments:
        return []

    for garment in good_fit_garments:
        if garment.has_measurements():
            # Measurement-based match
            matches = find_products_by_measurement(garment.measurements)
            if matches:
                return matches, "Measurement match"
        # Fallback: Brand/size match
        matches = find_products_by_brand_and_size(garment.brand, garment.size)
        if matches:
            return matches, "Brand/size match"
    return []
```

---

## Why This Works
- Personalized: Uses what the user already likes.
- Safe fallback: Never recommends something wildly different.
- Scalable: As you get more measurement data, recommendations get smarter.
- User trust: Explains why each item is recommended.

---

## Progress Tracking
- [ ] Measurement-based matching implemented
- [ ] Fallback brand/size matching implemented
- [ ] Recommendation reasons shown in UI
- [ ] User feedback on recommendations collected
- [ ] Product catalog/measurement data reviewed and improved

---

**Update and cross off items as you make progress!**

---

## Future Automation Opportunities: Size Guide Ingestion

As the system grows, consider automating the size guide ingestion process to improve speed, accuracy, and scalability. Potential automation steps include:

1. **Brand Existence & Insert Automation**
   - Script or API to check if a brand exists and insert if not, returning the new brand_id.

2. **Column Mapping Engine**
   - Tool to map brand-specific terms to standardized schema columns using brand_automap, with prompts for new mappings.

3. **SQL Insert Generation**
   - Script to generate correct SQL for size_guides_v2 and brand_automap based on standardized data.

4. **Screenshot/Table OCR Integration**
   - Use OCR to extract tables from screenshots directly into structured data for ingestion.

5. **End-to-End Ingestion Tool**
   - One-click script or web tool that handles all steps: data extraction, brand check, mapping, SQL generation, and automap updates.

6. **AI-Assisted Mapping**
   - Use an LLM to suggest or auto-map new terms based on context and previous mappings.

7. **Validation & Logging**
   - Automated validation for required fields and constraints, with logging for audit and rollback.

**Note:** This would be a significant project (essentially a mini-app), but would make ingestion nearly hands-off and highly reliable. Revisit as data volume and team needs grow. 