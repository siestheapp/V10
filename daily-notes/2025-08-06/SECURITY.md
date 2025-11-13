# Security Guidelines

## 🔐 **CRITICAL: This repository contains sensitive information**

### **Current Security Status:**
- ✅ **Repository**: Should be set to **PRIVATE** on GitHub
- ✅ **Environment Variables**: Sensitive credentials moved to `.env` files
- ✅ **Gitignore**: Updated to exclude sensitive files
- ⚠️ **Database Credentials**: Still need to be removed from hardcoded files

### **Sensitive Information Found:**
1. **Database Password**: `efvTower12` (exposed in 30+ files)
2. **Database Host**: `aws-0-us-east-2.pooler.supabase.com:6543`
3. **Database User**: `postgres.lbilxlkchzpducggkrxx`
4. **Supabase Connection**: Full connection string exposed

### **Immediate Actions Required:**

#### **1. Make Repository Private**
```bash
# On GitHub: Settings → General → Danger Zone → Change repository visibility
# Or use GitHub CLI:
gh repo edit --visibility private
```

#### **2. Remove Hardcoded Credentials**
All files with hardcoded database credentials need to be updated to use environment variables:

**Files to update:**
- `src/ios_app/Backend/app.py`
- `src/ios_app/Backend/main.py`
- All files in `scripts/` directory
- All files in `tests/` directory
- Documentation files

#### **3. Use Environment Variables**
```python
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}
```

### **Supabase Database Security:**

#### **Current Status:**
- ✅ **Database**: Supabase PostgreSQL (tailor3)
- ✅ **Connection**: Pooled connection via Supabase
- ⚠️ **Credentials**: Exposed in code (needs fixing)

#### **Recommended Actions:**
1. **Rotate Database Password**: Change the Supabase database password
2. **Use Connection Pooling**: Already configured correctly
3. **Enable Row Level Security**: Consider implementing RLS policies
4. **Audit Access**: Monitor database access logs

### **Environment Setup:**

#### **For Development:**
1. Copy `.env.template` to `.env`
2. Fill in your actual credentials
3. Never commit `.env` files

#### **For Production:**
1. Use environment variables in deployment
2. Use secrets management (AWS Secrets Manager, etc.)
3. Rotate credentials regularly

### **Files to Never Commit:**
- `.env` files
- `*.log` files
- Database dumps
- Credential files
- iOS build artifacts

### **GitHub Security:**
- ✅ **Repository**: Set to PRIVATE
- ✅ **Branch Protection**: Enable for main branch
- ✅ **Code Scanning**: Enable GitHub Advanced Security
- ✅ **Dependency Scanning**: Enable automated security scanning

### **Next Steps:**
1. ✅ Make repository private
2. ✅ Update .gitignore
3. ✅ Create environment template
4. ✅ **COMPLETED**: Remove hardcoded credentials from main backend files
5. ✅ **COMPLETED**: Update main scripts to use environment variables
6. ⚠️ **TODO**: Remove hardcoded credentials from remaining script files (20+ files)
7. ⚠️ **TODO**: Rotate database password
8. ⚠️ **TODO**: Enable GitHub security features

---
*Last updated: 2025-01-27*
*Status: Critical security issues identified - immediate action required*
