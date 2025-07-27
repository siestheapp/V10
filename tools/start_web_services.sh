#!/bin/bash

# Activate virtual environment and start the web services
cd "$(dirname "$0")"

# Check if servers are already running on ports 5001 and 5002
echo "🔍 Checking if servers are already running on ports 5001 and 5002..."

# Check port 5001 (Web Garment Manager)
if lsof -i :5001 > /dev/null 2>&1; then
    echo "⚠️  Server already running on port 5001. Stopping existing server..."
    pids=$(lsof -ti :5001)
    if [ ! -z "$pids" ]; then
        kill $pids
        echo "✅ Stopped existing server processes on port 5001: $pids"
        sleep 2
    fi
else
    echo "✅ No existing server found on port 5001"
fi

# Check port 5002 (Admin Interface)
if lsof -i :5002 > /dev/null 2>&1; then
    echo "⚠️  Server already running on port 5002. Stopping existing server..."
    pids=$(lsof -ti :5002)
    if [ ! -z "$pids" ]; then
        kill $pids
        echo "✅ Stopped existing server processes on port 5002: $pids"
        sleep 2
    fi
else
    echo "✅ No existing server found on port 5002"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../venv/bin/activate

# Start the Web Garment Manager (port 5001)
echo "🚀 Starting Web Garment Manager on http://127.0.0.1:5001..."
python ../scripts/admin/web_garment_manager.py &

# Start the Admin Interface (port 5002)
echo "🔧 Starting Admin Interface on http://127.0.0.1:5002..."
python ../scripts/admin/admin_garment_manager.py &

echo "✅ Both web services started!"
echo "📱 Web Garment Manager: http://localhost:5001"
echo "🔧 Admin Interface: http://localhost:5002/admin/login"
echo ""
echo "Press Ctrl+C to stop all servers"
wait 