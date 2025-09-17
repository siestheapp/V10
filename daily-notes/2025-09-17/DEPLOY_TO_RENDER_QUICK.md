# 🚀 Deploy Backend to Render - 5 Minutes

## Quick Steps:

1. **Go to Render.com**
   - Sign up/login
   - Click "New +" → "Web Service"

2. **Connect GitHub**
   - Choose "Build and deploy from Git"
   - Connect GitHub account if needed
   - Select repository: V10

3. **Configure Service**
   ```
   Name: v10-contractor-test
   Region: Ohio (US East)
   Branch: contractor-performance-simple
   Root Directory: src/ios_app/Backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   Instance Type: Free
   ```

4. **Add Environment Variables**
   Click "Add Environment Variable" for each:
   ```
   DB_HOST = db.[your-supabase-id].supabase.co
   DB_USER = postgres
   DB_PASSWORD = [your-supabase-password]
   DB_NAME = postgres
   DB_PORT = 5432
   PORT = 10000
   ```

   OR for truly isolated test (no real DB):
   ```
   MOCK_MODE = true
   PORT = 10000
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait ~5-10 minutes for first deploy
   - Copy the URL: https://v10-contractor-test.onrender.com

6. **Update Contractor Branch**
   ```bash
   git checkout contractor-performance-simple
   
   # Update Config.swift with Render URL
   cat > src/ios_app/V10/App/Config.swift << 'EOF'
   import Foundation
   
   struct Config {
       static let baseURL = "https://v10-contractor-test.onrender.com"
       static let useMockData = false
   }
   EOF
   
   git add -A
   git commit -m "Update Config to use Render backend"
   git push origin contractor-performance-simple
   ```

7. **Send URL to Contractor**
   ```
   The backend is now live at:
   https://v10-contractor-test.onrender.com
   
   It has test data for user1@example.com.
   The iOS app is already configured to use it.
   ```

## Alternative: Use Your Existing Backend

If you already have a backend deployed:
1. Just share that URL (since data is fake anyway)
2. Update Config.swift in contractor branch
3. Done!

## To Tear Down After Project

1. Go to Render dashboard
2. Settings → Delete Web Service
3. Confirm deletion

Total cost: $0 (free tier)
