#!/bin/bash

# Start web services with port cleanup
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

# Start the web services
echo "🚀 Starting web services..."
./tools/start_web_services.sh