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
The backend (`ios_app/Backend/app.py`) is currently configured to use the local `tailor2` database (needs migration to tailor3).

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
- ✅ **2 users, 8+ brands, 10+ size guides**
- ✅ **Multiple user garments**
- ✅ **Proper schema with all tables**
- ✅ **Used by snapshot scripts**
- ✅ **Automatic change logging enabled**

#### **Local tailor2 (DEPRECATED)**
- ❌ **Old database**
- ❌ **Not used by current system**
- ❌ **Different schema structure**
- ❌ **Moved to `database/old_schemas/tailor2/`**

### 📚 **Related Documentation**

#### **Project Documentation**
- **`README.md`** - Main project overview and structure
- **`START.md`** - Detailed startup guide
- **`SESSION_LOG.md`** - Development session logs and changes

#### **Schema Documentation**
- **`supabase/TAILOR3_SCHEMA.md`** - Complete schema documentation for tailor3
- **`database/old_schemas/tailor2/DATABASE_SCHEMA.md`** - Old schema documentation (DEPRECATED)
- **`supabase/schema.sql`** - Raw SQL schema dump for tailor3

#### **Configuration Files**
- **`supabase/config.toml`** - Supabase local development configuration
- **`.vscode/settings.json`** - VS Code database connections (includes both databases)
- **`ios_app/App/Config.swift`** - iOS app configuration (✅ Updated for tailor2)

#### **Development Documentation**
- **`ios_app/Docs/PROJECT_STRUCTURE.md`** - Project overview (✅ Updated for tailor2)
- **`supabase/session_log_tailor3.md`** - Tailor3-specific session logs
- **`database/old_schemas/tailor2/SIZE_GUIDE_INGESTION.md`** - Size guide ingestion process (DEPRECATED)

#### **Scripts and Tools**
- **`scripts/db_snapshot.py`** - Database snapshot tool (CORRECTLY configured for tailor3)
- **`scripts/garment_input_helper.py`** - Garment input helper (CORRECTLY configured for tailor3)
- **`scripts/schema_evolution.py`** - Schema evolution tracker (INCORRECTLY configured for tailor2)
- **`scripts/db_change_logger.py`** - **ENHANCED**: Automatic change tracking with database triggers (CORRECTLY configured for tailor3)
- **`scripts/web_garment_manager.py`** - User web interface
- **`scripts/admin_garment_manager.py`** - Admin web interface

#### **Test Scripts**
- **`tests/`** - All test and debugging scripts (moved from `scripts/`)
- **`tests/README.md`** - Test scripts documentation

### 🔍 **Database Change Tracking**

#### **Automatic Change Logger** ⭐ **ENHANCED**
The change logging system now includes automatic database triggers for comprehensive tracking:

**Features:**
- ✅ **Automatic logging** - Database triggers capture all changes
- ✅ **Fast logging** - No full database snapshots required
- ✅ **Individual changes** - Track each INSERT/UPDATE/DELETE
- ✅ **User attribution** - Know which user made changes
- ✅ **Daily logs** - Organized by date
- ✅ **Statistics** - Track change patterns
- ✅ **Size guide tracking** - Automatically logs size guide additions

**Usage:**
```bash
# View recent changes
python3 scripts/db_change_logger.py recent 10

# View statistics
python3 scripts/db_change_logger.py stats

# Set up automatic logging triggers
python3 scripts/db_change_logger.py setup

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
- `log_size_guide_entry_addition(size_guide_id, size_label, entry_id, measurements)`
- `log_raw_size_guide_addition(brand_name, gender, category, raw_guide_id)`

### 🏗️ **Project Structure**

#### **Current Organization**
```
V10/
├── ios_app/                 # iOS application (SwiftUI)
├── scripts/                 # Web applications and utilities
├── tests/                   # Test and debugging scripts
├── database/                # Database-related files
│   ├── backups/             # Database backups
│   ├── snapshots/           # Current snapshots
│   └── old_schemas/         # Legacy schemas (including tailor2)
├── supabase/                # Current database (tailor3)
│   ├── schema.sql           # Current schema
│   ├── snapshots/           # Schema evolution
│   └── change_logs/         # Change tracking
├── archive/                 # Archived files
│   ├── large_files/         # Large files (>100MB)
│   └── old_code/            # Old code files
└── venv/                    # Python virtual environment
```

### 🚨 **Important Notes**

1. **Always use Supabase tailor3** for database operations
2. **Backend server currently uses tailor2** (needs migration to tailor3)
3. **Snapshot scripts are correctly configured** for Supabase tailor3
4. **Local tailor2 database has been moved** to `database/old_schemas/tailor2/`
5. **Test scripts have been moved** to the `tests/` directory
6. **Use the enhanced change logger** for comprehensive tracking
7. **Automatic triggers are set up** for size guide changes

### 🔄 **Next Steps**

1. **Backend configuration** in `ios_app/Backend/app.py` (currently uses tailor2)
2. **iOS app configuration** in `ios_app/App/Config.swift` (✅ Updated for tailor2)
3. **Project documentation** in `ios_app/Docs/PROJECT_STRUCTURE.md` (✅ Updated for tailor2)
4. **Update schema evolution script** in `scripts/schema_evolution.py`
5. **Consider removing local tailor2 database** to avoid confusion
6. **Integrate change logger** into your database operations

### 🎯 **Quick Reference**

**For Database Operations:**
- ✅ Use: `aws-0-us-east-2.pooler.supabase.com:6543` (Supabase tailor3)
- ❌ Don't use: `localhost` (local tailor2)

**For Documentation:**
- ✅ Use: `supabase/TAILOR3_SCHEMA.md`
- ❌ Don't use: `database/old_schemas/tailor2/DATABASE_SCHEMA.md`

**For Scripts:**
- ✅ Use: `scripts/db_snapshot.py`, `scripts/garment_input_helper.py`, `scripts/db_change_logger.py`
- ❌ Don't use: `scripts/schema_evolution.py` (needs update)

**For Testing:**
- ✅ Use: `tests/` directory for all test scripts
- ✅ Use: `tests/README.md` for test documentation

**For Change Tracking:**
- ✅ Use: `scripts/db_change_logger.py` (automatic with triggers)
- ⚠️ Use sparingly: `scripts/db_snapshot.py` (full snapshots)

---
*Last updated: 2025-07-04*
*Database: Supabase tailor3 (CORRECT)*
*Project: Reorganized with new structure* 