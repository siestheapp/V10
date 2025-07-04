# Database Directory

This directory contains all database-related files and snapshots.

## Structure

- **backups/** - Database backup files
- **snapshots/** - Current database snapshots and evolution tracking
- **old_schemas/** - Legacy schema files and old database versions

## Current Database

The current database is hosted on Supabase and uses the **tailor3** schema.

## Snapshots

Current snapshots are stored in `supabase/snapshots/` and include:
- Schema evolution tracking
- Database snapshots with sample data
- Change logs

## Old Schemas

The `old_schemas/` directory contains:
- **tailor2/** - Previous database schema (legacy)
- **tailor3_schema_dump.sql** - Initial tailor3 schema dump
- **database_snapshots/** - Old snapshot files

## Usage

- Current snapshots: `supabase/snapshots/`
- Schema file: `supabase/schema.sql`
- Change logs: `supabase/change_logs/`

## Notes

- The current working schema is in `supabase/schema.sql`
- All active development uses the tailor3 schema
- Old schemas are kept for reference and rollback purposes 