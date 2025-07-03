# V10 Database Configuration

## 🎯 **CORRECT DATABASE: Supabase tailor3**

**The V10 project uses the Supabase-hosted `tailor3` database, NOT the local `tailor2` database.**

### 📍 **Current Configuration**

#### **Production Database (Supabase tailor3)**
- **Host**: `aws-0-us-east-2.pooler.supabase.com:6543`
- **Database**: `postgres`
- **User**: `postgres.lbilxlkchzpducggkrxx`
- **Password**: `efvTower12`
- **Connection Type**: Pooled connection

#### **Local Database (tailor2) - DEPRECATED**
- **Host**: `localhost`
- **Database**: `tailor2`
- **User**: `seandavey`
- **Password**: `""`
- **Status**: ❌ **DO NOT USE** - This is the old database

### 🔧 **Configuration Files**

#### **Backend Configuration**
The current backend (`V10/V10/Backend/app.py`) is **incorrectly** configured to use `tailor2`. It should be updated to use the Supabase `tailor3` connection.

#### **Correct Configuration (for reference)**
```python
# Database configuration - CORRECT (Supabase tailor3)
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx", 
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}
```

### 📊 **Database Status**

#### **Supabase tailor3 (CORRECT)**
- ✅ **Active and current**
- ✅ **2 users, 5 brands, 5 size guides**
- ✅ **1 user garment**
- ✅ **Proper schema with all tables**
- ✅ **Used by snapshot scripts**

#### **Local tailor2 (DEPRECATED)**
- ❌ **Old database**
- ❌ **Not used by current system**
- ❌ **Different schema structure**

### 📚 **Related Documentation**

#### **Schema Documentation**
- **`supabase/TAILOR3_SCHEMA.md`** - Complete schema documentation for tailor3
- **`tailor2/DATABASE_SCHEMA.md`** - Old schema documentation (DEPRECATED)
- **`supabase/schema.sql`** - Raw SQL schema dump for tailor3

#### **Configuration Files**
- **`supabase/config.toml`** - Supabase local development configuration
- **`.vscode/settings.json`** - VS Code database connections (includes both databases)
- **`V10/V10/App/Config.swift`** - iOS app configuration (mentions tailor2 - needs update)

#### **Development Documentation**
- **`V10/V10/Docs/PROJECT_STRUCTURE.md`** - Project overview (mentions tailor2 - needs update)
- **`SESSION_LOG.md`** - Development session logs and changes
- **`supabase/session_log_tailor3.md`** - Tailor3-specific session logs
- **`tailor2/SIZE_GUIDE_INGESTION.md`** - Size guide ingestion process (DEPRECATED)

#### **Scripts and Tools**
- **`scripts/db_snapshot.py`** - Database snapshot tool (CORRECTLY configured for tailor3)
- **`scripts/garment_input_helper.py`** - Garment input helper (CORRECTLY configured for tailor3)
- **`scripts/schema_evolution.py`** - Schema evolution tracker (INCORRECTLY configured for tailor2)
- **`scripts/db_change_logger.py`** - **NEW**: Lightweight change tracking (CORRECTLY configured for tailor3)

### 🔍 **Database Change Tracking**

#### **Lightweight Change Logger** ⭐ **NEW**
Instead of creating full snapshots every time, use the lightweight change logger:

**Features:**
- ✅ **Fast logging** - No full database snapshots
- ✅ **Individual changes** - Track each INSERT/UPDATE/DELETE
- ✅ **User attribution** - Know which user made changes
- ✅ **Daily logs** - Organized by date
- ✅ **Statistics** - Track change patterns

**Usage:**
```bash
# View recent changes
python3 scripts/db_change_logger.py recent 10

# View statistics
python3 scripts/db_change_logger.py stats

# In your code
from db_change_logger import log_user_creation, log_garment_addition
log_user_creation("user@example.com", "Male", 123)
```

**Log Files:**
- `supabase/change_logs/db_changes_YYYY-MM-DD.jsonl` - Daily logs
- `supabase/change_logs/db_changes_summary.jsonl` - All changes

**Available Functions:**
- `log_user_creation(email, gender, user_id)`
- `log_garment_addition(user_id, brand_name, product_name, size_label, garment_id)`
- `log_feedback_submission(user_id, garment_id, dimension, feedback_text)`
- `log_brand_addition(brand_name, brand_id)`
- `log_size_guide_addition(brand_name, gender, category, size_guide_id)`

### 🚨 **Important Notes**

1. **Always use Supabase tailor3** for database operations
2. **The backend server needs to be updated** to use the correct database
3. **Snapshot scripts are correctly configured** for Supabase tailor3
4. **Local tailor2 database should be ignored** or removed
5. **Several documentation files still reference tailor2** and need updates
6. **Use the change logger** for lightweight tracking instead of full snapshots

### 🔄 **Next Steps**

1. **Update backend configuration** in `V10/V10/Backend/app.py`
2. **Update iOS app configuration** in `V10/V10/App/Config.swift`
3. **Update project documentation** in `V10/V10/Docs/PROJECT_STRUCTURE.md`
4. **Update schema evolution script** in `scripts/schema_evolution.py`
5. **Consider removing local tailor2 database** to avoid confusion
6. **Integrate change logger** into your database operations

### 🎯 **Quick Reference**

**For Database Operations:**
- ✅ Use: `aws-0-us-east-2.pooler.supabase.com:6543` (Supabase tailor3)
- ❌ Don't use: `localhost` (local tailor2)

**For Documentation:**
- ✅ Use: `supabase/TAILOR3_SCHEMA.md`
- ❌ Don't use: `tailor2/DATABASE_SCHEMA.md`

**For Scripts:**
- ✅ Use: `scripts/db_snapshot.py`, `scripts/garment_input_helper.py`, `scripts/db_change_logger.py`
- ❌ Don't use: `scripts/schema_evolution.py` (needs update)

**For Change Tracking:**
- ✅ Use: `scripts/db_change_logger.py` (lightweight)
- ⚠️ Use sparingly: `scripts/db_snapshot.py` (full snapshots)

---
*Last updated: 2025-07-02*
*Database: Supabase tailor3 (CORRECT)* 