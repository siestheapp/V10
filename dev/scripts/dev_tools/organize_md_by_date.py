#!/usr/bin/env python3
"""
Organize Markdown Files by Date
Creates date-based folders and moves .md files based on their modification date
Uses Eastern Time (EST/EDT) for date determination
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import stat
import pytz

def get_file_date(file_path):
    """Get the modification date of a file in Eastern Time"""
    try:
        # Get file stats
        file_stat = os.stat(file_path)
        
        # Use modification time (so updated files move to today's folder)
        modification_time = file_stat.st_mtime
        
        # Convert to Eastern Time
        utc_dt = datetime.fromtimestamp(modification_time, tz=pytz.UTC)
        eastern = pytz.timezone('US/Eastern')
        eastern_dt = utc_dt.astimezone(eastern)
        
        return eastern_dt
    except Exception as e:
        print(f"  ⚠️  Error getting date for {file_path}: {e}")
        # Return current time in Eastern timezone as fallback
        eastern = pytz.timezone('US/Eastern')
        return datetime.now(eastern)

def organize_md_files():
    """Organize all .md files in the project by date"""
    
    print('📅 ORGANIZING MARKDOWN FILES BY DATE (Eastern Time)')
    print('=' * 60)
    
    project_root = os.getcwd()
    print(f'📁 Project root: {project_root}')
    
    # Create daily-notes directory structure
    daily_notes_dir = 'daily-notes'
    os.makedirs(daily_notes_dir, exist_ok=True)
    print(f'📂 Created: {daily_notes_dir}/')
    
    # Find all .md files in the project (excluding certain directories)
    exclude_dirs = {'.git', 'node_modules', 'venv', '.vscode', '.temp', 'archive'}
    md_files = []
    
    print(f'\\n🔍 SCANNING FOR MARKDOWN FILES:')
    
    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # Skip if we're in certain directories (don't move files that are already organized or belong elsewhere)
        path_parts = Path(root).parts
        if any(part in path_parts for part in ['daily-notes', '.specstory']):
            continue
            
        for file in files:
            if file.endswith('.md') and not file.startswith('.'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_root)
                md_files.append((file_path, relative_path))
                print(f'  📄 Found: {relative_path}')
    
    print(f'\\n📊 Found {len(md_files)} markdown files')
    
    # Group files by date and organize
    print(f'\\n📅 ORGANIZING BY DATE:')
    
    files_by_date = {}
    
    for file_path, relative_path in md_files:
        # Get file date
        file_date = get_file_date(file_path)
        date_str = file_date.strftime('%Y-%m-%d')
        
        if date_str not in files_by_date:
            files_by_date[date_str] = []
        
        files_by_date[date_str].append((file_path, relative_path, file_date))
    
    # Create date folders and move files
    for date_str, files in sorted(files_by_date.items()):
        date_folder = os.path.join(daily_notes_dir, date_str)
        os.makedirs(date_folder, exist_ok=True)
        
        print(f'\\n📅 {date_str} ({len(files)} files):')
        
        for file_path, relative_path, file_date in files:
            filename = os.path.basename(file_path)
            
            # Create a descriptive name with time if multiple files on same day
            time_str = file_date.strftime('%H%M')
            
            # Check if we need to add time to avoid conflicts
            dest_filename = filename
            dest_path = os.path.join(date_folder, dest_filename)
            
            if os.path.exists(dest_path):
                # Add time to filename if conflict
                name, ext = os.path.splitext(filename)
                dest_filename = f'{name}_{time_str}{ext}'
                dest_path = os.path.join(date_folder, dest_filename)
            
            # Move the file
            try:
                shutil.move(file_path, dest_path)
                print(f'  📄 {relative_path} → {date_str}/{dest_filename}')
            except Exception as e:
                print(f'  ❌ Failed to move {relative_path}: {e}')
    
    # Create index file for easy navigation
    print(f'\\n📋 CREATING DATE INDEX:')
    
    index_path = os.path.join(daily_notes_dir, 'INDEX.md')
    with open(index_path, 'w') as f:
        f.write('# Daily Notes Index\\n\\n')
        eastern = pytz.timezone('US/Eastern')
        now_eastern = datetime.now(eastern)
        f.write(f'**Generated**: {now_eastern.strftime("%Y-%m-%d %H:%M:%S %Z")}\\n\\n')
        f.write('## Timeline of Work\\n\\n')
        
        for date_str in sorted(files_by_date.keys(), reverse=True):  # Most recent first
            files = files_by_date[date_str]
            f.write(f'### {date_str} ({len(files)} files)\\n\\n')
            
            for file_path, relative_path, file_date in files:
                filename = os.path.basename(file_path)
                time_str = file_date.strftime('%H:%M')
                
                # Check if filename was modified due to conflicts
                dest_filename = filename
                dest_path = os.path.join(daily_notes_dir, date_str, dest_filename)
                if not os.path.exists(dest_path):
                    name, ext = os.path.splitext(filename)
                    dest_filename = f'{name}_{file_date.strftime("%H%M")}{ext}'
                
                f.write(f'- **{time_str}** [{dest_filename}]({date_str}/{dest_filename})\\n')
            
            f.write('\\n')
        
        f.write('\\n---\\n\\n')
        f.write('*This index is automatically generated. Re-run the organize script to update.*\\n')
    
    print(f'  📋 Created: {index_path}')
    
    # Summary
    print(f'\\n🎉 ORGANIZATION COMPLETE!')
    print('=' * 50)
    print(f'✅ Organized {len(md_files)} markdown files')
    print(f'✅ Created {len(files_by_date)} date folders')
    print(f'✅ Generated timeline index')
    
    print(f'\\n📂 STRUCTURE:')
    print(f'  daily-notes/')
    for date_str in sorted(files_by_date.keys()):
        file_count = len(files_by_date[date_str])
        print(f'  ├── {date_str}/ ({file_count} files)')
    print(f'  └── INDEX.md (timeline overview)')
    
    print(f'\\n🎯 TO BROWSE YOUR WORK:')
    print(f'  • Open: daily-notes/INDEX.md')
    print(f'  • Click on any date to see that day\'s work')
    print(f'  • Files are organized chronologically')

if __name__ == '__main__':
    organize_md_files()
