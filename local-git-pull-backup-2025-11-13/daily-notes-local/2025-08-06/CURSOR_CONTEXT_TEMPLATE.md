# Essential Context Files for New Cursor Chats

## Always Include These Files:

### Project Overview
- README.md
- docs/development/QUICK_REFERENCE.md  
- SIZE_RECOMMENDATION_SYSTEM_GUIDE.md

### Database Understanding
- docs/database/TAILOR3_SCHEMA.md
- docs/database/DATABASE_CONFIG.md
- database/DATABASE_EVOLUTION_SUMMARY.md (data evolution over time)
- database/backups/snapshots/2025-07-24/DATABASE_EVOLUTION_SUMMARY.md (recent data snapshot)

### Backend API
- src/ios_app/Backend/app.py (first 100 lines - main API structure)
- src/ios_app/Backend/simple_multi_dimensional_analyzer.py (class definition)

## For Specific Work Types:

### iOS Development
- src/ios_app/V10/Views/Scanning & Matching/ScanTab.swift (data models)
- src/ios_app/README.md

### Database/Web Work  
- scripts/web_garment_manager.py (first 50 lines)
- scripts/admin_garment_manager.py (first 50 lines)

## Quick Copy-Paste for @ Mentions:
```
@README.md @docs/development/QUICK_REFERENCE.md @SIZE_RECOMMENDATION_SYSTEM_GUIDE.md @docs/database/TAILOR3_SCHEMA.md @docs/database/DATABASE_CONFIG.md @database/DATABASE_EVOLUTION_SUMMARY.md @src/ios_app/Backend/app.py
```

## Ports & Services Reference:
- Port 8006: Main Flask API (src/ios_app/Backend/app.py)
- Port 5001: User Web Interface (scripts/web_garment_manager.py) 
- Port 5002: Admin Interface (scripts/admin_garment_manager.py)
- Database: Supabase PostgreSQL (tailor3)

## Key Concepts:
- Multi-dimensional fit analysis system
- User fit zones derived from closet feedback
- Brand-specific size guides with measurements
- iOS app + Flask backend + Supabase database architecture
