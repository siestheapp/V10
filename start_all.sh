#!/bin/bash

# Master startup script for V10 project
# Starts backend server (port 8006) and web services (ports 5001, 5002)

echo "🚀 Starting V10 Development Environment..."
echo "============================================"

# Navigate to project root
cd "$(dirname "$0")"

# Function to check if a port is in use
check_port() {
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
echo "🔍 Checking ports..."
check_port 8006  # Backend server
check_port 5001  # Web Garment Manager
check_port 5002  # Admin Interface

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Start backend server in background
echo "🚀 Starting backend server on http://127.0.0.1:8006..."
cd src/ios_app/Backend
python -m uvicorn app:app --host 0.0.0.0 --port 8006 --reload &
BACKEND_PID=$!
cd ../../..

# Start Web Garment Manager in background
echo "🚀 Starting Web Garment Manager on http://127.0.0.1:5001..."
python scripts/admin/web_garment_manager.py &
WEB_MANAGER_PID=$!

# Start Admin Interface in background
echo "🔧 Starting Admin Interface on http://127.0.0.1:5002..."
python scripts/admin/admin_garment_manager.py &
ADMIN_PID=$!

echo ""
echo "✅ All services started successfully!"
echo "============================================"
echo "📱 Backend Server: http://localhost:8006"
echo "🌐 Web Garment Manager: http://localhost:5001"
echo "🔧 Admin Interface: http://localhost:5002/admin/login"
echo ""
echo "💡 To stop all services, press Ctrl+C"
echo "============================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID $WEB_MANAGER_PID $ADMIN_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait