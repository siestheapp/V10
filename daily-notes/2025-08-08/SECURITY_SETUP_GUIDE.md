# Database Security Setup Guide

## 🚨 Current Security Status: CRITICAL VULNERABILITY

Your database currently has **NO security policies** - anyone with the connection string can access all user data.

## Security Issues Found

### ❌ Row Level Security (RLS) Disabled
- All tables show "Unrestricted" in Supabase dashboard
- No authentication required to read/write data
- User data is completely exposed

### ❌ No Access Policies
- No policies restricting data access
- Service accounts have unlimited access
- AI agent would have full database access

## Recommended Security Architecture

### 🔒 Three-Tier Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│ 1. AUTHENTICATED USERS (iOS App)                            │
│    • Can only access their own data                         │
│    • RLS policies enforce user isolation                    │
│    • Uses Supabase Auth JWT tokens                          │
├─────────────────────────────────────────────────────────────┤
│ 2. SERVICE ROLE (Backend/API)                               │
│    • Full access for legitimate operations                  │
│    • Used by your backend server                            │
│    • Bypasses RLS for admin operations                      │
├─────────────────────────────────────────────────────────────┤
│ 3. AI AGENT ROLE (Limited Access)                           │
│    • Read-only access to user data                          │
│    • Can log AI decisions/actions                           │
│    • Cannot modify user personal data                       │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Step 1: Apply Security Policies

Run the security setup script:

```bash
# From your project root
cd /Users/seandavey/projects/V10
source venv/bin/activate
python3 -c "
import psycopg2

DB_CONFIG = {
    'host': 'aws-0-us-east-2.pooler.supabase.com',
    'port': '6543',
    'database': 'postgres',
    'user': 'postgres.lbilxlkchzpducggkrxx',
    'password': 'efvTower12'
}

# Read and execute security script
with open('scripts/database/secure_database_setup.sql', 'r') as f:
    security_sql = f.read()

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute(security_sql)
conn.commit()
print('✅ Security policies applied!')
cur.close()
conn.close()
"
```

### Step 2: Create AI Agent Credentials

Create a separate database user for the AI agent:

```sql
-- In Supabase SQL Editor
CREATE USER ai_agent WITH PASSWORD 'secure_ai_password_here';
GRANT ai_agent_role TO ai_agent;
```

### Step 3: Update Application Configuration

#### Backend Configuration (.env)
```env
# Main service role (full access)
DB_HOST=aws-0-us-east-2.pooler.supabase.com
DB_PORT=6543
DB_NAME=postgres
DB_USER=postgres.lbilxlkchzpducggkrxx
DB_PASSWORD=efvTower12

# AI Agent (limited access)
AI_DB_USER=ai_agent
AI_DB_PASSWORD=secure_ai_password_here
```

#### iOS App Configuration
```swift
// Use Supabase client with RLS enabled
let supabase = SupabaseClient(
    supabaseURL: URL(string: "https://your-project.supabase.co")!,
    supabaseKey: "your-anon-key"
)
```

## AI Agent Security

### ✅ What AI Agent CAN Do:
- Read user garment data for size recommendations
- Read size guides and brand data
- Log AI decisions and recommendations
- Access fit zone calculations

### ❌ What AI Agent CANNOT Do:
- Modify user personal information
- Delete user garments
- Access other users' data directly
- Bypass authentication

### AI Agent Connection Example:
```python
# AI Agent connection (limited permissions)
AI_DB_CONFIG = {
    'host': 'aws-0-us-east-2.pooler.supabase.com',
    'port': '6543',
    'database': 'postgres',
    'user': 'ai_agent',
    'password': 'secure_ai_password_here'
}

# This connection can only read data and log AI actions
conn = psycopg2.connect(**AI_DB_CONFIG)
```

## Database Branching Explanation

### What Supabase Branches Are:
- **Separate database instances** (not like Git code branches)
- Each branch has its own data and schema
- Used for testing schema changes safely

### Recommended Branch Strategy:
```
Production Branch (main)
├── Your live user data
├── Production schema
└── Used by iOS app

Development Branch (dev)
├── Test data
├── Schema experiments
└── Safe for AI training experiments
```

### Creating a Development Branch:
1. In Supabase dashboard: Create new branch
2. Name it "ai-training" or "development"  
3. Test AI agent on dev branch first
4. Apply security policies to both branches

## Security Verification

After applying security:

### Check RLS Status:
```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND rowsecurity = true;
```

### Check Policies:
```sql
SELECT tablename, policyname, cmd 
FROM pg_policies 
WHERE schemaname = 'public';
```

### Test AI Agent Access:
```python
# Should work (read access)
cur.execute("SELECT * FROM user_garments WHERE user_id = 1")

# Should fail (no write access to user data)
cur.execute("UPDATE users SET email = 'hacker@evil.com' WHERE id = 1")
```

## Emergency Security Actions

If you suspect unauthorized access:

### Immediate Actions:
1. **Rotate database password** in Supabase dashboard
2. **Check audit logs** for suspicious activity
3. **Review user_actions table** for unexpected entries
4. **Update .env files** with new credentials

### Long-term Monitoring:
- Enable Supabase audit logging
- Monitor user_actions table for AI decisions
- Regular security policy reviews
- Rotate AI agent credentials monthly

## Cost Implications

### Security Features (Free on Supabase):
- ✅ Row Level Security (RLS)
- ✅ Authentication
- ✅ Basic audit logging

### Paid Features (If Needed):
- Advanced audit logging
- Database backups
- Point-in-time recovery

## Next Steps

1. **Apply security script** (5 minutes)
2. **Create AI agent user** (2 minutes)
3. **Test access levels** (5 minutes)
4. **Update application configs** (10 minutes)
5. **Create development branch** for AI training (5 minutes)

**Total time to secure: ~30 minutes**

The current "Unrestricted" status is a critical vulnerability that should be fixed immediately before any AI agent implementation.
