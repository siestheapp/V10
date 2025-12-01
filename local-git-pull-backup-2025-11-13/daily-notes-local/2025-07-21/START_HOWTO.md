# V10 Project Startup Guide (Tailor3/Supabase)

This guide will help you start the V10 project from the root directory using the Supabase `tailor3` database.

## Prerequisites

Make sure you have:
- Python 3.x installed
- Xcode installed (for iOS development)
- Internet connection (for Supabase database)

## Step-by-Step Startup

### 1. Navigate to Project Directory
```bash
cd /Users/seandavey/projects/V10
pwd
# Should show: /Users/seandavey/projects/V10
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
# You should see (venv) in your prompt
```

### 3. Start the FastAPI Backend Server
```bash
cd src/ios_app/Backend
uvicorn app:app --host 0.0.0.0 --port 8006 --reload
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/Users/seandavey/projects/V10/src/ios_app/Backend']
INFO:     Uvicorn running on http://0.0.0.0:8006 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using StatReload
Connected to database
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4. Verify Server is Running
In a new terminal window:
```bash
lsof -i :8006
# Should show Python processes listening on port 8006
```

### 5. Open iOS Project in Xcode
- Open Xcode
- Go to File → Open
- Navigate to `src/ios_app/V10.xcodeproj`
- Select the project file and click "Open"

### 6. Run the iOS App
- In Xcode, select your target device (iPhone simulator or physical device)
- Click the Run button (▶️) to build and run the app

## Database Configuration

This branch uses **Supabase Cloud Database** (`tailor3`):
- **Host**: `aws-0-us-east-2.pooler.supabase.com`
- **Port**: `6543`
- **Database**: `postgres`
- **No local PostgreSQL required!**

## Alternative: Use the Startup Script

If the above doesn't work, you can use the provided startup script:
```bash
chmod +x start_server.sh
./start_server.sh
```

## Troubleshooting

### If uvicorn command not found:
Make sure you're in the virtual environment:
```bash
source venv/bin/activate
which uvicorn
```

### If port 8006 is already in use:
Kill existing processes:
```bash
lsof -i :8006
kill [PID_NUMBER]
```

### If database connection fails:
- Check your internet connection
- Verify Supabase is running (cloud database)
- Check the database credentials in `src/ios_app/Backend/app.py`

## Project Structure

- **Backend**: FastAPI server on `localhost:8006`
- **Database**: Supabase Cloud (`tailor3`)
- **iOS App**: SwiftUI app in `src/ios_app/V10.xcodeproj`
- **Config**: App configured to use user ID 2 by default

## Quick Commands Summary

```bash
# From /Users/seandavey/projects/V10
source venv/bin/activate
cd src/ios_app/Backend
uvicorn app:app --host 0.0.0.0 --port 8006 --reload
```

Then open `src/ios_app/V10.xcodeproj` in Xcode and run the app.

## Key Differences from Backup Branch

- **Database**: Supabase Cloud instead of local PostgreSQL
- **No local database setup required**
- **Uses `app.py` instead of `main.py`**
- **Project path**: `src/ios_app/` instead of `V10/V10/`
- **User ID**: 2 instead of 18 