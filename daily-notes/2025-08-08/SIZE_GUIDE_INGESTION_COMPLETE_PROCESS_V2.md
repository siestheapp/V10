# Complete Size Guide Ingestion Process Documentation V2

**Date Created**: August 8, 2025  
**Last Updated**: August 8, 2025  
**Author**: Updated based on Lacoste implementation and specificity field addition  
**Status**: CURRENT - Use this version

## Overview

This document provides a comprehensive, granular guide for implementing size guide ingestion into the tailor3 database system. It covers ALL database tables involved, business logic complexities, and step-by-step instructions to ensure no columns or tables are missed.

---

## 🗄️ Database Tables Involved (4 Core Tables)

### 1. **`brands`** - Brand Management
```sql
-- Check if brand exists first
SELECT id, name FROM brands WHERE LOWER(name) = LOWER('[Brand Name]');

-- If not found, create brand
INSERT INTO brands (name, region, default_unit, notes) 
VALUES ('[Brand Name]', '[Country/Region]', 'in', '[Brand notes]') 
RETURNING id;
```

**Purpose**: Create or verify brand exists  
**Required Fields**: `name`, `default_unit`  
**Optional Fields**: `region`, `notes`  
**Key Decisions**: 
- `default_unit`: `'in'` (inches) or `'cm'` (centimeters)
- `region`: Country/region for context (e.g., 'France', 'USA')

### 2. **`size_guides`** - Size Guide Metadata
```sql
INSERT INTO size_guides (
    brand_id, gender, category_id, subcategory_id, fit_type, 
    guide_level, specificity, unit, source_url, size_guide_header, notes
) VALUES (
    [brand_id], 'Male', [category_id], [subcategory_id], '[fit_type]', 
    '[guide_level]', '[specificity]', 'in', '[source_url]', '[header]', '[notes]'
) RETURNING id;
```

**Purpose**: Main size guide record with complete metadata  

**CRITICAL FIELDS - Must Be Set:**
- `brand_id`: Foreign key to brands table
- `gender`: `'Male'` | `'Female'` | `'Unisex'`
- `category_id`: Foreign key to categories (usually 1 for Tops)
- `guide_level`: `'brand_level'` | `'category_level'` | `'product_level'`
- `specificity`: `'broad'` | `'specific'` | `'product'` | `'unknown'`
- `unit`: `'in'` | `'cm'`
- `source_url`: Official size guide page URL

**IMPORTANT FIELDS - Should Be Set:**
- `subcategory_id`: Foreign key if guide is subcategory-specific (NULL for broad guides)
- `fit_type`: `'Regular'` | `'Slim'` | `'Tall'` | `'NA'` (use 'NA' when unclear)
- `size_guide_header`: Descriptive header from the guide (e.g., "Men's Shirts")
- `notes`: Comprehensive notes about scope and specificity

**Guide Level Classification:**
- `'brand_level'`: Universal across all brand categories (rare)
- `'category_level'`: Specific to one category (most common)
- `'product_level'`: Specific to individual products

**Specificity Classification (NEW):**
- `'broad'`: Covers entire category (e.g., "All Men's Tops")
- `'specific'`: Covers subcategory (e.g., "Men's Shirts only")
- `'product'`: Single product guide
- `'unknown'`: Unclear scope - needs research

### 3. **`size_guide_entries`** - Individual Size Measurements
```sql
INSERT INTO size_guide_entries (
    size_guide_id, size_label,
    chest_min, chest_max, chest_range,
    neck_min, neck_max, neck_range,
    waist_min, waist_max, waist_range,
    sleeve_min, sleeve_max, sleeve_range,
    hip_min, hip_max, hip_range,
    center_back_length
) VALUES (
    [size_guide_id], '[size_label]',
    [chest], [chest], '[chest]',
    [neck], [neck], '[neck]',
    [waist], [waist], '[waist]',
    [sleeve], [sleeve], '[sleeve]',
    [hip], [hip], '[hip]',
    [length]
);
```

**Purpose**: Individual size measurements for each size  

**Available Dimensions**: `chest`, `neck`, `waist`, `sleeve`, `hip`, `center_back_length`  

**Data Entry Rules**:
- **Single Values**: `min = max = value`, `range = "value"`
- **Ranges**: `min = lower`, `max = upper`, `range = "lower-upper"`
- **Missing Data**: Use `NULL` for all three fields (min, max, range)

**Common Brand Term Mappings**:
- "Collar" / "Collar Size" → `neck`
- "Bust" → `chest` (for women)
- "Chest" → `chest` (for men)
- "Waist" → `waist`
- "Sleeve Length" → `sleeve`
- "Hip" → `hip`
- "Inseam" / "Inside Leg" / "Length" → `center_back_length`

### 4. **`raw_size_guides`** - Source Documentation & Screenshots
```sql
INSERT INTO raw_size_guides (
    brand_id, gender, category_id, subcategory_id, fit_type,
    source_url, screenshot_path, raw_text, raw_table_json
) VALUES (
    [brand_id], 'Male', [category_id], [subcategory_id], '[fit_type]',
    '[official_guide_url]', '[screenshot_drive_link]', '[raw_text]', '[json_data]'
);
```

**Purpose**: Store original source materials and documentation  

**CRITICAL FIELDS**:
- `brand_id`, `gender`, `category_id`: Match the main size guide
- `source_url`: Official size guide page URL
- `screenshot_path`: Google Drive link to screenshot

**OPTIONAL FIELDS**:
- `raw_text`: Extracted text from the guide
- `raw_table_json`: JSON representation of the size table
- `subcategory_id`: If guide is subcategory-specific

---

## 📋 Complete Step-by-Step Ingestion Process

### **Phase 1: Pre-Analysis (CRITICAL)**

#### **Step 1.1: Screenshot Analysis**
- [ ] **Brand Identification**: What brand is this?
- [ ] **Gender**: Male/Female/Unisex?
- [ ] **Category**: Tops/Bottoms/Outerwear/etc.?
- [ ] **Subcategory Specificity**: Does dropdown show this is for specific subcategory?
- [ ] **Measurements Available**: Which dimensions are provided?
- [ ] **Size Range**: What sizes are covered?

#### **Step 1.2: Scope Determination**
- [ ] **Guide Level**: Brand-wide, category-specific, or product-specific?
- [ ] **Specificity Assessment**: 
  - `broad`: Covers all items in category
  - `specific`: Covers subcategory only (like Lacoste "Men's Shirts")
  - `product`: Single product
  - `unknown`: Can't determine without research

#### **Step 1.3: Source Documentation**
- [ ] **Official Guide URL**: Link to brand's size guide page
- [ ] **Screenshot Storage**: Upload to Google Drive, get shareable link
- [ ] **Product Context**: If from product page, note specific product

### **Phase 2: Database Preparation**

#### **Step 2.1: Brand Verification**
```sql
-- Check if brand exists
SELECT id, name, region, default_unit FROM brands WHERE LOWER(name) = LOWER('[Brand Name]');
```
- [ ] **If exists**: Note brand_id for later use
- [ ] **If not exists**: Create brand with proper region and unit

#### **Step 2.2: Category/Subcategory Lookup**
```sql
-- Get category ID
SELECT id FROM categories WHERE name = '[Category Name]';

-- Get subcategory ID (if applicable)
SELECT id FROM subcategories WHERE name = '[Subcategory Name]' AND category_id = [category_id];
```
- [ ] **Category ID**: Usually 1 for Tops
- [ ] **Subcategory ID**: Only if guide is subcategory-specific

### **Phase 3: Size Guide Creation**

#### **Step 3.1: Main Size Guide Record**
```sql
INSERT INTO size_guides (
    brand_id, gender, category_id, subcategory_id, fit_type,
    guide_level, specificity, unit, source_url, size_guide_header, notes
) VALUES (
    [brand_id], '[gender]', [category_id], [subcategory_id], '[fit_type]',
    '[guide_level]', '[specificity]', '[unit]', '[source_url]', '[header]', '[detailed_notes]'
) RETURNING id;
```

**Checklist for each field**:
- [ ] `brand_id`: Correct brand ID from Step 2.1
- [ ] `gender`: Male/Female/Unisex
- [ ] `category_id`: Correct category ID from Step 2.2
- [ ] `subcategory_id`: NULL unless subcategory-specific
- [ ] `fit_type`: Regular/Slim/Tall/NA (use NA when unclear)
- [ ] `guide_level`: brand_level/category_level/product_level
- [ ] `specificity`: broad/specific/product/unknown
- [ ] `unit`: in/cm (match brand's default)
- [ ] `source_url`: Official size guide page URL
- [ ] `size_guide_header`: Header from guide (e.g., "Men's Shirts")
- [ ] `notes`: Comprehensive description of scope and context

#### **Step 3.2: Raw Source Documentation**
```sql
INSERT INTO raw_size_guides (
    brand_id, gender, category_id, subcategory_id, fit_type,
    source_url, screenshot_path
) VALUES (
    [brand_id], '[gender]', [category_id], [subcategory_id], '[fit_type]',
    '[source_url]', '[screenshot_drive_link]'
);
```

**Checklist**:
- [ ] **All metadata fields**: Match the main size guide exactly
- [ ] **source_url**: Official guide page
- [ ] **screenshot_path**: Google Drive shareable link

### **Phase 4: Size Entry Data**

#### **Step 4.1: Measurement Extraction**
For each size in the guide:
- [ ] **Size Label**: Extract exact size label (S, M, L, XS-S, etc.)
- [ ] **Measurements**: Extract all available dimensions
- [ ] **Value Type**: Single value or range?

#### **Step 4.2: Data Entry**
```sql
-- For each size
INSERT INTO size_guide_entries (
    size_guide_id, size_label,
    chest_min, chest_max, chest_range,
    neck_min, neck_max, neck_range,
    waist_min, waist_max, waist_range,
    sleeve_min, sleeve_max, sleeve_range,
    hip_min, hip_max, hip_range,
    center_back_length
) VALUES (
    [size_guide_id], '[size_label]',
    [chest_value], [chest_value], '[chest_value]',
    [neck_value], [neck_value], '[neck_value]',
    -- ... continue for all available dimensions
    -- Use NULL for unavailable dimensions
);
```

**Data Entry Checklist for Each Size**:
- [ ] **size_guide_id**: Correct ID from Step 3.1
- [ ] **size_label**: Exact label from guide
- [ ] **chest**: min, max, range (NULL if not available)
- [ ] **neck**: min, max, range (NULL if not available)
- [ ] **waist**: min, max, range (NULL if not available)
- [ ] **sleeve**: min, max, range (NULL if not available)
- [ ] **hip**: min, max, range (NULL if not available)
- [ ] **center_back_length**: single value (NULL if not available)

### **Phase 5: Verification & Quality Check**

#### **Step 5.1: Data Verification**
```sql
-- Verify size guide was created
SELECT sg.*, b.name as brand_name 
FROM size_guides sg 
JOIN brands b ON sg.brand_id = b.id 
WHERE sg.id = [size_guide_id];

-- Verify all size entries
SELECT size_label, chest_min, neck_min, waist_min, sleeve_min 
FROM size_guide_entries 
WHERE size_guide_id = [size_guide_id] 
ORDER BY chest_min;

-- Verify raw documentation
SELECT source_url, screenshot_path 
FROM raw_size_guides 
WHERE brand_id = [brand_id] AND category_id = [category_id];
```

#### **Step 5.2: Quality Checklist**
- [ ] **All required fields populated**: No critical NULLs
- [ ] **Consistent measurements**: Logical progression across sizes
- [ ] **Proper specificity**: Classification matches actual scope
- [ ] **Complete documentation**: Both source URL and screenshot stored
- [ ] **Accurate metadata**: Header and notes reflect true scope

---

## 🎯 Real-World Examples

### **Example 1: Lacoste (Specific Subcategory Guide)**
- **Specificity**: `'specific'` (Men's Shirts only, not all tops)
- **Guide Level**: `'brand_level'` (official brand guide)
- **Header**: "Men's Shirts"
- **Notes**: "Subcategory-specific guide for Men's Long Sleeve Shirts only. Lacoste maintains separate size guides for different product types..."

### **Example 2: Faherty (Broad Category Guide)**
- **Specificity**: `'broad'` (covers all men's tops)
- **Guide Level**: `'category_level'`
- **Header**: "Measurements for Men's Tops"
- **Notes**: "Universal guide covering all men's tops categories"

### **Example 3: Theory (Unknown Scope)**
- **Specificity**: `'unknown'` (unclear if broad or specific)
- **Guide Level**: `'category_level'`
- **Header**: "Size Guide"
- **Notes**: "Scope unclear - needs research to determine if this applies to all tops or specific subcategories"

---

## ⚠️ Common Mistakes to Avoid

### **Database Mistakes**:
1. **Missing raw_size_guides entry**: Always create both main guide AND raw documentation
2. **Wrong specificity**: Don't assume broad - check if brand has multiple guides
3. **Incomplete notes**: Always explain the scope and context
4. **Missing screenshot**: Always store the screenshot in raw_size_guides
5. **Wrong source_url**: Use the main size guide page, not product page

### **Data Entry Mistakes**:
1. **Inconsistent units**: All measurements must use same unit (usually inches)
2. **Missing range fields**: Always populate min, max, AND range for each measurement
3. **Wrong size labels**: Use exact labels from guide (including hyphens, spaces)
4. **Estimated data**: Never estimate or extrapolate - only use confirmed data

### **Classification Mistakes**:
1. **Assuming broad scope**: Many brands have subcategory-specific guides
2. **Wrong guide_level**: Most are category_level, not brand_level
3. **Generic headers**: Use specific headers from the guide, not generic ones

---

## 🔧 Database Schema Reference

### **Critical Constraints**:
- `guide_level`: Must be 'brand_level', 'category_level', or 'product_level'
- `specificity`: Must be 'broad', 'specific', 'product', or 'unknown'
- `gender`: Must be 'Male', 'Female', or 'Unisex'
- `unit`: Must be 'in' or 'cm'

### **Foreign Key Relationships**:
- `size_guides.brand_id` → `brands.id`
- `size_guides.category_id` → `categories.id`
- `size_guides.subcategory_id` → `subcategories.id` (nullable)
- `size_guide_entries.size_guide_id` → `size_guides.id`
- `raw_size_guides.brand_id` → `brands.id`

---

## 📝 Conclusion

This process ensures complete, accurate size guide ingestion with full documentation and proper classification. Following this checklist prevents missed columns, incorrect classifications, and incomplete documentation.

**Always remember**: When in doubt about specificity, use `'unknown'` rather than guessing. It's better to be honest about uncertainty than to misclassify data.
