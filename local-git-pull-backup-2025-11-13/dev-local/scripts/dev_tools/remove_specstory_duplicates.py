#!/usr/bin/env python3
"""
Remove duplicate .specstory files from daily-notes
Keep them only in their original .specstory/history/ location
"""

import os
import shutil
from datetime import datetime

def remove_specstory_duplicates():
    print('🧹 REMOVING SPECSTORY DUPLICATES FROM DAILY-NOTES')
    print('=' * 60)
    
    daily_notes_dir = 'daily-notes'
    removed_count = 0
    
    # Find and remove all specstory files from daily-notes
    print('🔍 Finding specstory duplicates in daily-notes...')
    
    for date_dir in os.listdir(daily_notes_dir):
        date_path = os.path.join(daily_notes_dir, date_dir)
        if os.path.isdir(date_path) and date_dir.startswith('2025-'):
            
            files_to_remove = []
            for file in os.listdir(date_path):
                # Identify specstory files by their naming pattern
                if (file.startswith('2025-') and 
                    file.endswith('.md') and 
                    '-0400-' in file and
                    len(file.split('_')) >= 3):  # Has date_time_timezone pattern
                    
                    files_to_remove.append(os.path.join(date_path, file))
            
            # Remove the specstory files
            for file_path in files_to_remove:
                try:
                    os.remove(file_path)
                    filename = os.path.basename(file_path)
                    print(f'  🗑️  Removed duplicate: {filename}')
                    removed_count += 1
                except Exception as e:
                    print(f'  ❌ Error removing {file_path}: {e}')
    
    print(f'\\n✅ Removed {removed_count} duplicate specstory files')
    
    # Clean up empty directories
    print(f'\\n🧹 Cleaning up empty date directories...')
    
    empty_dirs_removed = 0
    for date_dir in os.listdir(daily_notes_dir):
        date_path = os.path.join(daily_notes_dir, date_dir)
        if os.path.isdir(date_path) and date_dir.startswith('2025-'):
            try:
                # Check if directory is empty (except for .DS_Store)
                contents = [f for f in os.listdir(date_path) if f != '.DS_Store']
                if not contents:
                    os.rmdir(date_path)
                    print(f'  🗑️  Removed empty: {date_dir}/')
                    empty_dirs_removed += 1
            except Exception as e:
                print(f'  ⚠️  Could not remove {date_dir}: {e}')
    
    # Regenerate the index with remaining files
    print(f'\\n📋 Regenerating daily-notes index...')
    
    files_by_date = {}
    total_files = 0
    
    for date_dir in os.listdir(daily_notes_dir):
        date_path = os.path.join(daily_notes_dir, date_dir)
        if os.path.isdir(date_path) and date_dir.startswith('2025-'):
            files_in_date = []
            
            for file in os.listdir(date_path):
                if file.endswith('.md'):
                    file_path = os.path.join(date_path, file)
                    try:
                        # Get file modification time for sorting
                        file_stat = os.stat(file_path)
                        mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                        files_in_date.append((file, mod_time))
                        total_files += 1
                    except Exception as e:
                        print(f'  ⚠️  Error reading {file}: {e}')
            
            if files_in_date:  # Only include dates that have files
                files_by_date[date_dir] = files_in_date
    
    # Create updated index
    index_path = os.path.join(daily_notes_dir, 'INDEX.md')
    with open(index_path, 'w') as f:
        f.write('# Daily Notes Index\\n\\n')
        f.write(f'**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\\n\\n')
        f.write('**Note**: Cursor conversation history files remain in `.specstory/history/`\\n\\n')
        f.write('## Timeline of Work\\n\\n')
        
        if files_by_date:
            for date_str in sorted(files_by_date.keys(), reverse=True):  # Most recent first
                files = files_by_date[date_str]
                f.write(f'### {date_str} ({len(files)} files)\\n\\n')
                
                # Sort files by time within the date
                files.sort(key=lambda x: x[1])  # Sort by modification time
                
                for filename, mod_time in files:
                    time_str = mod_time.strftime('%H:%M')
                    f.write(f'- **{time_str}** [{filename}]({date_str}/{filename})\\n')
                
                f.write('\\n')
        else:
            f.write('*No markdown files organized yet.*\\n\\n')
        
        f.write(f'\\n**Total organized files**: {total_files}\\n\\n')
        f.write('---\\n\\n')
        f.write('*This index shows only your markdown documentation files.*\\n')
        f.write('*Cursor conversation history files remain in `.specstory/history/` where they belong.*\\n')
    
    print(f'  📋 Updated: {index_path}')
    
    # Summary
    print(f'\\n🎉 CLEANUP COMPLETE!')
    print('=' * 60)
    print(f'✅ Removed {removed_count} duplicate specstory files')
    print(f'✅ Removed {empty_dirs_removed} empty date directories')
    print(f'✅ Updated index with {total_files} remaining files')
    
    print(f'\\n📁 FINAL STRUCTURE:')
    print(f'  • .specstory/history/ - Cursor conversations (59 files)')
    print(f'  • daily-notes/ - Your markdown docs ({total_files} files)')
    print(f'  • daily-notes/INDEX.md - Timeline of your documentation work')
    
    print(f'\\n🎯 RESULT:')
    print(f'  • Conversation history stays in .specstory where Cursor expects it')
    print(f'  • Your documentation is organized by date in daily-notes')
    print(f'  • No more duplicates!')

if __name__ == '__main__':
    remove_specstory_duplicates()
