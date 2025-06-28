# V10 Recommendation System Plan

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