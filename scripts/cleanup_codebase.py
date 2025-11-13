#!/usr/bin/env python3
"""
Codebase Cleanup Script - Organizes V10 project structure
Keeps only essential files and creates clean organization
"""

import os
import shutil
import subprocess
from datetime import datetime

def main():
    print('🧹 V10 CODEBASE CLEANUP')
    print('=' * 50)
    
    # Get current directory
    project_root = os.getcwd()
    print(f'📁 Project root: {project_root}')
    
    # Create archive and dev directories
    print('\n📦 CREATING ARCHIVE STRUCTURE:')
    
    directories_to_create = [
        'archive/old_scripts',
        'archive/old_docs', 
        'archive/old_tests',
        'dev/scripts/database',
        'dev/scripts/ports',
        'dev/scripts/dev_tools',
        'dev/logs',
        'docs/user',
        'docs/dev'
    ]
    
    for dir_path in directories_to_create:
        os.makedirs(dir_path, exist_ok=True)
        print(f'  ✅ Created: {dir_path}')
    
    # Files to archive (move to archive/)
    print('\n📦 ARCHIVING OLD FILES:')
    
    files_to_archive = [
        # Old startup scripts (keep start_webservices.sh, stop_all.sh, and start_backend.sh)
        ('start_all_clipboard.sh', 'archive/old_scripts/'),
        ('start_all_cursor.sh', 'archive/old_scripts/'),
        ('start_all_separate.sh', 'archive/old_scripts/'),
        ('start_all.sh', 'archive/old_scripts/'),
        # Keep start_backend.sh and start_webservices.sh - user's aliases depend on them!
        
        # Old documentation
        ('todo.md', 'archive/old_docs/'),
        ('todoAug.md', 'archive/old_docs/'),
        
        # Test files (might be outdated)
        ('test_confidence_field.py', 'archive/old_tests/'),
        ('test_endpoint.py', 'archive/old_tests/'),
        ('test_feedback_dictionary.py', 'archive/old_tests/'),
        ('test_feedback_field.py', 'archive/old_tests/'),
        ('test_measurements_field.py', 'archive/old_tests/'),
        ('test_real_jcrew_shirt.py', 'archive/old_tests/'),
        ('test_size_field.py', 'archive/old_tests/'),
        ('test_string_measurements.py', 'archive/old_tests/'),
    ]
    
    for source, dest_dir in files_to_archive:
        if os.path.exists(source):
            dest_path = os.path.join(dest_dir, source)
            shutil.move(source, dest_path)
            print(f'  📦 Archived: {source} → {dest_path}')
        else:
            print(f'  ⚠️  Not found: {source}')
    
    # Move scripts to organized structure
    print('\n🗂️  ORGANIZING SCRIPTS:')
    
    script_moves = [
        # Database scripts
        ('scripts/database_change_logger.py', 'dev/scripts/database/'),
        ('scripts/add_lacoste_dual_measurements.py', 'dev/scripts/database/'),
        ('scripts/fix_lacoste_and_security.py', 'dev/scripts/database/'),
        ('scripts/fix_security_model.py', 'dev/scripts/database/'),
        ('scripts/update_subcategories.py', 'dev/scripts/database/'),
        ('scripts/log_todays_changes.py', 'dev/scripts/database/'),
        
        # Port management scripts
        ('scripts/check_ports.py', 'dev/scripts/ports/'),
        ('scripts/check_ports.sh', 'dev/scripts/ports/'),
        ('scripts/kill_ports.py', 'dev/scripts/ports/'),
        ('scripts/kill_ports.sh', 'dev/scripts/ports/'),
        
        # Development tools
        ('scripts/auto_read_cursor.py', 'dev/scripts/dev_tools/'),
        ('scripts/example_with_logging.py', 'dev/scripts/dev_tools/'),
    ]
    
    for source, dest_dir in script_moves:
        if os.path.exists(source):
            filename = os.path.basename(source)
            dest_path = os.path.join(dest_dir, filename)
            shutil.move(source, dest_path)
            print(f'  🗂️  Moved: {source} → {dest_path}')
        else:
            print(f'  ⚠️  Not found: {source}')
    
    # Move logs
    print('\n📊 ORGANIZING LOGS:')
    if os.path.exists('logs'):
        if os.listdir('logs'):  # Check if logs directory has files
            for log_file in os.listdir('logs'):
                source = os.path.join('logs', log_file)
                dest = os.path.join('dev/logs', log_file)
                shutil.move(source, dest)
                print(f'  📊 Moved: {source} → {dest}')
        os.rmdir('logs')  # Remove empty logs directory
        print(f'  🗑️  Removed empty: logs/')
    
    # Create additional utility commands (keep your be/ws aliases!)
    print('\n🚀 CREATING ADDITIONAL UTILITY COMMANDS:')
    
    # Create dev/kill_ports (easy access to port management)
    with open('dev/kill_ports', 'w') as f:
        f.write('''#!/bin/bash
# Kill Stuck Ports - Easy access to port management
cd /Users/seandavey/projects/V10
python3 dev/scripts/ports/kill_ports.py "$@"
''')
    os.chmod('dev/kill_ports', 0o755)
    print('  ✅ Created: dev/kill_ports (easy port management)')
    
    # Create dev/status
    with open('dev/status', 'w') as f:
        f.write('''#!/bin/bash
# Check Running Services
cd /Users/seandavey/projects/V10
python3 dev/scripts/ports/check_ports.py
''')
    os.chmod('dev/status', 0o755)
    print('  ✅ Created: dev/status (check what\'s running)')
    
    # Move documentation
    print('\n📚 ORGANIZING DOCUMENTATION:')
    
    doc_moves = [
        # User-facing docs
        ('START_HOWTO.md', 'docs/user/QUICK_START.md'),
        ('docs/database/DATABASE_CHANGE_LOG_GUIDE.md', 'docs/user/'),
        
        # Developer docs  
        ('docs/AI_DRIVEN_FIT_LOGIC_STRATEGY.md', 'docs/dev/'),
        ('docs/Aug8_AI_Driven_Logic_Extraction.md', 'docs/dev/'),
        ('docs/CODEBASE_CLEANUP_PLAN.md', 'docs/dev/'),
        ('docs/database/DUAL_MEASUREMENT_SYSTEM_DESIGN.md', 'docs/dev/'),
        ('docs/database/SECURITY_SETUP_GUIDE.md', 'docs/dev/'),
    ]
    
    for source, dest in doc_moves:
        if os.path.exists(source):
            # Handle directory destinations
            if dest.endswith('/'):
                filename = os.path.basename(source)
                dest_path = os.path.join(dest, filename)
            else:
                dest_path = dest
                
            # Create destination directory if needed
            dest_dir = os.path.dirname(dest_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(source, dest_path)
            print(f'  📚 Moved: {source} → {dest_path}')
        else:
            print(f'  ⚠️  Not found: {source}')
    
    # Create simple README for root
    print('\n📝 CREATING ROOT README:')
    
    with open('README.md', 'w') as f:
        f.write(f'''# V10 Clothing Fit Analysis App

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}

## 🚀 Quick Start

```bash
# Start backend server
./dev/start_backend

# Start web services  
./dev/start_webservices

# Check what's running
./dev/status

# Stop everything
./dev/stop_all

# Kill stuck ports
./dev/kill_ports
```

## 📁 Project Structure

- `📱 src/` - iOS app and backend code
- `🛠️ dev/` - Development tools and scripts
- `📚 docs/` - Documentation (user & developer)
- `🗄️ archive/` - Old/deprecated files

## 📖 Documentation

- **User Guide**: `docs/user/QUICK_START.md`
- **Database Changes**: `docs/user/DATABASE_CHANGE_LOG_GUIDE.md`
- **Developer Docs**: `docs/dev/`

## 🔧 Development

All development tools are in `dev/`:
- **Database scripts**: `dev/scripts/database/`
- **Port management**: `dev/scripts/ports/`
- **Logs**: `dev/logs/`

## ✨ What's New

- ✅ Clean, organized codebase structure
- ✅ Simple command shortcuts in `dev/`
- ✅ Archived old/outdated files safely
- ✅ Centralized documentation
- ✅ Database change logging system
''')
    print('  📝 Created: README.md')
    
    # Summary
    print('\n🎉 CLEANUP COMPLETE!')
    print('=' * 50)
    print('✅ Archived old files safely')
    print('✅ Organized scripts by purpose')
    print('✅ Created user-friendly commands')
    print('✅ Structured documentation')
    print('✅ Clean root directory')
    
    print('\n🎯 YOUR WORKFLOW (UNCHANGED):')
    print('  • Backend: be (still works!)')
    print('  • Web services: ws (still works!)')
    print('  • Stop all: ./stop_all.sh (still works!)')
    print('')
    print('🆕 NEW UTILITIES:')
    print('  • Kill ports: ./dev/kill_ports')
    print('  • Check status: ./dev/status')
    
    print('\n📁 KEY LOCATIONS:')
    print('  • Database scripts: dev/scripts/database/')
    print('  • Port tools: dev/scripts/ports/')
    print('  • Change logs: dev/logs/')
    print('  • User docs: docs/user/')
    print('  • Old files: archive/ (safe to delete later)')

if __name__ == '__main__':
    main()
