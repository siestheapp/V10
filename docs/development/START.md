# V10 Project Startup Guide

This guide provides step-by-step instructions for running the V10 tailor/fit recommendation system.

## Prerequisites

- **Database:** Supabase "tailor3" database (configured and running)
- **Python:** Python 3.x with virtual environment support
- **Terminal:** macOS Terminal or similar

## Pre-Start Server Check

Before starting the servers, check if ports 5001 and 5002 are already in use:

### 1. Check Port Status
```bash
# Quick check - shows process IDs if ports are in use
lsof -ti:5001 -ti:5002

# Detailed check - shows what's running on each port
lsof -i:5001 -i:5002
```

**Expected Output if ports are free:**
- No output (empty response)

**If ports are in use, you'll see:**
```
COMMAND   PID      USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
Python  63841 seandavey    6u  IPv4 0xd9628a056cad0dec      0t0  TCP *:rfe (LISTEN)
Python  67536 seandavey    6u  IPv4 0xd2e51cca3b607357      0t0  TCP *:commplex-link (LISTEN)
```

### 2. Clean Up Existing Servers (if needed)
If you see processes running on ports 5001/5002, you have three options:

#### Option A: Kill All Python Processes on These Ports (Recommended)
```bash
# Kill all processes on both ports
lsof -ti:5001 -ti:5002 | xargs kill -9
```

#### Option B: Kill Specific Processes
```bash
# Kill specific process (replace PID with actual process ID)
kill -9 63841
kill -9 67536
```

#### Option C: Kill All Python Processes (Nuclear Option)
```bash
# WARNING: This kills ALL Python processes
pkill -f python
```

### 3. Verify Ports Are Clear
```bash
# Should return no output if successful
lsof -ti:5001 -ti:5002
```

## Quick Start

### 1. Navigate to Project Directory
```bash
cd /Users/seandavey/projects/V10
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```
You should see `(venv)` appear in your terminal prompt:
```bash
(venv)seandavey@MacBook-Air V10 %
```

### 3. Start the Web Interfaces

#### Option A: User Interface Only (Port 5001)
```bash
python scripts/web_garment_manager.py
```

#### Option B: Admin Interface Only (Port 5002)
```bash
python scripts/admin_garment_manager.py
```

#### Option C: Both Interfaces (Recommended)
Open two terminal windows/tabs:

**Terminal 1 - User Interface:**
```bash
cd /Users/seandavey/projects/V10
source venv/bin/activate
python scripts/web_garment_manager.py
```

**Terminal 2 - Admin Interface:**
```bash
cd /Users/seandavey/projects/V10
source venv/bin/activate
python scripts/admin_garment_manager.py
```

## Available Endpoints

### User Interface (Port 5001)
Access at: http://localhost:5001

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard - view users, recent garments, brands |
| `/add_garment` | GET/POST | Add new garment to user's closet |
| `/garment/<id>` | GET | View specific garment details and feedback |
| `/add_feedback/<id>` | POST | Add manual feedback for a garment |
| `/progressive_feedback/<id>` | GET | Progressive feedback form (5-point satisfaction scale) |
| `/submit_progressive_feedback/<id>` | POST | Submit progressive feedback |
| `/api/feedback_codes` | GET | API endpoint for feedback codes |

### Admin Interface (Port 5002)
Access at: http://localhost:5002

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/login` | GET/POST | Admin login (username: admin, password: admin123) |
| `/admin/dashboard` | GET | Admin dashboard with system overview |
| `/admin/brands` | GET/POST | Manage brands (view, add, edit) |
| `/admin/categories` | GET/POST | Manage categories and subcategories |
| `/admin/users` | GET | View all users and their activity |
| `/admin/activity` | GET | View admin activity log |

## Database Connection

The system connects to the **Supabase "tailor3" database** with the following configuration:
- **Host:** aws-0-us-east-2.pooler.supabase.com
- **Port:** 6543
- **Database:** postgres
- **User:** postgres.lbilxlkchzpducggkrxx
- **Connection:** Configured in `DATABASE_CONFIG.md`

### Direct Database Access
```bash
psql -h aws-0-us-east-2.pooler.supabase.com -p 6543 -U postgres.lbilxlkchzpducggkrxx -d postgres
```
Password: `efvTower12`

## Key Features

### 1. Garment Management
- **Add Garments:** Users can add clothing items to their digital closet
- **Automatic Measurement Linking:** System automatically links garments to size guide measurements
- **Brand/Category Integration:** Dynamic dropdowns populated from database

### 2. Fit Feedback System
- **Progressive Feedback:** 5-point satisfaction scale (Too Tight → Slightly Tight → Good Fit → Slightly Loose → Too Loose)
- **Dimension-Specific Feedback:** Collect feedback on chest, waist, sleeve, neck, hip, length (based on brand's available measurements)
- **Smart Dimension Detection:** System automatically detects which dimensions to ask about based on brand's size guide data

### 3. Admin Management
- **Brand Management:** Add/edit brands and their measurement units
- **Category Management:** Manage clothing categories and subcategories
- **User Monitoring:** View user activity and garment additions
- **Activity Logging:** Track all admin actions with timestamps

### 4. Database Change Logging
All database changes are automatically logged with:
- Timestamp
- User/Admin attribution
- Change details
- Stored in JSONL format in `supabase/change_logs/`

## Troubleshooting

### Port Already in Use
If you see "Address already in use" error:
```bash
# Find process using port 5001
lsof -ti:5001
# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

### Virtual Environment Issues
If virtual environment activation fails:
```bash
# Recreate virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # if requirements.txt exists
```

### Database Connection Issues
1. Check if Supabase is accessible
2. Verify credentials in `scripts/web_garment_manager.py` and `scripts/admin_garment_manager.py`
3. Test connection with direct psql command above

### Missing Dependencies
If you get import errors:
```bash
source venv/bin/activate
pip install flask psycopg2-binary python-dotenv
```

## Development Tools

### Database Debugging Scripts
```bash
# Analyze brand dimensions
python scripts/test_brand_dimensions.py

# Debug garment details
python scripts/test_garment_details.py

# Test measurement linking
python scripts/test_measurement_linking.py

# Fix garments without size guide links
python scripts/fix_garment_links.py
```

### Database Snapshots
```bash
# Create database snapshot
python scripts/db_snapshot.py

# Log database changes
python scripts/db_change_logger.py
```

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   User Web UI   │    │  Admin Web UI   │
│   (Port 5001)   │    │   (Port 5002)   │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌─────────────────┐
         │  Database APIs  │
         │  (psycopg2)     │
         └─────────────────┘
                     │
         ┌─────────────────┐
         │  Supabase DB    │
         │   "tailor3"     │
         └─────────────────┘
```

## Data Flow

1. **Garment Addition:** User adds garment → System auto-links to size guide → Measurements available for feedback
2. **Feedback Collection:** User provides fit feedback → System stores with dimension context → Data ready for recommendations
3. **Admin Management:** Admin manages brands/categories → Users get updated dropdown options → Consistent data entry

## Next Steps

After starting the system:
1. Visit http://localhost:5001 to access the user interface
2. Visit http://localhost:5002 to access the admin interface (login: admin/admin123)
3. Add test garments and feedback to verify functionality
4. Monitor logs in terminal for database change tracking

For detailed session history and troubleshooting, see `SESSION_LOG.md`. 