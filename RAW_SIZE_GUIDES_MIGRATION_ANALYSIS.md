# Raw Size Guides References Analysis

**Generated:** January 20, 2025  
**Purpose:** Document all references to `raw_size_guides` table before migration to dual measurement system  
**Status:** Table was DROPPED in August 9, 2025 dual measurement system evolution  

## 🚨 CRITICAL FINDINGS

The `raw_size_guides` table was **completely dropped** and its functionality migrated to:
- `size_guides.raw_source_text` column
- `size_guides.screenshot_path` column

## 📋 ACTIVE CODE REFERENCES THAT NEED UPDATES

### 1. **Database Scripts (HIGH PRIORITY)**

#### `./scripts/database/db_snapshot.py:172`
- **Issue:** Still includes `raw_size_guides` in table list for snapshots
- **Fix:** Remove from table list since it no longer exists
- **Impact:** Snapshot generation will fail

#### `./scripts/database/db_change_logger.py:185`
- **Issue:** Still monitoring `raw_size_guides` for changes
- **Fix:** Remove from monitored tables list
- **Impact:** Change logging may fail or throw errors

### 2. **Admin Interface (CRITICAL)**

#### `./scripts/admin/admin_garment_manager.py:437`
```python
INSERT INTO raw_size_guides (brand_id, gender, category_id, fit_type, source_url, screenshot_path, raw_text, uploaded_by)
```
- **Issue:** Admin interface tries to insert into non-existent table
- **Fix:** Update to insert into `size_guides` with new column structure
- **Impact:** Size guide ingestion completely broken

#### `./scripts/admin/brand_completeness_checker.py:174-175`
```python
print("   # Update raw_size_guides with screenshot path:")
print(f"   UPDATE raw_size_guides SET screenshot_path = 'screenshot_url' WHERE brand_id = {brand_id};")
```
- **Issue:** Generates SQL commands for non-existent table
- **Fix:** Update to use `size_guides.screenshot_path`
- **Impact:** Brand completeness checking broken

## 🔄 MIGRATION MAPPING

### Old Structure → New Structure
```sql
-- OLD (DROPPED)
raw_size_guides.raw_text → size_guides.raw_source_text
raw_size_guides.screenshot_path → size_guides.screenshot_path
raw_size_guides.source_url → size_guides.source_url (already existed)

-- NEW DUAL SYSTEM
size_guides (body measurements) ← migrated raw_size_guides data
garment_guides (garment measurements) ← uses same column structure
```

## 🎯 REQUIRED FIXES

### 1. Database Scripts
- [ ] Update `db_snapshot.py` - remove `raw_size_guides` from table list
- [ ] Update `db_change_logger.py` - remove from monitored tables

### 2. Admin Interface  
- [ ] Update `admin_garment_manager.py` - change INSERT to use `size_guides`
- [ ] Update `brand_completeness_checker.py` - change UPDATE commands

### 3. Query Updates
All queries should now use:
```sql
-- Instead of: SELECT * FROM raw_size_guides WHERE brand_id = ?
-- Use: SELECT raw_source_text, screenshot_path FROM size_guides WHERE brand_id = ?
```

## ⚠️ IMPACT ASSESSMENT

### **BROKEN FUNCTIONALITY:**
1. **Size guide ingestion via admin interface** - completely broken
2. **Database snapshots** - will fail when trying to query dropped table
3. **Change logging** - may throw errors on table monitoring
4. **Brand completeness checking** - generates invalid SQL

### **WORKING FUNCTIONALITY:**
1. **Main app endpoints** - don't directly reference `raw_size_guides`
2. **iOS app** - no direct database table references
3. **User feedback system** - uses `user_garment_feedback` (still exists)

## 📊 TOTAL REFERENCES FOUND

- **Total references in codebase:** 2,370 lines
- **Active code references:** 5 locations
- **Critical fixes needed:** 4 files

## 🚀 NEXT STEPS

1. **IMMEDIATE:** Fix admin interface (`admin_garment_manager.py`)
2. **HIGH:** Update database utility scripts
3. **MEDIUM:** Update brand completeness checker
4. **TEST:** Verify all functionality works with new structure

---

**Note:** This analysis excludes documentation files, SQL dumps, and archived code. Focus on the 4 active code files identified above.