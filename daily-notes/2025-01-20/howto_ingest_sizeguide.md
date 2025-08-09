# How to Ingest Size Guides - Complete AI Agent Guide

**Created**: January 20, 2025  
**Last Updated**: January 20, 2025  
**Purpose**: Step-by-step guide for AI agents to add brand size guides to the database  
**Status**: TESTED - Based on successful Vuori ingestion

---

## 🎯 **Quick Start Checklist**

For AI agents who need to add a size guide quickly:

- [ ] **Step 1**: Extract size data from user's images/text
- [ ] **Step 2**: Check if brand exists, create if needed
- [ ] **Step 3**: Create size guide record with proper metadata
- [ ] **Step 4**: Add individual size entries for each size
- [ ] **Step 5**: Create raw documentation record
- [ ] **Step 6**: Verify ingestion with quality checks

---

## 📋 **Complete Step-by-Step Process**

### **Phase 1: Data Extraction & Analysis**

#### **1.1 Extract Size Data from User Input**
- Look for size charts in images or text
- Identify available measurements (chest, neck, waist, sleeve, etc.)
- Note the measurement units (inches or cm)
- Extract all size labels and their corresponding measurements

**Example from Vuori ingestion:**
```
XXS: 33-35" chest
XS: 33-35" chest  
S: 35-39" chest
M: 39-41" chest
L: 41-43" chest
XL: 43-46" chest
XXL: 46-49" chest
3XL: 49-52" chest
```

#### **1.2 Determine Size Guide Metadata**
- **Brand**: What brand is this?
- **Gender**: Male/Female/Unisex?
- **Category**: Usually "Tops" (category_id = 1)
- **Specificity**: 
  - `'broad'` = covers all items in category (most common)
  - `'specific'` = covers subcategory only
  - `'product'` = single product
- **Source**: Official size guide URL if available

---

### **Phase 2: Database Operations**

#### **Step 1: Check if Brand Exists**

```sql
-- ✅ TESTED: Check for existing brand
SELECT id, name, region, default_unit FROM brands WHERE LOWER(name) = LOWER('Vuori');
```

**If brand doesn't exist, create it:**
```sql
-- ✅ TESTED: Create new brand
INSERT INTO brands (name, region, default_unit, notes) 
VALUES ('Vuori', 'USA', 'in', 'Premium athletic and performance wear brand based in California') 
RETURNING id;
```

#### **Step 2: Create Size Guide Record**

```sql
-- ✅ TESTED: Create main size guide record
INSERT INTO size_guides (
    brand_id, gender, category_id, subcategory_id, fit_type,
    guide_level, specificity, unit, source_url, size_guide_header, notes
) VALUES (
    13, 'Male', 1, NULL, 'Regular',
    'category_level', 'broad', 'in', 
    'https://vuoriclothing.com/size-guide',
    'Men''s Tops Size Guide', 
    'Universal size guide for Vuori men''s tops. Chest measurements in inches. Data extracted from official size guide images.'
) RETURNING id;
```

**Field Guidelines:**
- `brand_id`: Use ID from Step 1
- `gender`: 'Male', 'Female', or 'Unisex'
- `category_id`: Usually 1 for Tops
- `subcategory_id`: NULL unless specific subcategory
- `fit_type`: 'Regular', 'Slim', 'Tall', or 'NA'
- `guide_level`: Usually 'category_level'
- `specificity`: Usually 'broad'
- `unit`: 'in' or 'cm'

#### **Step 3: Add Size Entries**

```sql
-- ✅ TESTED: Add individual size measurements
INSERT INTO size_guide_entries (
    size_guide_id, size_label,
    chest_min, chest_max, chest_range,
    neck_min, neck_max, neck_range,
    waist_min, waist_max, waist_range,
    sleeve_min, sleeve_max, sleeve_range,
    hip_min, hip_max, hip_range,
    center_back_length
) VALUES 
    (16, 'XXS', 33, 35, '33-35', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    (16, 'XS', 33, 35, '33-35', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    (16, 'S', 35, 39, '35-39', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    (16, 'M', 39, 41, '39-41', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    (16, 'L', 41, 43, '41-43', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    (16, 'XL', 43, 46, '43-46', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    (16, 'XXL', 46, 49, '46-49', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
    (16, '3XL', 49, 52, '49-52', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
```

**Data Entry Rules:**
- **Single Values**: `min = max = value`, `range = "value"`
- **Ranges**: `min = lower`, `max = upper`, `range = "lower-upper"`
- **Missing Data**: Use `NULL` for all three fields (min, max, range)

#### **Step 4: Create Raw Documentation**

```sql
-- ✅ TESTED: Store source documentation for audit trail
INSERT INTO raw_size_guides (
    brand_id, gender, category_id, subcategory_id, fit_type,
    source_url, screenshot_path, raw_text
) VALUES (
    13, 'Male', 1, NULL, 'Regular',
    'https://vuoriclothing.com/size-guide',
    'User provided images of Vuori size guide showing chest measurements',
    'Vuori Men''s Size Guide - Chest measurements in inches: XXS(33-35), XS(33-35), S(35-39), M(39-41), L(41-43), XL(43-46), XXL(46-49), 3XL(49-52)'
);
```

#### **Step 5: Verify Ingestion**

```sql
-- ✅ TESTED: Verify size guide was created correctly
SELECT 
    sg.id, sg.brand_id, b.name as brand_name, sg.gender, sg.specificity, 
    sg.guide_level, sg.size_guide_header, sg.notes
FROM size_guides sg 
JOIN brands b ON sg.brand_id = b.id 
WHERE sg.id = 16;

-- ✅ TESTED: Verify all size entries
SELECT size_label, chest_min, chest_max, chest_range
FROM size_guide_entries 
WHERE size_guide_id = 16 
ORDER BY chest_min;

-- ✅ TESTED: Check for measurement overlaps
SELECT 
    size_label, chest_min, chest_max,
    LAG(chest_max) OVER (ORDER BY chest_min) as prev_max,
    CASE 
        WHEN chest_min < LAG(chest_max) OVER (ORDER BY chest_min) 
        THEN 'OVERLAP' 
        ELSE 'OK' 
    END as overlap_status
FROM size_guide_entries 
WHERE size_guide_id = 16 AND chest_min IS NOT NULL
ORDER BY chest_min;
```

---

## 🛠️ **Python Script Template**

For AI agents who prefer to create Python scripts:

```python
#!/usr/bin/env python3
"""
Size Guide Ingestion Template
Adapt this for any brand's size guide data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.database_access import execute_query

# 1. Define your size data
BRAND_NAME = "YourBrand"
SIZE_DATA = [
    {"size_label": "S", "chest_min": 35, "chest_max": 39, "chest_range": "35-39"},
    {"size_label": "M", "chest_min": 39, "chest_max": 41, "chest_range": "39-41"},
    # Add more sizes...
]

def check_or_create_brand():
    """Check if brand exists, create if needed"""
    # Check existing
    result = execute_query(
        "SELECT id, name FROM brands WHERE LOWER(name) = LOWER(%s);", 
        (BRAND_NAME,)
    )
    
    if result and len(result) > 0:
        return result[0]['id']
    
    # Create new
    result = execute_query(
        "INSERT INTO brands (name, region, default_unit, notes) VALUES (%s, %s, %s, %s) RETURNING id;",
        (BRAND_NAME, "USA", "in", f"{BRAND_NAME} size guide")
    )
    
    return result[0]['id'] if result else None

def create_size_guide(brand_id):
    """Create size guide record"""
    result = execute_query("""
        INSERT INTO size_guides (
            brand_id, gender, category_id, subcategory_id, fit_type,
            guide_level, specificity, unit, source_url, size_guide_header, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
    """, (
        brand_id, 'Male', 1, None, 'Regular',
        'category_level', 'broad', 'in', 
        f'https://{BRAND_NAME.lower()}.com/size-guide',
        f'{BRAND_NAME} Men\'s Tops Size Guide', 
        f'Size guide for {BRAND_NAME} men\'s tops'
    ))
    
    return result[0]['id'] if result else None

def add_size_entries(size_guide_id):
    """Add individual size measurements"""
    for size_data in SIZE_DATA:
        execute_query("""
            INSERT INTO size_guide_entries (
                size_guide_id, size_label, chest_min, chest_max, chest_range
            ) VALUES (%s, %s, %s, %s, %s);
        """, (
            size_guide_id,
            size_data["size_label"],
            size_data["chest_min"],
            size_data["chest_max"],
            size_data["chest_range"]
        ))

def main():
    """Main ingestion process"""
    print(f"🚀 Starting {BRAND_NAME} Size Guide Ingestion")
    
    # Step 1: Brand
    brand_id = check_or_create_brand()
    print(f"✅ Brand ID: {brand_id}")
    
    # Step 2: Size Guide
    size_guide_id = create_size_guide(brand_id)
    print(f"✅ Size Guide ID: {size_guide_id}")
    
    # Step 3: Size Entries
    add_size_entries(size_guide_id)
    print(f"✅ Added {len(SIZE_DATA)} size entries")
    
    print("🎉 Ingestion Complete!")

if __name__ == "__main__":
    main()
```

---

## 🔍 **Common Patterns & Examples**

### **Pattern 1: Chest Measurements Only (like Vuori)**
- Most athletic/casual brands
- Only chest measurements provided
- Set other measurements to NULL

### **Pattern 2: Full Measurements (Dress Shirts)**
- Formal/business brands
- Chest, neck, sleeve, waist measurements
- More complex but follows same pattern

### **Pattern 3: Women's Sizing**
- Use "bust" measurements → map to `chest` field
- May include hip measurements
- Gender = 'Female'

### **Pattern 4: Range vs Single Values**
```sql
-- Ranges: "34-36"
chest_min = 34, chest_max = 36, chest_range = "34-36"

-- Single values: "38"
chest_min = 38, chest_max = 38, chest_range = "38"
```

---

## ⚠️ **Common Mistakes to Avoid**

1. **Missing raw_size_guides**: Always create the documentation record
2. **Wrong specificity**: Don't assume 'broad' - check if brand has multiple guides
3. **Inconsistent units**: All measurements must use same unit (usually inches)
4. **Missing verification**: Always verify with the test queries
5. **Estimated data**: Never estimate - only use confirmed data from user
6. **Wrong size labels**: Use exact labels from guide (including hyphens, spaces)

---

## 🎯 **Success Criteria**

Your ingestion is successful when:
- [ ] Brand exists in database
- [ ] Size guide record created with proper metadata
- [ ] All size entries added with correct measurements
- [ ] Raw documentation stored
- [ ] Verification queries return expected results
- [ ] No database constraint violations
- [ ] Size progression is logical (no major overlaps)

---

## 📚 **Related Files**

- **[Database Query Cookbook](docs/database/DATABASE_QUERY_COOKBOOK.md)** - More SQL examples
- **[Size Guide Ingestion Process V2](daily-notes/2025-08-08/SIZE_GUIDE_INGESTION_COMPLETE_PROCESS_V2.md)** - Detailed technical specs
- **[Database Access Script](scripts/database_access.py)** - Python database functions

---

## 📝 **Real-World Success Story**

**Vuori Size Guide Ingestion (January 20, 2025)**
- ✅ Successfully added 8 sizes (XXS through 3XL)
- ✅ Chest measurements from 33-52 inches
- ✅ Complete documentation and verification
- ✅ Ready for V10 app fit recommendations

**Result**: Size guide ID 16, fully functional and tested!

---

**This guide is based on actual successful ingestion. Copy the patterns, adapt the data, and you'll have reliable size guide ingestion every time!** 🚀
