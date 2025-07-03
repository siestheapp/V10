#!/bin/bash
# ⚠️  NOTE: Backend is currently configured for local tailor2 database
#     Should be updated to use Supabase tailor3 database
#     See DATABASE_CONFIG.md for correct configuration
source venv/bin/activate
cd V10/V10/Backend
uvicorn app:app --host 0.0.0.0 --port 8006 --reload
