#!/bin/bash

# Master startup script for V10 project with separate terminals
# Opens separate terminal windows for backend and web services

echo "🚀 Starting V10 Development Environment in separate terminals..."
echo "============================================"

# Navigate to project root
cd "$(dirname "$0")"

# Function to check if a port is in use and kill processes
check_and_kill_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  Port $port is already in use. Stopping existing processes..."
        pids=$(lsof -ti :$port)
        if [ ! -z "$pids" ]; then
            kill $pids
            echo "✅ Stopped processes on port $port: $pids"
            sleep 2
        fi
    else
        echo "✅ Port $port is available"
    fi
}

# Check all required ports
echo "🔍 Checking and cleaning up ports..."
check_and_kill_port 8006  # Backend server
check_and_kill_port 5001  # Web Garment Manager
check_and_kill_port 5002  # Admin Interface

echo ""
echo "🖥️  Opening separate terminal windows..."

# Start backend server in new terminal
osascript -e "tell application \"Terminal\" to do script \"cd '$PWD/src/ios_app/Backend' && source ../../../venv/bin/activate && echo '🚀 Backend Server Starting...' && python -m uvicorn app:app --host 0.0.0.0 --port 8006 --reload\""

# Wait a moment for the backend to start
sleep 2

# Start web services in another new terminal
osascript -e "tell application \"Terminal\" to do script \"cd '$PWD' && echo '🌐 Web Services Starting...' && ./tools/start_web_services.sh\""

echo ""
echo "✅ All services are starting in separate terminals!"
echo "============================================"
echo "📱 Backend Server: http://localhost:8006 (Terminal 1)"
echo "🌐 Web Garment Manager: http://localhost:5001 (Terminal 2)"
echo "🔧 Admin Interface: http://localhost:5002/admin/login (Terminal 2)"
echo ""
echo "💡 Each service has its own terminal window for easier debugging"
echo "💡 Close terminal windows or press Ctrl+C in each to stop services"
echo "============================================"