#!/bin/bash

# Quick monitor script for V10 services
cd "$(dirname "$0")"

if [ ! -d "logs" ]; then
    echo "❌ No logs directory found. Run 'v10' first to start services."
    exit 1
fi

echo "📊 V10 Service Monitor"
echo "====================="
echo "1) Backend Server logs"
echo "2) Web Manager logs" 
echo "3) Admin Interface logs"
echo "4) All services status"
echo "5) Stop all services"
echo ""
read -p "Select option (1-5): " choice

case $choice in
    1)
        echo "🚀 Monitoring Backend Server logs (Ctrl+C to exit)..."
        tail -f logs/backend.log
        ;;
    2)
        echo "🌐 Monitoring Web Manager logs (Ctrl+C to exit)..."
        tail -f logs/web_manager.log
        ;;
    3)
        echo "🔧 Monitoring Admin Interface logs (Ctrl+C to exit)..."
        tail -f logs/admin.log
        ;;
    4)
        echo "📊 Service Status:"
        echo "=================="
        for port in 8006 5001 5002; do
            if lsof -i :$port > /dev/null 2>&1; then
                echo "✅ Port $port: Running"
            else
                echo "❌ Port $port: Not running"
            fi
        done
        echo ""
        echo "📱 Backend Server: http://localhost:8006"
        echo "🌐 Web Manager: http://localhost:5001"
        echo "🔧 Admin Interface: http://localhost:5002/admin/login"
        ;;
    5)
        ./stop_all.sh
        ;;
    *)
        echo "❌ Invalid option"
        ;;
esac