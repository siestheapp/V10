#!/bin/bash

# Master startup script for V10 project with separate Cursor terminals
# Opens separate terminal tabs/panes in Cursor for backend and web services

echo "🚀 Starting V10 Development Environment in Cursor terminals..."
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
echo "🖥️  Starting services in background with separate log files..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Start backend server in background with log file
echo "🚀 Starting backend server on http://127.0.0.1:8006..."
cd src/ios_app/Backend
source ../../../venv/bin/activate
nohup python -m uvicorn app:app --host 0.0.0.0 --port 8006 --reload > ../../../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ../../..

# Start Web Garment Manager in background with log file
echo "🚀 Starting Web Garment Manager on http://127.0.0.1:5001..."
source venv/bin/activate
nohup python scripts/admin/web_garment_manager.py > logs/web_manager.log 2>&1 &
WEB_MANAGER_PID=$!

# Start Admin Interface in background with log file
echo "🔧 Starting Admin Interface on http://127.0.0.1:5002..."
nohup python scripts/admin/admin_garment_manager.py > logs/admin.log 2>&1 &
ADMIN_PID=$!

# Wait a moment for services to start
sleep 3

echo ""
echo "✅ All services started successfully!"
echo "============================================"
echo "📱 Backend Server: http://localhost:8006"
echo "🌐 Web Garment Manager: http://localhost:5001"
echo "🔧 Admin Interface: http://localhost:5002/admin/login"
echo ""
echo "📋 To monitor logs in separate Cursor terminals:"
echo "   Backend:     tail -f logs/backend.log"
echo "   Web Manager: tail -f logs/web_manager.log" 
echo "   Admin:       tail -f logs/admin.log"
echo ""
echo "💡 Services are running in background (PIDs: $BACKEND_PID, $WEB_MANAGER_PID, $ADMIN_PID)"
echo "💡 To stop all services: kill $BACKEND_PID $WEB_MANAGER_PID $ADMIN_PID"
echo "============================================"

# Save PIDs to file for easy cleanup
echo "$BACKEND_PID $WEB_MANAGER_PID $ADMIN_PID" > logs/pids.txt
echo "🔧 Service PIDs saved to logs/pids.txt"