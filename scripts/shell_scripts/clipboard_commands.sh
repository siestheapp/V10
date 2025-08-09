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
