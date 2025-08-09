#!/bin/bash

# Stop all V10 services script

echo "🛑 Stopping V10 Development Services..."

cd "$(dirname "$0")"

# Check if PID file exists
if [ -f "logs/pids.txt" ]; then
    echo "📋 Reading service PIDs from logs/pids.txt..."
    PIDS=$(cat logs/pids.txt)
    echo "🔧 Stopping services (PIDs: $PIDS)..."
    kill $PIDS 2>/dev/null
    rm logs/pids.txt
    echo "✅ Services stopped and PID file cleaned up"
else
    echo "🔍 No PID file found, stopping by port..."
    # Fallback: kill by port
    for port in 8006 5001 5002; do
        if lsof -i :$port > /dev/null 2>&1; then
            pids=$(lsof -ti :$port)
            if [ ! -z "$pids" ]; then
                kill $pids
                echo "✅ Stopped processes on port $port: $pids"
            fi
        fi
    done
fi

echo "🎉 All V10 services stopped!"