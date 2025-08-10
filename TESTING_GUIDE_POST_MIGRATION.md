# Testing Guide: Post-Migration Database Changes

**Date:** January 20, 2025  
**Purpose:** Test all fixes applied after the dual measurement system migration  

## 🎯 **TESTING RESULTS**

### ✅ **WORKING FIXES**

#### 1. **Backend Endpoint Fix** 
- **Status:** ✅ **WORKING**
- **Test garment ID:** 6 (has garment measurements)
- **Test URL:** `http://localhost:5001/garment/6/measurements`
- **Result:** Query works, returns 4 measurements

#### 2. **Admin Interface Fix**
- **Status:** ✅ **READY** 
- **Database columns:** `raw_source_text` and `screenshot_path` exist in `size_guides`
- **Result:** Admin size guide ingestion should work

#### 3. **Database Tables**
- **Status:** ✅ **ALL ACCESSIBLE**
- `size_guides`: 10 records
- `size_guide_entries`: 199 records  
- `garment_guides`: 4 records
- `garment_guide_entries`: 51 records

### ⚠️ **MINOR ISSUE FOUND**

#### Database Snapshot Script
- **Issue:** SQL syntax error in snapshot query
- **Impact:** Low (utility script, doesn't affect main app)
- **Status:** Needs small fix

## 🧪 **HOW TO TEST**

### **Method 1: Test Backend Endpoint**

1. **Start your backend:**
   ```bash
   cd /Users/seandavey/projects/V10
   source venv/bin/activate
   python src/ios_app/Backend/app.py
   ```

2. **Test the fixed endpoint:**
   ```bash
   curl http://localhost:5001/garment/6/measurements
   ```

   **Expected response:**
   ```json
   {
     "garment_id": 6,
     "measurements": {
       "body_length": "28.0\"",
       "chest_width": "21.5\"", 
       "shoulder_width": "17.5\"",
       "sleeve_length": "17.5\""
     },
     "count": 4
   }
   ```

### **Method 2: Test Admin Interface**

1. **Start admin web interface:**
   ```bash
   cd /Users/seandavey/projects/V10/scripts/admin
   python admin_garment_manager.py
   ```

2. **Visit:** `http://localhost:5000/admin/upload-size-guide`

3. **Try uploading a size guide** - should now work without `raw_size_guides` errors

### **Method 3: Test iOS App**

1. **Start backend** (Method 1 above)

2. **Open iOS app in Xcode**

3. **Test garment feedback functionality:**
   - Go to closet view
   - Try to view garment measurements  
   - Submit feedback on fit

### **Method 4: Test Database Utilities**

```bash
# Test database snapshot (after we fix the minor issue)
python scripts/database/db_snapshot.py

# Test change logger
python -c "
import sys
sys.path.append('scripts/database')
from db_change_logger import log_size_guide_addition
log_size_guide_addition('Test Brand', 'Male', 'Tops', 999)
print('✅ Change logger works')
"
```

## 🔍 **WHAT TO LOOK FOR**

### **✅ Success Indicators:**
- Backend starts without errors
- Garment measurements endpoint returns data
- Admin interface loads without database errors
- iOS app can view garment measurements
- No "table does not exist" errors

### **❌ Failure Indicators:**
- `relation "raw_size_guides" does not exist` errors
- `relation "garment_measurements" does not exist` errors
- Empty responses from measurement endpoints
- Admin interface crashes on size guide upload

## 🚨 **EMERGENCY ROLLBACK**

If critical issues are found:

```bash
# Restore from backup (if needed)
# You have: ~/Downloads/tailor3_backup_Aug82025.dump

# Or revert specific fixes:
git checkout HEAD~1 -- src/ios_app/Backend/app.py
git checkout HEAD~1 -- scripts/admin/admin_garment_manager.py
```

## 📊 **TESTING CHECKLIST**

- [ ] Backend starts successfully
- [ ] `/garment/6/measurements` returns measurements
- [ ] Admin interface loads without errors  
- [ ] iOS app displays garment measurements
- [ ] No `raw_size_guides` errors in logs
- [ ] Size guide ingestion works via admin

## 🎯 **NEXT STEPS AFTER TESTING**

1. **If all tests pass:** Add `garment_guide_id` support to complete the dual system
2. **If issues found:** Review specific failures and apply targeted fixes
3. **iOS compatibility:** Verify app works with updated backend responses

---

**Quick Test Command:**
```bash
curl http://localhost:5001/garment/6/measurements
```
**Expected:** JSON response with 4 measurements, no errors
