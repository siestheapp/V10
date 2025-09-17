# Simplified Contractor Setup - Real Backend with Test Data

> Since user1 data is all fake/test data, we can give the contractor a more realistic environment!

## 🎯 New Approach: Real Backend, Fake Data

### Why This Is Better
- **Real API latencies** - They can identify if backend is part of the problem
- **Actual data structures** - No mocking needed
- **True performance testing** - Testing the real app, not a mock
- **Simpler setup** - Less preparation needed

### What They Get Access To
✅ iOS app source code
✅ Backend API running locally or on test server  
✅ User1 test data (it's all fake anyway)
✅ Ability to test real data flow

### What They DON'T Get
❌ Scraper code (proprietary)
❌ Production server credentials
❌ Ability to modify database schema
❌ Access to other users (if any exist)
❌ API keys for external services

## 📦 Option 1: Local Backend Setup (Simpler)

### Prepare a Test Database Dump

```bash
# Export just user1's data
cd /Users/seandavey/projects/V10

# Create a sanitized dump with only test data
cat > export_test_data.sql << 'EOF'
-- Export only user1 test data for contractor
\c tailor3

-- Export schema
\echo 'Exporting schema...'

-- Export only user1 related data
\echo 'Exporting user1 test data...'
\copy (SELECT * FROM users WHERE user_id = 1) TO 'users_test.csv' CSV HEADER;
\copy (SELECT * FROM user_garments WHERE user_id = 1) TO 'user_garments_test.csv' CSV HEADER;
\copy (SELECT * FROM user_garment_feedback WHERE user_garment_id IN (SELECT id FROM user_garments WHERE user_id = 1)) TO 'feedback_test.csv' CSV HEADER;
\copy (SELECT * FROM user_measurements WHERE user_id = 1) TO 'measurements_test.csv' CSV HEADER;

-- Export all product data (not sensitive)
\copy (SELECT * FROM brands) TO 'brands.csv' CSV HEADER;
\copy (SELECT * FROM product_master) TO 'products.csv' CSV HEADER;
\copy (SELECT * FROM product_variants) TO 'variants.csv' CSV HEADER;
\copy (SELECT * FROM measurement_sets) TO 'measurement_sets.csv' CSV HEADER;
\copy (SELECT * FROM measurements) TO 'measurements.csv' CSV HEADER;
EOF
```

### Create Contractor Package

```bash
# Create contractor package
mkdir contractor-package
cd contractor-package

# Copy iOS app
cp -r ../src/ios_app .

# Copy backend WITHOUT scrapers
mkdir backend
cp ../src/ios_app/Backend/app.py backend/
cp ../src/ios_app/Backend/requirements.txt backend/
# Skip proprietary algorithms if you want

# Create simple db_config
cat > backend/db_config.py << 'EOF'
# Local test database config
DB_CONFIG = {
    'user': 'postgres',
    'password': 'localtest',
    'host': 'localhost',
    'port': 5432,
    'database': 'v10_test'
}
EOF

# Create setup instructions
cat > SETUP.md << 'EOF'
# V10 Performance Testing Setup

## 1. Install PostgreSQL locally
```bash
brew install postgresql
brew services start postgresql
```

## 2. Create test database
```bash
createdb v10_test
# Import the test data CSVs provided
```

## 3. Run backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 4. Run iOS app
```bash
cd ios_app
open V10.xcodeproj
# Update Config.swift to point to localhost:8006
```

## 5. Test with user1
- Email: user1@example.com
- All data is test data - inconsistent on purpose
EOF
```

## 📦 Option 2: Test Server (Easier for Contractor)

### Set Up Render/Railway Test Instance

1. **Create test database on Supabase** (free tier)
   - New project: "v10-contractor-test"
   - Import only user1 data
   - Give contractor read-only SQL access

2. **Deploy backend to Render** (free tier)
   ```yaml
   # render.yaml for test deployment
   services:
     - type: web
       name: v10-contractor-test
       env: python
       buildCommand: "pip install -r requirements.txt"
       startCommand: "python app.py"
       envVars:
         - key: DATABASE_URL
           value: "postgresql://[test-db-url]"
         - key: CONTRACTOR_MODE
           value: "true"
   ```

3. **Give contractor the test URL**
   ```swift
   // They update Config.swift to:
   static let baseURL = "https://v10-contractor-test.onrender.com"
   ```

## 🔒 Modified Security Approach

### prepare_contractor_branch_simple.sh
```bash
#!/bin/bash
echo "🔒 Preparing simplified contractor branch..."

# Start from your working branch
git checkout revert-to-a42786

# Create contractor branch
git checkout -b contractor-ios-simple

echo "📁 Removing only sensitive items..."

# Remove scrapers (proprietary)
rm -rf scrapers/
rm -rf scripts/*scraper*.py

# Remove production configs
rm -f .env.production
rm -f railway.json
rm -f render.yaml

# Keep the backend but add warning
cat > src/ios_app/Backend/README_CONTRACTOR.md << 'EOF'
# Backend for Testing Only

This backend is provided for performance testing.
- Uses test data only (user1)
- No real user information
- Do not modify database schema
- Focus on iOS performance optimization
EOF

echo "✅ Simplified branch ready!"
echo "The contractor can now:"
echo "1. Run the real backend locally"
echo "2. Test with actual API calls"
echo "3. See real performance characteristics"

git add -A
git commit -m "Contractor version with test backend access"
git push origin contractor-ios-simple

git checkout revert-to-a42786
```

## 🎯 Updated Contractor Instructions

### What to Tell Them

```
Hi [Name],

For this performance optimization project, you'll have access to:

1. Full iOS source code
2. Backend API (running locally or on test server)
3. Test database with user1 (all fake data)

The "user1" account has intentionally inconsistent data - 3XL shirts marked 
as "too small" and S shirts as "too big" - this is test data I created by 
randomly clicking buttons. Don't worry about the data making sense.

Focus on:
- Tab switching speed (<200ms)
- Scroll performance (55+ FPS)
- Button responsiveness (<100ms)

You can run the backend locally with the test data, or I can provide a test 
server URL. Whatever is easier for you.

The performance issues are in the iOS UI layer, but having the real backend 
will help you test actual data loading patterns.
```

## ✅ Benefits of This Approach

### For Performance Testing
- **Real latencies** - Actual network delays
- **True data volume** - Real database queries
- **Actual caching needs** - Real API responses
- **Backend bottlenecks** - Can identify if API is slow too

### For Security
- **No real user data** - It's all test junk
- **No production access** - Separate test environment
- **Limited database access** - Read-only or just user1
- **No scraper code** - That stays private

### For Simplicity
- **Less mocking needed** - Use real backend
- **Familiar tools** - Standard iOS + API setup
- **Easier debugging** - Can see actual API calls
- **Better testing** - More realistic environment

## 📋 Quick Setup Checklist

1. **Decide on approach**:
   - [ ] Local backend (more control)
   - [ ] Test server (easier for contractor)

2. **Prepare test data**:
   - [ ] Export user1 data only
   - [ ] Verify it's all test data
   - [ ] Create import scripts

3. **Set up environment**:
   - [ ] Create contractor branch
   - [ ] Remove only scrapers/credentials
   - [ ] Keep backend code

4. **For test server**:
   - [ ] Create test database
   - [ ] Deploy backend to free tier
   - [ ] Share URL with contractor

5. **Communication**:
   - [ ] Explain it's test data
   - [ ] Share performance targets
   - [ ] Provide setup instructions

## 🚀 Even Simpler: Just Share Everything Except Scrapers

Since it's all test data anyway:

```bash
# Super simple approach
git checkout revert-to-a42786
git checkout -b contractor-full-access

# Only remove scrapers (your real IP)
rm -rf scrapers/
rm -rf scripts/*scraper*.py

# Maybe remove production deploys
rm -f .env.production

git add -A
git commit -m "Contractor version - full access except scrapers"
git push origin contractor-full-access

# Tell contractor:
# "Here's everything except the scrapers. 
#  The database only has test data.
#  Focus on iOS performance."
```

This is actually the most practical approach since:
1. The data is fake
2. Backend performance might be relevant
3. Simpler is better
4. Less prep work for you

---

The main insight: Since your data is fake test data, you don't need elaborate security. Just remove the proprietary scrapers and let them work with the real system!
