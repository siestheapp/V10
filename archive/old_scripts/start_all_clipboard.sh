#!/bin/bash

# Master startup script for V10 project with clipboard automation
# Starts services and copies monitoring commands to clipboard

echo "🚀 Starting V10 Development Environment with clipboard automation..."
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

# Save PIDs to file for easy cleanup
echo "$BACKEND_PID $WEB_MANAGER_PID $ADMIN_PID" > logs/pids.txt

# Copy first command to clipboard
BACKEND_CMD="cd /Users/seandavey/projects/V10 && tail -f logs/backend.log"
echo "$BACKEND_CMD" | pbcopy

echo "📋 CLIPBOARD AUTOMATION READY!"
echo "============================================"
echo "📋 Step 1: Backend monitoring command copied to clipboard!"
echo "   👆 Open a new Cursor terminal and paste (Cmd+V)"
echo ""
echo "📋 Step 2: After pasting backend command, run this to get web manager:"
echo "   echo 'cd /Users/seandavey/projects/V10 && tail -f logs/web_manager.log' | pbcopy"
echo ""
echo "📋 Step 3: After pasting web manager command, run this to get admin:"
echo "   echo 'cd /Users/seandavey/projects/V10 && tail -f logs/admin.log' | pbcopy"
echo ""
echo "🔧 Quick clipboard commands saved to: clipboard_commands.sh"

# Create a helper script for the clipboard commands
cat > clipboard_commands.sh << 'EOF'
#!/bin/bash
echo "📋 V10 Clipboard Helper"
echo "======================="
echo "1) Copy backend command"
echo "2) Copy web manager command" 
echo "3) Copy admin command"
echo "4) Copy stop command"
echo ""
read -p "Select option (1-4): " choice

case $choice in
    1)
        echo "cd /Users/seandavey/projects/V10 && tail -f logs/backend.log" | pbcopy
        echo "✅ Backend monitoring command copied to clipboard!"
        ;;
    2)
        echo "cd /Users/seandavey/projects/V10 && tail -f logs/web_manager.log" | pbcopy
        echo "✅ Web manager monitoring command copied to clipboard!"
        ;;
    3)
        echo "cd /Users/seandavey/projects/V10 && tail -f logs/admin.log" | pbcopy
        echo "✅ Admin monitoring command copied to clipboard!"
        ;;
    4)
        echo "cd /Users/seandavey/projects/V10 && ./stop_all.sh" | pbcopy
        echo "✅ Stop all services command copied to clipboard!"
        ;;
    *)
        echo "❌ Invalid option"
        ;;
esac
EOF

chmod +x clipboard_commands.sh

echo ""
echo "💡 Services are running in background (PIDs: $BACKEND_PID, $WEB_MANAGER_PID, $ADMIN_PID)"
echo "💡 To stop all services: v10-stop (or run the copied stop command)"
echo "💡 For more clipboard commands: ./clipboard_commands.sh"
echo "============================================"