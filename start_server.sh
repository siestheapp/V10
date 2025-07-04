#!/bin/bash
# V10 Project Startup Script
# Starts both web interfaces (user and admin)

echo "🚀 Starting V10 Web Interfaces..."

# Check if ports are available
if lsof -ti:5001 -ti:5002 > /dev/null 2>&1; then
    echo "⚠️  Ports 5001 or 5002 are already in use. Stopping existing processes..."
    lsof -ti:5001 -ti:5002 | xargs kill -9
fi

# Activate virtual environment
source venv/bin/activate

# Start user interface (port 5001)
echo "📱 Starting User Interface on port 5001..."
python scripts/web_garment_manager.py &

# Start admin interface (port 5002)
echo "🔧 Starting Admin Interface on port 5002..."
python scripts/admin_garment_manager.py &

echo "✅ Both interfaces started!"
echo "🌐 User Interface: http://localhost:5001"
echo "🔧 Admin Interface: http://localhost:5002 (admin/admin123)"
echo ""
echo "Press Ctrl+C to stop all servers"
wait
