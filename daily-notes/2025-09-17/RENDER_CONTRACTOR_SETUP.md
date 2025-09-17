# Render Test Server for Contractor

## Quick Setup (5 minutes)

### 1. Deploy Backend to Render Free Tier

```bash
# Create render.yaml for contractor branch
cat > render.yaml << 'EOF'
services:
  - type: web
    name: v10-contractor-test
    runtime: python
    buildCommand: "cd src/ios_app/Backend && pip install -r requirements.txt"
    startCommand: "cd src/ios_app/Backend && python app.py"
    envVars:
      - key: DATABASE_URL
        value: postgresql://user:pass@host/db  # Your test DB
      - key: OPENAI_API_KEY
        value: skip  # Not needed for performance testing
      - key: PORT
        value: 8006
EOF
```

### 2. Use Supabase Free Tier for Test DB

Since user1 data is all fake anyway:
- Create new Supabase project: "v10-contractor-test"
- Import only user1 test data
- Give contractor the connection string

### 3. Update Config.swift in Contractor Branch

```swift
// In src/ios_app/V10/App/Config.swift
struct Config {
    #if DEBUG
    static let baseURL = "https://v10-contractor-test.onrender.com"
    #else
    static let baseURL = "https://v10-contractor-test.onrender.com"
    #endif
}
```

## Why This Is Better Than Local Setup

1. **No setup hassles** - Contractor doesn't need PostgreSQL locally
2. **Real network latency** - Can identify if lag is from API calls
3. **Consistent environment** - Same for both of you
4. **Free tier is enough** - Only testing with user1 data
5. **Easy to tear down** - Delete after 2 weeks

## What Contractor Gets

✅ Real backend with real (fake) data
✅ Actual API latencies to debug
✅ Database queries to optimize
✅ Full stack to troubleshoot
❌ No access to production
❌ No real user data
❌ No ability to modify schema

## Security Note

Since it's ALL fake test data:
- user1's 3XL shirts marked "too small" 
- S shirts marked "too big"
- Random nonsensical feedback
- No real measurements

There's NO confidentiality risk!

## Message to Contractor

"The backend is deployed at https://v10-contractor-test.onrender.com
It has test data for user1@example.com (all fake/random).
This will help you identify if the lag is from:
- iOS UI rendering
- Network/API calls  
- Database queries
- Data processing

The Config.swift is already updated to point there."
