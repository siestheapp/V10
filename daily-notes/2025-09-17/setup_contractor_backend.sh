#!/bin/bash
# Quick script to set up contractor backend access

echo "🚀 Setting up contractor backend access..."
echo ""
echo "Choose an option:"
echo "1. Deploy to Render (Recommended - 5 minutes)"
echo "2. Share Supabase read-only credentials"
echo "3. Help them run locally"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
  1)
    echo "📦 Deploying to Render..."
    echo ""
    echo "1. Go to https://render.com"
    echo "2. Connect GitHub repo"
    echo "3. Create new Web Service:"
    echo "   - Name: v10-contractor-test"
    echo "   - Branch: contractor-performance-simple"
    echo "   - Root Directory: src/ios_app/Backend"
    echo "   - Build: pip install -r requirements.txt"
    echo "   - Start: python app.py"
    echo ""
    echo "4. Add environment variables:"
    echo "   DB_HOST=your-supabase-host"
    echo "   DB_USER=your-test-user"
    echo "   DB_PASSWORD=your-test-password"
    echo "   DB_NAME=postgres"
    echo "   DB_PORT=6543"
    echo ""
    echo "5. Deploy and share URL with contractor"
    ;;
    
  2)
    echo "🔐 Creating read-only database user..."
    echo ""
    echo "Run this in Supabase SQL editor:"
    echo ""
    cat << 'SQL'
-- Create read-only user for contractor
CREATE USER contractor_readonly WITH PASSWORD 'temp_password_2weeks';

-- Grant connect
GRANT CONNECT ON DATABASE postgres TO contractor_readonly;

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO contractor_readonly;

-- Grant SELECT on all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO contractor_readonly;

-- Grant SELECT on future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT SELECT ON TABLES TO contractor_readonly;

-- Show connection info
SELECT 'Connection String:' as info,
'postgresql://contractor_readonly:temp_password_2weeks@aws-0-us-east-2.pooler.supabase.com:6543/postgres' as connection_string;
SQL
    ;;
    
  3)
    echo "📝 Local setup instructions for contractor:"
    echo ""
    cat << 'INSTRUCTIONS'
Send this to contractor:

## Local Backend Setup

1. Install PostgreSQL:
   ```bash
   # Mac
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql
   ```

2. Create test database:
   ```bash
   createdb v10_test
   psql v10_test < test_data.sql  # We'll provide this
   ```

3. Run backend:
   ```bash
   cd src/ios_app/Backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Update db_config_mock.py with local credentials
   python app.py
   ```

4. Update iOS Config.swift:
   ```swift
   static let baseURL = "http://127.0.0.1:8006"
   ```
INSTRUCTIONS
    ;;
esac

echo ""
echo "✅ Done! Share the above with contractor."
