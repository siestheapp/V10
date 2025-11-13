# Codebase Cleanup Plan

**Created**: January 19, 2025  
**Purpose**: Organize V10 codebase by removing outdated files and creating clean structure  

---

## 🎯 **Current Issues**

### **Root Directory Clutter:**
- ❌ Multiple similar startup scripts (`start_all*.sh`, `start_backend.sh`, etc.)
- ❌ Outdated `todo.md` (last updated February)
- ❌ Old test files that may not match current logic
- ❌ User only uses `be` and `ws` commands
- ❌ Can't find port management tools easily

### **Missing Organization:**
- ❌ No clear "frequently used" vs "utility" separation
- ❌ Documentation scattered across multiple files
- ❌ Scripts not organized by purpose

---

## 🧹 **Cleanup Strategy**

### **Phase 1: Archive Old Files**
```bash
mkdir -p archive/old_scripts
mkdir -p archive/old_docs
mkdir -p archive/old_tests

# Move outdated files
mv todo.md archive/old_docs/
mv test_*.py archive/old_tests/
mv start_all*.sh archive/old_scripts/
mv start_backend.sh archive/old_scripts/
# Keep only: start_webservices.sh, stop_all.sh
```

### **Phase 2: Create Clean Structure**
```
V10/
├── 🚀 QUICK_START.md           # Simple startup guide
├── 🛠️  dev/                    # Development utilities
│   ├── scripts/               # All scripts organized by purpose
│   │   ├── database/          # Database management
│   │   ├── ports/             # Port management
│   │   └── dev_tools/         # Development utilities
│   └── logs/                  # All log files
├── 📚 docs/                   # All documentation
│   ├── user/                  # User-facing guides
│   ├── dev/                   # Developer documentation
│   └── database/              # Database documentation
├── 🗄️  archive/               # Old/deprecated files
└── src/                       # Source code (unchanged)
```

### **Phase 3: Create User-Friendly Tools**
```bash
# Simple commands you actually use:
./dev/start_backend     # Replaces 'be' 
./dev/start_webservices # Replaces 'ws'
./dev/stop_all          # Stops everything
./dev/kill_ports        # Kills stuck ports
./dev/status            # Shows what's running
```

---

## 📋 **Files to Keep vs Archive**

### **✅ KEEP (Essential):**
- `start_webservices.sh` → You use this (`ws`)
- `stop_all.sh` → You use this
- `START_HOWTO.md` → Update and rename to `QUICK_START.md`
- `scripts/kill_ports.*` → You need this for port management
- `scripts/database_change_logger.py` → New utility we created
- All `src/` code → Core application

### **📦 ARCHIVE (Outdated):**
- `todo.md` → February, superseded by new system
- `start_all*.sh` → Multiple versions, confusing
- `start_backend.sh` → Redundant
- `test_*.py` → May be outdated, logic changing
- Old documentation → Keep for reference but move

### **🗑️ DELETE (If Safe):**
- Duplicate files
- Empty or broken scripts
- Temporary files

---

## 🎯 **Proposed New Workflow**

### **Daily Usage:**
```bash
# Start development
./dev/start_backend     # Backend server
./dev/start_webservices # Web services
./dev/status           # Check what's running

# When done
./dev/stop_all         # Stop everything

# If ports stuck
./dev/kill_ports       # Force kill stuck processes
```

### **Development:**
```bash
# Database changes
./dev/scripts/database/update_schema.py
./dev/scripts/database/add_garment.py

# View changes
cat dev/logs/database_changes.log

# Port management
./dev/scripts/ports/check_ports.py
./dev/scripts/ports/kill_specific_port.py 8006
```

---

## 🚀 **Implementation Steps**

### **Step 1: Safe Archive**
- Create archive directories
- Move old files (don't delete yet)
- Test that current workflow still works

### **Step 2: Reorganize Scripts**
- Group scripts by purpose
- Create simple wrapper commands
- Update any path references

### **Step 3: Update Documentation**
- Create simple QUICK_START guide
- Update paths in existing docs
- Create user vs developer doc separation

### **Step 4: Test & Validate**
- Ensure `be` and `ws` equivalents work
- Test port management tools
- Verify database scripts function

---

## ❓ **Questions for User**

1. **What do `be` and `ws` actually run?** (aliases or script names?)
2. **Any other commands you use regularly?**
3. **Safe to archive February `todo.md`?** (or should we extract anything first?)
4. **Keep test files?** (might be useful for reference even if outdated?)

---

## 🎯 **Expected Benefits**

### **For Daily Use:**
- ✅ Clean root directory
- ✅ Easy-to-find tools
- ✅ Simple startup commands
- ✅ Clear documentation

### **For Development:**
- ✅ Organized script library
- ✅ Centralized logging
- ✅ Logical file structure
- ✅ Easy to add new tools

### **For Future:**
- ✅ Scalable organization
- ✅ Easy onboarding for others
- ✅ Clear separation of concerns
- ✅ Professional codebase structure
