#!/bin/bash
# Setup script for automated schema evolution tracking

# Get the current directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create cron job to run schema evolution daily at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * cd $PROJECT_DIR && python3 scripts/schema_evolution.py >> logs/schema_evolution.log 2>&1") | crontab -

echo "✅ Daily schema evolution cron job added (runs at 2 AM)"
echo "📁 Logs will be saved to: $PROJECT_DIR/logs/schema_evolution.log" 