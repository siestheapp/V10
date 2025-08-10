# Tailor3 Database Restoration Guide

## Overview
This guide shows you how to restore the exported tailor3 database tables. The export includes complete data and table structures for full restoration.

## Export Contents
Each table was exported in 3 formats:
- **`.csv`** - Raw data for analysis/viewing
- **`.sql`** - Complete SQL dump for restoration
- **`_metadata.json`** - Table structure and statistics

## Restoration Methods

### Method 1: Python Script (Recommended)
Use the provided restoration script:

```bash
# Activate virtual environment
source ../venv/bin/activate

# Edit the TARGET_DB_CONFIG in restore_tailor3_database.py first
python restore_tailor3_database.py
```

### Method 2: Manual SQL Execution

#### Option A: Using psql command line
```bash
# For each table, run:
psql -h your-host -p your-port -U your-username -d your-database -f size_guides.sql
psql -h your-host -p your-port -U your-username -d your-database -f size_guide_entries.sql
psql -h your-host -p your-port -U your-username -d your-database -f garment_guides.sql
# ... continue for all tables
```

#### Option B: Using any PostgreSQL client (pgAdmin, DBeaver, etc.)
1. Connect to your target database
2. Open and execute each `.sql` file in order:
   - `brands.sql` (should be first - other tables may reference it)
   - `size_guides.sql`
   - `size_guide_entries.sql`
   - `garment_guides.sql`
   - `garment_guide_entries.sql`
   - `products.sql`
   - `user_garments.sql`
   - `admin_activity_log.sql`
   - `audit_log.sql`
   - `garment_measurement_feedback.sql`
   - `user_garment_feedback.sql`

### Method 3: CSV Import
If you only need the data (not table structure):

```sql
-- First create the table structure manually, then:
COPY table_name FROM '/path/to/table_name.csv' WITH CSV HEADER;
```

## Important Notes

### Before Restoration
1. **Backup your target database** if it contains important data
2. **Update database credentials** in the restoration script
3. **Check for naming conflicts** - the SQL files will DROP existing tables
4. **Verify PostgreSQL version compatibility** - exported from PostgreSQL 15.8

### Database Configuration
Update these values in `restore_tailor3_database.py`:
```python
TARGET_DB_CONFIG = {
    "database": "your_database_name",
    "user": "your_username", 
    "password": "your_password",
    "host": "your_host",
    "port": "your_port"
}
```

### Restoration Order
The script handles table dependencies automatically, but if restoring manually:
1. Start with `brands.sql` (referenced by other tables)
2. Then `size_guides.sql` and `garment_guides.sql`
3. Follow with dependent tables
4. Finish with log tables

## Data Summary
Based on the export:
- **size_guides**: 10 rows
- **size_guide_entries**: 199 rows  
- **garment_guides**: 4 rows
- **garment_guide_entries**: 51 rows
- **products**: 0 rows (empty)
- **user_garments**: 13 rows
- **admin_activity_log**: 201 rows
- **audit_log**: 527 rows
- **brands**: 11 rows
- **garment_measurement_feedback**: 0 rows (empty)
- **user_garment_feedback**: 36 rows

## Troubleshooting

### Common Issues
1. **Permission denied**: Ensure your user has CREATE, DROP, and INSERT permissions
2. **Table already exists**: The SQL files include `DROP TABLE IF EXISTS` statements
3. **Encoding issues**: All files are UTF-8 encoded
4. **Foreign key constraints**: May need to disable temporarily during restoration

### Verification
After restoration, verify the data:
```sql
-- Check table counts
SELECT 
    schemaname,
    tablename,
    n_tup_ins as "rows"
FROM pg_stat_user_tables 
WHERE tablename IN (
    'size_guides', 'size_guide_entries', 'garment_guides', 
    'garment_guide_entries', 'products', 'user_garments',
    'admin_activity_log', 'audit_log', 'brands',
    'garment_measurement_feedback', 'user_garment_feedback'
);
```

## Support
If you encounter issues:
1. Check the export_summary.json for export details
2. Review the *_metadata.json files for table structure
3. Ensure all dependencies are met
4. Check PostgreSQL logs for detailed error messages
