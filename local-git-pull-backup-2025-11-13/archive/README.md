# Archive Directory

This directory contains archived files and old versions of the project.

## Structure

- **large_files/** - Very large files (>100MB) that are kept for reference
  - `V10_Project_2025-02-25.txt.zip` (5.6GB) - Large project backup
- **old_code/** - Old code files and backups
  - `codebase_v10_june282025.txt` (23MB) - Old codebase dump
  - `v10_summary.txt` (31MB) - Old project summary
  - `codepart_*` files - Old code partitions
  - `V10_backup_feb12/` - Old V10 backup from February 2025
- **SCHEMA_EVOLUTION.md** - Old schema evolution documentation
- **brands_data.sql** - Old brands data

## Notes

- **Large files are kept for reference only** - they are not needed for current development
- **Old code files** may contain useful historical information but are not part of the current codebase
- **Consider cleaning up** large files if they're no longer needed
- **Current development** uses files in the root directory and `scripts/`

## Cleanup Recommendations

- The 5.6GB zip file can be deleted if no longer needed
- Old code files can be deleted if they don't contain unique information
- Keep only files that contain valuable historical data or are needed for rollback 