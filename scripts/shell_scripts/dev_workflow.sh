#!/bin/bash

# Fast Development Workflow Script
# Run this to set up a fast development environment

echo "🚀 Setting up fast development workflow..."

# Function to start backend
start_backend() {
    echo "🔧 Starting backend server..."
    cd /Users/seandavey/projects/V10
    source venv/bin/activate
    python3 src/ios_app/Backend/app.py &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID)"
    echo "   API available at: http://localhost:8006"
}

# Function to test API quickly
test_api() {
    echo "🧪 Testing API endpoints..."
    cd /Users/seandavey/projects/V10
    source venv/bin/activate
    python3 tests/quick_api_test.py
}

# Function to open Xcode
open_xcode() {
    echo "📱 Opening Xcode..."
    open src/ios_app/V10.xcodeproj
}

# Function to show development tips
show_tips() {
    echo ""
    echo "💡 Development Tips for Speed:"
    echo "1. Use SwiftUI Canvas for instant UI previews"
    echo "2. Test API with: python3 tests/quick_api_test.py"
    echo "3. Use mock data by setting useMockData = true"
    echo "4. Test backend changes without iOS rebuild"
    echo "5. Use curl for quick API testing:"
    echo "   curl -X POST http://localhost:8006/garment/size-recommendation \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"product_url\":\"https://bananarepublic.gap.com/browse/product.do?pid=704275052\",\"user_id\":1}'"
    echo ""
}

# Main menu
while true; do
    echo ""
    echo "🔧 Fast Development Workflow"
    echo "1. Start backend server"
    echo "2. Test API endpoints"
    echo "3. Open Xcode"
    echo "4. Show development tips"
    echo "5. Exit"
    echo ""
    read -p "Choose option (1-5): " choice
    
    case $choice in
        1)
            start_backend
            ;;
        2)
            test_api
            ;;
        3)
            open_xcode
            ;;
        4)
            show_tips
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option"
            ;;
    esac
done
