# V10 Project

A comprehensive garment fitting and recommendation system with iOS app and web admin interface.

## 🏗️ Project Structure

```
V10/
├── ios_app/                 # iOS application (SwiftUI)
├── scripts/                 # Web applications and utilities
│   ├── web_garment_manager.py      # User web interface
│   ├── admin_garment_manager.py    # Admin web interface
│   ├── db_change_logger.py         # Database change tracking
│   ├── db_snapshot.py              # Database snapshots
│   └── templates/                  # Web templates
├── tests/                   # Test and debugging scripts
├── database/                # Database-related files
│   ├── backups/             # Database backups
│   ├── snapshots/           # Current snapshots
│   └── old_schemas/         # Legacy schemas
├── supabase/                # Current database (tailor3)
│   ├── schema.sql           # Current schema
│   ├── snapshots/           # Schema evolution
│   └── change_logs/         # Change tracking
├── archive/                 # Archived files
│   ├── large_files/         # Large files (>100MB)
│   └── old_code/            # Old code files
└── venv/                    # Python virtual environment
```

## 🚀 Quick Start

1. **Start the web interfaces:**
   ```bash
   ./start_server.sh
   ```

2. **Access the applications:**
   - User Interface: http://localhost:5001
   - Admin Interface: http://localhost:5002 (admin/admin123)

3. **iOS App:**
   - Open `ios_app/V10.xcodeproj` in Xcode
   - Build and run on device or simulator

## 📊 Database

- **Current Schema:** tailor3 (Supabase)
- **Schema File:** `supabase/schema.sql`
- **Change Tracking:** Automatic via database triggers
- **Snapshots:** Daily automatic snapshots

## 🔧 Development

### Web Development
- **User Interface:** Flask app for garment management
- **Admin Interface:** Flask app for brand/category management
- **Templates:** Bootstrap-based responsive design

### iOS Development
- **Framework:** SwiftUI
- **Features:** Garment scanning, fit feedback, size guides
- **Backend:** Supabase integration

### Database Management
- **Change Logging:** Automatic tracking of all changes
- **Schema Evolution:** Version-controlled schema changes
- **Snapshots:** Point-in-time database captures

## 📁 Key Files

- `START.md` - Detailed startup guide
- `DATABASE_CONFIG.md` - Database configuration
- `SESSION_LOG.md` - Development session history
- `scripts/db_change_logger.py` - Change tracking system
- `supabase/schema.sql` - Current database schema

## 🧪 Testing

Test scripts are organized in the `tests/` directory:
- Brand dimension testing
- Garment detail testing
- Measurement linking
- Feedback system testing

## 📈 Monitoring

- **Change Logs:** `supabase/change_logs/`
- **Database Snapshots:** `supabase/snapshots/`
- **Session Log:** `SESSION_LOG.md`

## 🔄 Workflow

1. **Development:** Use scripts in `scripts/` directory
2. **Testing:** Run tests from `tests/` directory
3. **Database Changes:** Automatically logged via triggers
4. **Deployment:** Use current schema in `supabase/schema.sql`

## 📝 Notes

- All database changes are automatically tracked
- Schema evolution is version-controlled
- Large files are archived in `archive/large_files/`
- Old schemas preserved in `database/old_schemas/` 