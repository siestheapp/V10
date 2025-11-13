#!/bin/bash

# Activate virtual environment and start the backend server
cd "$(dirname "$0")"

# Check if server is already running on port 8006
echo "🔍 Checking if server is already running on port 8006..."
if lsof -i :8006 > /dev/null 2>&1; then
    echo "⚠️  Server already running on port 8006. Stopping existing server..."
    pids=$(lsof -ti :8006)
    if [ ! -z "$pids" ]; then
        kill $pids
        echo "✅ Stopped existing server processes: $pids"
        sleep 2
    fi
else
    echo "✅ No existing server found on port 8006"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../../../venv/bin/activate

# Start the server
echo "🚀 Starting backend server on http://127.0.0.1:8006..."
python -m uvicorn app:app --host 0.0.0.0 --port 8006 --reload 