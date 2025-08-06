# Size Recommendation System - Complete Technical Guide

*Last Updated: August 2025*

## 🎯 Overview

The Sies size recommendation system is a sophisticated multi-dimensional fit analysis engine that provides personalized size recommendations by analyzing garment measurements against a user's established fit preferences derived from their closet data.

## 📚 Related Documentation

### **Core System Files:**
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Project overview, ports, and common operations
- **[TAILOR3_SCHEMA.md](database/TAILOR3_SCHEMA.md)** - Complete database schema with constraints and relationships
- **[fitlogic.md](fitlogic.md)** - Fit zone system architecture and shopping integration
- **[session_log_tailor3.md](database/session_log_tailor3.md)** - Database evolution and ingestion history

### **Database Documentation:**
- **[DATABASE_EVOLUTION_SUMMARY.md](database/DATABASE_EVOLUTION_SUMMARY.md)** - Schema changes over time
- **[DATABASE_CONFIG.md](DATABASE_CONFIG.md)** - Connection details and setup
- **[VIEWS_CREATED.md](VIEWS_CREATED.md)** - Database views and their purposes

### **Development Tools:**
- **`scripts/brand_completeness_checker.py`** - Check brand size guide coverage
- **`scripts/web_garment_manager.py`** - User closet management (port 5001)
- **`scripts/admin_garment_manager.py`** - Brand/category admin (port 5002)
- **`src/ios_app/Backend/app.py`** - Main Flask API (port 8006)

## 📊 Database Architecture

### Core Tables

#### **`user_fit_zones`** - Pre-computed Fit Preferences (PRIMARY DATA SOURCE)
*Note: There are TWO fit zone tables - see Dual Fit Zone System section below*
```sql
-- User 1's stored fit zones (computed from closet analysis)
SELECT * FROM user_fit_zones WHERE user_id = 1;

id | user_id | category | dimension | tight_min | tight_max | good_min | good_max | relaxed_min | relaxed_max | confidence_score | data_points_count | last_updated
---|---------|----------|-----------|-----------|-----------|----------|----------|-------------|-------------|------------------|-------------------|-------------
1  | 1       | Tops     | chest     | 37.50     | 39.00     | 39.50    | 42.50    | 42.00       | 45.50       | 0.80             | 10                | 2025-08-01
6  | 1       | Tops     | neck      | NULL      | NULL      | 16.00    | 16.50    | NULL        | NULL        | 1.00             | 4                 | 2025-08-01  
7  | 1       | Tops     | sleeve    | NULL      | NULL      | 33.50    | 36.00    | NULL        | NULL        | 1.00             | 8                 | 2025-08-01
```

**Key Points:**
- **Pre-computed** from user's closet feedback (not calculated on-demand)
- **Three fit zones** per dimension: tight, good (standard), relaxed
- **High confidence** chest zone (0.80) based on 10 garments
- **Perfect confidence** neck/sleeve (1.00) based on 4-8 garments
- **Performance optimized** - fast database lookup vs. expensive calculation

#### **`user_garments`** - User's Closet Data
```sql
-- User 1's actual garments with feedback
SELECT ug.product_name, ug.size_label, b.name as brand, fc.feedback_text 
FROM user_garments ug 
JOIN brands b ON ug.brand_id = b.id 
LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id AND ugf.dimension = 'overall'
LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id 
WHERE ug.user_id = 1 AND ug.owns_garment = true;

Cotton piqué-stitch crewneck sweater | L  | J.Crew          | Good Fit
Burgundy micro-check button-down     | M  | Theory          | Good Fit  
Blue polo with front pocket          | M  | Theory          | Good Fit
Soft Wash Long-Sleeve T-Shirt        | L  | Banana Republic | Good Fit
Evolution Long-Sleeve Polo Shirt     | M  | Lululemon       | Good Fit
...
```

#### **`size_guide_entries`** - Brand Size Charts
```sql
-- J.Crew size guide (what we compare against)
SELECT size_label, chest_min, chest_max, neck_min, neck_max, sleeve_min, sleeve_max 
FROM size_guide_entries sge 
JOIN size_guides sg ON sge.size_guide_id = sg.id 
JOIN brands b ON sg.brand_id = b.id 
WHERE b.name = 'J.Crew' AND size_label IN ('M', 'L');

size_label | chest_min | chest_max | neck_min | neck_max | sleeve_min | sleeve_max
-----------|-----------|-----------|----------|----------|------------|------------
L          | 41        | 43        | 16       | 16.5     | 34         | 35
M          | 38        | 40        | 15       | 15.5     | 33         | 34
```

#### **`body_measurements`** - Direct Body Measurements (EMPTY for User 1)
```sql
-- User 1 has NO direct body measurements - system relies on fit zones instead
SELECT * FROM body_measurements WHERE user_id = 1;
-- (0 rows) - This is normal! System uses garment feedback, not body measurements
```

## 🔄 Size Recommendation Flow

### **Step 1: URL Processing**
```
POST /garment/size-recommendation
{
  "product_url": "https://www.jcrew.com/p/mens-shirts/...",
  "user_id": "1", 
  "fit_preference": "Standard"
}
```

**Actions:**
1. **Log scan action** in `user_actions` table
2. **Extract brand** from URL → "J.Crew" (brand_id: X)
3. **Validate brand** exists in database

### **Step 2: Analyzer Selection** 
**Primary Engine:** `SimpleMultiDimensionalAnalyzer` (practical, fast)
- Alternative: `MultiDimensionalFitAnalyzer` (comprehensive, slower)
- Alternative: `UnifiedFitRecommendationEngine` (fit-zone focused)

### **Step 3: User Profile Loading** ⚡ **CACHED LOOKUP**
```python
# SimpleMultiDimensionalAnalyzer._get_user_dimension_profiles()

# FAST PATH: Get pre-computed fit zones from database
cached_data = fit_zone_service.get_stored_fit_zones(user_id=1, category="Tops")

# Returns from user_fit_zones table:
{
  'chest': {
    'tight': {'min': 37.5, 'max': 39.0},
    'good': {'min': 39.5, 'max': 42.5},    # ← Primary fit zone
    'relaxed': {'min': 42.0, 'max': 45.5}
  },
  'neck': {
    'good': {'min': 16.0, 'max': 16.5}     # ← Only good zone available
  },
  'sleeve': {
    'good': {'min': 33.5, 'max': 36.0}     # ← Only good zone available  
  }
}
```

**Performance Note:** If cached data exists, **expensive closet analysis is skipped entirely**!

## 🔄 Dual Fit Zone System

### **Two Fit Zone Tables Explained:**

#### **1. `user_fit_zones`** (Older System - Aug 1, 2025)
```sql
-- Computed fit zones from FitZoneService
SELECT * FROM user_fit_zones WHERE user_id = 1;
-- Returns: chest (37.5-45.5 range), neck (16.0-16.5), sleeve (33.5-36.0)
```
- **Created:** 2025-08-01 (4 days ago)
- **Used by:** Size recommendation engine (`SimpleMultiDimensionalAnalyzer`)
- **Updated by:** `FitZoneService.calculate_and_store_fit_zones()`
- **Structure:** Single row per dimension with tight/good/relaxed ranges
- **Data Source:** Computed from `user_garments` + `user_garment_feedback`

#### **2. `fit_zones`** (Newer System - Aug 4, 2025) 
```sql  
-- Manually established fit zones (NOT from fitzonetracker.md directly)
SELECT * FROM fit_zones WHERE user_id = 1;
-- Returns: chest tight/good/relaxed zones, neck good, sleeve good
```
- **Created:** 2025-08-04 (yesterday) - NEWER!
- **Used by:** Some shopping/analysis functions (`get_fit_zones_from_database()`)
- **Structure:** Separate rows per fit type (tight/good/relaxed)
- **Source:** Manual SQL INSERT based on analysis documented in `fitzonetracker.md`
- **Notes:** `fitzonetracker.md` is a TRACKING document, not the data source - the fit zones were manually inserted via SQL based on the analysis tracked in that file

### **Current System Status:**
- ✅ **Size recommendations** use `user_fit_zones` (computed system)
- ✅ **Some analysis functions** use `fit_zones` (manual system)
- ⚠️ **Data divergence possible** - two sources of truth for same data
- 📝 **Important:** `fitzonetracker.md` is a TRACKING document, not a data source
- 🎯 **Need clarification:** Which system should be primary going forward?

### **Data Comparison:**
Both tables have similar data but different structures:
- **`user_fit_zones`**: chest 37.5-45.5, neck 16.0-16.5, sleeve 33.5-36.0
- **`fit_zones`**: chest tight 36.0-39.5, good 39.5-42.5, relaxed 43.0-45.5

### **Step 4: Brand Size Guide Loading**
```python
# Get J.Crew size guide from size_guide_entries
size_entries = [
  {
    'size_label': 'L',
    'chest_min': 41, 'chest_max': 43,      # ← 42" average
    'neck_min': 16, 'neck_max': 16.5,      # ← 16.25" average  
    'sleeve_min': 34, 'sleeve_max': 35     # ← 34.5" average
  },
  {
    'size_label': 'M', 
    'chest_min': 38, 'chest_max': 40,      # ← 39" average
    'neck_min': 15, 'neck_max': 15.5,      # ← 15.25" average
    'sleeve_min': 33, 'sleeve_max': 34     # ← 33.5" average
  }
]
```

### **Step 5: Multi-Dimensional Analysis**
**For each size (L, M), analyze each dimension:**

#### **Size L Analysis:**
```python
# Chest: 42" (average of 41-43) vs user's good zone (39.5-42.5)
chest_fit = analyze_dimension('chest', 42.0, user_zones['chest']['good'])
# Result: ✅ FITS (42.0 within 39.5-42.5 range)

# Neck: 16.25" vs user's good zone (16.0-16.5) 
neck_fit = analyze_dimension('neck', 16.25, user_zones['neck']['good'])
# Result: ✅ FITS (16.25 within 16.0-16.5 range)

# Sleeve: 34.5" vs user's good zone (33.5-36.0)
sleeve_fit = analyze_dimension('sleeve', 34.5, user_zones['sleeve']['good'])  
# Result: ✅ FITS (34.5 within 33.5-36.0 range)

# Overall Score: Weighted average
# (1.0 * 0.9) + (0.8 * 0.9) + (0.7 * 0.9) = High score!
```

#### **Size M Analysis:**
```python
# Chest: 39" vs user's good zone (39.5-42.5)
# Result: ❌ TIGHT (39" < 39.5 minimum)

# Neck: 15.25" vs user's good zone (16.0-16.5)  
# Result: ❌ TIGHT (15.25" < 16.0 minimum)

# Sleeve: 33.5" vs user's good zone (33.5-36.0)
# Result: ✅ FITS (exactly at minimum)

# Overall Score: Lower due to chest/neck concerns
```

### **Step 6: Confidence Calculation**
```python
# Enhanced confidence considering:
confidence_info = calculate_confidence_tier(
    overall_fit_score=0.85,                    # High fit score
    reference_garments={'jcrew_l': {...}},     # Same-brand reference  
    dimensions_analyzed=3,                     # All 3 dimensions available
    brand_name="J.Crew"
)

# Result: "Great Fit" (85% confidence with same-brand reference boost)
```

### **Step 7: Human Explanation Generation**
```python
human_explanation = generate_human_readable_explanation(
    analysis=size_l_analysis,
    reference_garments={'jcrew_l': 'Cotton crewneck sweater'},
    brand_name="J.Crew"
)

# Result: "Analyzed chest, neck, sleeve - matches your J.Crew L"
```

## 📱 API Response Structure

### **Final Response:**
```json
{
  "productUrl": "https://www.jcrew.com/p/mens-shirts/...",
  "brand": "J.Crew",
  "analysisType": "multi_dimensional",
  "dimensionsAnalyzed": ["chest", "neck", "sleeve"],
  "recommendedSize": "L",
  "recommendedFitScore": 0.85,
  "confidence": 0.87,
  "reasoning": "Size L fits well across all analyzed dimensions",
  
  // 🎯 ENHANCED UX FIELDS
  "confidenceTier": {
    "tier": "good",
    "label": "Great Fit", 
    "icon": "✅",
    "color": "green",
    "description": "This will fit you well"
  },
  "humanExplanation": "Analyzed chest, neck, sleeve - matches your J.Crew L",
  
  "referenceGarments": {
    "jcrew_l": {
      "brand": "J.Crew",
      "size": "L", 
      "confidence": 1.0,
      "product": "Cotton piqué-stitch crewneck sweater"
    }
  },
  
  "allSizes": [
    {
      "size": "L",
      "fitScore": 0.85,
      "measurementSummary": "chest: 41-43, neck: 16-16.5, sleeve: 34-35",
      "concerns": [],
      "fits_all_dimensions": true
    },
    {
      "size": "M", 
      "fitScore": 0.45,
      "measurementSummary": "chest: 38-40, neck: 15-15.5, sleeve: 33-34",
      "concerns": ["chest too tight", "neck too tight"],
      "fits_all_dimensions": false
    }
  ]
}
```

## 🚀 Performance Optimizations

### **Database Caching Strategy:**
1. **Fit zones pre-computed** and stored in `user_fit_zones` 
2. **Fast lookups** via indexed queries (`idx_user_fit_zones_lookup`)
3. **Expensive closet analysis avoided** when cache exists
4. **Event-driven updates** when user adds new garments

### **Analysis Engine Selection:**
- **SimpleMultiDimensionalAnalyzer**: Fast, practical (current default)
- **MultiDimensionalFitAnalyzer**: Comprehensive, slower (fallback)
- **UnifiedFitRecommendationEngine**: Fit-zone focused (specialized use)

### **Confidence Boosting:**
- **Same brand reference**: 2x weight boost (J.Crew → J.Crew)
- **Multiple dimensions**: Higher confidence with more data points
- **User satisfaction**: Loved garments weighted higher

## 🔧 System Dependencies

### **Key Services:**
- **`FitZoneService`**: Manages cached fit zone data
- **`BodyMeasurementEstimator`**: Fallback for missing fit zones  
- **Brand URL extraction**: Maps URLs to brand IDs
- **Size guide lookup**: Gets garment measurements

### **Database Views & Indexes:**
- `idx_user_fit_zones_lookup`: Fast fit zone retrieval
- `user_garment_feedback_view`: Combined garment + feedback data
- Audit triggers on all measurement tables

## 🎯 Current State (User 1)

### **Stored Data:**
- ✅ **13 garments** with feedback across 6 brands
- ✅ **Pre-computed fit zones** for chest, neck, sleeve
- ✅ **High confidence** zones (10 chest, 8 sleeve, 4 neck data points)
- ❌ **No direct body measurements** (system doesn't need them!)

### **Recommendation Quality:**
- **J.Crew recommendations**: Excellent (same-brand reference)
- **Theory recommendations**: Good (2 reference garments) 
- **New brand recommendations**: Fair (cross-brand inference)

### **Performance:**
- **Sub-second response** time (cached fit zones)
- **Multi-dimensional analysis** across 3+ dimensions
- **Honest confidence reporting** based on actual data quality

---

## 🔍 Troubleshooting Guide

### **No Recommendations Returned:**
1. Check if brand exists: `SELECT * FROM brands WHERE name = 'BrandName'`
2. Check size guide exists: `SELECT * FROM size_guide_entries WHERE size_guide_id IN (SELECT id FROM size_guides WHERE brand_id = X)`
3. Check user fit zones: `SELECT * FROM user_fit_zones WHERE user_id = X`

### **Low Confidence Recommendations:**
1. Check fit zone data points: Low `data_points_count` = lower confidence
2. Check reference garments: No same-brand references = lower confidence  
3. Check dimension coverage: Missing dimensions = lower confidence

### **Performance Issues:**
1. Verify fit zones are cached: `user_fit_zones` table populated
2. Check for expensive fallback calculations in logs
3. Monitor database query performance on size guide lookups

## 📊 Measurement Quality Tracking

### **`measurement_methodology`** - Data Quality Assurance
```sql
-- Track measurement quality for each size guide entry
SELECT * FROM measurement_methodology LIMIT 3;

id | size_guide_entry_id | dimension | methodology_type | measurement_confidence | reliability_score
11 | 1                   | chest     | native          | 1.00                   | 1.00
12 | 2                   | chest     | native          | 1.00                   | 1.00  
13 | 3                   | chest     | native          | 1.00                   | 1.00
```

**Quality Tracking Features:**
- **`methodology_type`**: native, converted, estimated, interpolated
- **`measurement_confidence`**: 0.0-1.0 score for data reliability
- **`reliability_score`**: Brand-specific reliability weighting
- **`expected_error_margin`**: Known measurement tolerance
- **`conversion_notes`**: Documentation of any data transformations

### **Database Views for Analysis:**
- **`brand_measurement_methodology_view`** - Measurement quality by brand
- **`brand_methodology_summary`** - Aggregated quality metrics
- **`brand_user_measurement_comparison`** - Coverage analysis
- **`brand_measurement_coverage_summary`** - Completeness statistics

## 🛠️ System Architecture Components

### **Service Layer:**
- **`FitZoneService`** - Manages cached fit zone data
- **`BodyMeasurementEstimator`** - Fallback body measurements from garment data
- **`SimpleMultiDimensionalAnalyzer`** - Primary recommendation engine
- **`DirectGarmentComparator`** - Direct garment-to-garment comparison
- **`UnifiedFitRecommendationEngine`** - Fit-zone focused recommendations

### **Data Pipeline:**
1. **Raw Ingestion** → `raw_size_guides` (screenshots, raw data)
2. **Standardization** → `size_guides` + `size_guide_entries` (clean measurements)
3. **Quality Tracking** → `measurement_methodology` (reliability scoring)
4. **User Feedback** → `user_garment_feedback` (fit experience)
5. **Fit Zone Calculation** → `user_fit_zones` (personalized ranges)
6. **Recommendation** → API response (size + confidence + explanation)

### **Audit & Tracking:**
- **`user_actions`** - Complete audit trail with undo capability
- **`admin_activity_log`** - Admin changes to size guides/brands
- **`standardization_log`** - Data cleaning and unit conversions
- **All tables** have audit triggers for change tracking

## 🔍 Integration Points

### **Frontend Integration:**
- **iOS App** (`src/ios_app/V10/`) - SwiftUI scan and shop interfaces
- **Web Closet Manager** (port 5001) - User garment management
- **Admin Interface** (port 5002) - Brand/size guide management

### **API Endpoints:**
- **`POST /garment/size-recommendation`** - Main recommendation endpoint
- **`GET /shop/recommendations`** - Shopping filter integration
- **`GET /user/{id}/measurements`** - User profile data
- **`POST /garments/submit`** - Add garments with feedback

### **Database Connections:**
- **Supabase PostgreSQL** (`tailor3`) - Primary database
- **Connection:** `aws-0-us-east-2.pooler.supabase.com:6543`
- **Audit logging** via triggers on all measurement tables

## 📈 Historical Evolution

### **Key Milestones (from `session_log_tailor3.md`):**
- **2025-06-29:** Initial tailor3 schema with Lululemon/Patagonia data
- **2025-06-30:** Added hip measurements, NN.07 product-level guides
- **2025-07-25:** Measurement methodology tracking system
- **2025-08-01:** User fit zones calculation and storage
- **2025-08-04:** Dual fit zone system (legacy + new)

### **Data Growth:**
- **Brands:** 6 active brands (J.Crew, Theory, Banana Republic, etc.)
- **Size Guides:** Multi-dimensional measurements (chest, neck, sleeve, hip)
- **User Data:** 13 garments with feedback across multiple brands
- **Fit Zones:** Pre-computed for instant recommendations

---

This system represents a sophisticated, production-ready recommendation engine that balances accuracy, performance, and user experience through intelligent caching, multi-dimensional analysis, and comprehensive quality tracking.