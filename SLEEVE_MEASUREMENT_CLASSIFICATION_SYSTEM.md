# Sleeve Measurement Classification System

**Created**: January 20, 2025  
**Purpose**: Definitive guide for classifying the 5 different types of sleeve measurements  

---

## 🎯 **The Problem**

Brands use **5 different sleeve measurement methods**, but we've been storing them all as generic "sleeve" measurements, creating massive confusion during size guide ingestion.

## 📏 **The 5 Sleeve Measurement Types**

### **Type 1: Body Arm Length (Center Back Method)**
- **Examples**: J.Crew "Arm Length", Faherty "Sleeve"
- **Method**: Measured on the body from center back neck, over shoulder, down to wrist
- **Typical Range**: 32"-36" for men's sizes
- **Database Storage**: `size_guide_entries.sleeve_*` 
- **Classification**: `body_measurement_center_back`

### **Type 2: Body Arm Length (Shoulder Point Method)**  
- **Examples**: Some formal wear brands
- **Method**: Measured on the body from shoulder point to wrist
- **Typical Range**: 24"-26" for men's sizes
- **Database Storage**: `size_guide_entries.sleeve_*`
- **Classification**: `body_measurement_shoulder_point`

### **Type 3: Garment Sleeve (Center Back Method)**
- **Examples**: Uniqlo "Sleeve length (center back)"
- **Method**: Garment laid flat, measured from center back neck seam to cuff
- **Typical Range**: 32"-36" for men's sizes (similar to Type 1)
- **Database Storage**: `garment_measurements` with `measurement_type='sleeve_center_back'`
- **Classification**: `garment_measurement_center_back`

### **Type 4: Garment Sleeve (Shoulder Seam to Cuff)**
- **Examples**: Clive "Sleeve Length", most garment specs
- **Method**: Garment laid flat, measured from shoulder seam to cuff
- **Typical Range**: 17"-26" for men's sizes (much shorter)
- **Database Storage**: `garment_measurements` with `measurement_type='sleeve_shoulder_cuff'`
- **Classification**: `garment_measurement_shoulder_cuff`

### **Type 5: Garment Sleeve (Armpit to Cuff)**
- **Examples**: Some technical/athletic brands
- **Method**: Garment laid flat, measured from armpit seam to cuff
- **Typical Range**: 15"-20" for men's sizes (shortest)
- **Database Storage**: `garment_measurements` with `measurement_type='sleeve_armpit_cuff'`
- **Classification**: `garment_measurement_armpit_cuff`

---

## 🔍 **Classification Decision Tree**

```python
def classify_sleeve_measurement(measurement_name, value, context, brand):
    """
    Determine the correct sleeve measurement type
    """
    
    # Value-based classification (most reliable)
    if value >= 30:
        # Long measurements = center back method
        if 'garment' in context.lower() or 'flat' in context.lower():
            return 'garment_measurement_center_back'
        else:
            return 'body_measurement_center_back'
    
    elif value >= 22:
        # Medium measurements = shoulder point or shoulder seam
        if 'garment' in context.lower() or 'shoulder' in context.lower():
            return 'garment_measurement_shoulder_cuff'
        else:
            return 'body_measurement_shoulder_point'
    
    elif value >= 15:
        # Short measurements = definitely garment shoulder seam
        return 'garment_measurement_shoulder_cuff'
    
    else:
        # Very short = armpit method
        return 'garment_measurement_armpit_cuff'
    
    # Context-based fallbacks
    if 'center back' in context.lower():
        return 'garment_measurement_center_back' if 'garment' in context else 'body_measurement_center_back'
    
    if 'arm length' in measurement_name.lower():
        return 'body_measurement_center_back'
    
    # Brand-specific patterns
    brand_patterns = {
        'j_crew': 'body_measurement_center_back',
        'faherty': 'body_measurement_center_back', 
        'uniqlo': 'garment_measurement_shoulder_cuff',  # Unless specified as center back
        'banana_republic': 'body_measurement_center_back'
    }
    
    return brand_patterns.get(brand.lower().replace(' ', '_'), 'unknown')
```

---

## 💾 **Database Implementation Strategy**

### **Enhanced Storage Fields**

Add to both tables:
```sql
-- For size_guide_entries
ALTER TABLE size_guide_entries ADD COLUMN sleeve_measurement_type TEXT;
ALTER TABLE size_guide_entries ADD COLUMN sleeve_method TEXT;

-- For garment_measurements  
ALTER TABLE garment_measurements ADD COLUMN measurement_method TEXT;
ALTER TABLE garment_measurements ADD COLUMN measurement_classification TEXT;
```

### **Standardized Values**
```sql
-- measurement_type values for garment_measurements
'sleeve_center_back'     -- Garment center back to cuff
'sleeve_shoulder_cuff'   -- Garment shoulder seam to cuff  
'sleeve_armpit_cuff'     -- Garment armpit to cuff

-- sleeve_measurement_type for size_guide_entries
'body_center_back'       -- Body measurement, center back method
'body_shoulder_point'    -- Body measurement, shoulder point method
```

---

## 🔄 **Migration Strategy**

### **Phase 1: Reclassify Existing Data**
```python
# Analyze current sleeve measurements and reclassify
UPDATE size_guide_entries SET 
    sleeve_measurement_type = CASE 
        WHEN sleeve_min >= 30 THEN 'body_center_back'
        WHEN sleeve_min >= 22 THEN 'body_shoulder_point'
        ELSE 'unknown'
    END
WHERE sleeve_min IS NOT NULL;

UPDATE garment_measurements SET
    measurement_type = CASE
        WHEN measurement_value >= 30 THEN 'sleeve_center_back'
        WHEN measurement_value >= 15 THEN 'sleeve_shoulder_cuff'
        ELSE 'sleeve_armpit_cuff'
    END,
    measurement_classification = 'migrated_from_generic_sleeve'
WHERE measurement_type = 'sleeve_length';
```

### **Phase 2: Enhanced Ingestion**
- Use the classification decision tree for all new sleeve measurements
- Store the original brand term in `source_term` field
- Add measurement method context to notes

### **Phase 3: Fit Prediction Enhancement**
- Convert all sleeve measurements to common baseline (e.g., shoulder seam to cuff)
- Use conversion ratios between different measurement methods
- Provide more accurate sleeve fit predictions

---

## 🎯 **Conversion Ratios** 

For fit prediction, convert everything to shoulder seam to cuff:

```python
SLEEVE_CONVERSION_RATIOS = {
    'body_center_back': 0.65,      # ~35" center back = ~23" shoulder cuff
    'body_shoulder_point': 0.85,   # ~25" shoulder point = ~21" shoulder cuff  
    'garment_center_back': 0.65,   # Same as body center back
    'garment_shoulder_cuff': 1.0,  # This is our baseline
    'garment_armpit_cuff': 1.3     # ~18" armpit = ~23" shoulder cuff
}
```

---

## ✅ **Success Criteria**

After implementation:
- No more sleeve measurement confusion during ingestion
- Clear classification of all 5 sleeve types
- Accurate sleeve fit predictions across brands
- Ability to compare sleeve measurements across different methods

---

This system finally solves the sleeve measurement chaos by acknowledging that "sleeve" isn't one measurement - it's 5 completely different measurements that need to be handled separately.
