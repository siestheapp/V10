#!/usr/bin/env python3
"""
Fix .specstory files - move them back to their original location
and update the daily-notes index to exclude them
"""

import os
import shutil
import glob
from datetime import datetime

def fix_specstory_files():
    print('🔧 FIXING SPECSTORY FILE LOCATIONS')
    print('=' * 50)
    
    project_root = os.getcwd()
    daily_notes_dir = 'daily-notes'
    specstory_dir = '.specstory/history'
    
    # Find all specstory files that were moved to daily-notes
    moved_specstory_files = []
    
    for date_dir in os.listdir(daily_notes_dir):
        date_path = os.path.join(daily_notes_dir, date_dir)
        if os.path.isdir(date_path) and date_dir.startswith('2025-'):
            for file in os.listdir(date_path):
                if file.startswith('2025-') and file.endswith('.md') and '_0400-' in file:
                    # This looks like a specstory file
                    file_path = os.path.join(date_path, file)
                    moved_specstory_files.append((file_path, file))
    
    print(f'🔍 Found {len(moved_specstory_files)} specstory files to move back')
    
    # Move them back to .specstory/history/
    for file_path, filename in moved_specstory_files:
        dest_path = os.path.join(specstory_dir, filename)
        
        try:
            shutil.move(file_path, dest_path)
            print(f'  ↩️  Moved back: {filename}')
        except Exception as e:
            print(f'  ❌ Error moving {filename}: {e}')
    
    # Regenerate the INDEX.md without specstory files
    print(f'\\n📋 REGENERATING INDEX WITHOUT SPECSTORY FILES:')
    
    # Get all remaining files in daily-notes (excluding specstory files)
    files_by_date = {}
    
    for date_dir in os.listdir(daily_notes_dir):
        date_path = os.path.join(daily_notes_dir, date_dir)
        if os.path.isdir(date_path) and date_dir.startswith('2025-'):
            files_in_date = []
            
            for file in os.listdir(date_path):
                if file.endswith('.md'):
                    file_path = os.path.join(date_path, file)
                    # Get file modification time for sorting
                    file_stat = os.stat(file_path)
                    mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                    files_in_date.append((file, mod_time))
            
            if files_in_date:  # Only include dates that still have files
                files_by_date[date_dir] = files_in_date
    
    # Create updated index
    index_path = os.path.join(daily_notes_dir, 'INDEX.md')
    with open(index_path, 'w') as f:
        f.write('# Daily Notes Index\\n\\n')
        f.write(f'**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\\n\\n')
        f.write('**Note**: Cursor conversation history files (.specstory) remain in their original location\\n\\n')
        f.write('## Timeline of Work\\n\\n')
        
        total_files = 0
        for date_str in sorted(files_by_date.keys(), reverse=True):  # Most recent first
            files = files_by_date[date_str]
            if files:  # Only show dates with files
                total_files += len(files)
                f.write(f'### {date_str} ({len(files)} files)\\n\\n')
                
                # Sort files by time within the date
                files.sort(key=lambda x: x[1])  # Sort by modification time
                
                for filename, mod_time in files:
                    time_str = mod_time.strftime('%H:%M')
                    f.write(f'- **{time_str}** [{filename}]({date_str}/{filename})\\n')
                
                f.write('\\n')
        
        f.write(f'\\n**Total organized files**: {total_files}\\n\\n')
        f.write('---\\n\\n')
        f.write('*This index excludes .specstory conversation history files which remain in `.specstory/history/`*\\n')
    
    print(f'  📋 Updated: {index_path}')
    
    # Remove empty date directories
    print(f'\\n🧹 CLEANING UP EMPTY DATE DIRECTORIES:')
    
    for date_dir in os.listdir(daily_notes_dir):
        date_path = os.path.join(daily_notes_dir, date_dir)
        if os.path.isdir(date_path) and date_dir.startswith('2025-'):
            try:
                # Check if directory is empty (except for .DS_Store)
                contents = [f for f in os.listdir(date_path) if f != '.DS_Store']
                if not contents:
                    os.rmdir(date_path)
                    print(f'  🗑️  Removed empty: {date_dir}/')
            except Exception as e:
                print(f'  ⚠️  Could not remove {date_dir}: {e}')
    
    print(f'\\n✅ SPECSTORY FILES FIXED!')
    print('=' * 50)
    print('✅ Moved .specstory files back to their original location')
    print('✅ Updated daily-notes index to exclude conversation history')
    print('✅ Cleaned up empty date directories')
    
    print(f'\\n📁 CURRENT STRUCTURE:')
    print(f'  • .specstory/history/ - Cursor conversation history (unchanged)')
    print(f'  • daily-notes/ - Your markdown files organized by date')
    print(f'  • daily-notes/INDEX.md - Timeline of your work (excluding conversations)')

if __name__ == '__main__':
    fix_specstory_files()
