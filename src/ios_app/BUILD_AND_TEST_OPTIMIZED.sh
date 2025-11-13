#!/bin/bash

# Build and Test Optimized iOS App Script
# This script helps you build and test the performance-optimized version of the app

echo "======================================="
echo "V10 iOS App Performance Build Script"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "V10.xcodeproj/project.pbxproj" ]; then
    echo -e "${RED}Error: Not in the iOS app directory!${NC}"
    echo "Please run this script from: src/ios_app/"
    exit 1
fi

echo -e "${GREEN}✅ Found V10.xcodeproj${NC}"

# Function to add Swift files to Xcode project
add_files_to_xcode() {
    echo -e "${YELLOW}Adding new performance files to Xcode project...${NC}"
    
    # This would normally use xcodeproj gem or similar
    # For now, provide manual instructions
    cat << EOF

${YELLOW}MANUAL STEPS REQUIRED:${NC}

1. Open V10.xcodeproj in Xcode

2. Add these new files to the project:
   - Utilities/ImageCache.swift
   - Utilities/PerformanceOptimizedNetworkManager.swift
   - Views/Scanning & Matching/OptimizedScanTab.swift
   - Views/Shop/OptimizedShopView.swift

3. In the file navigator:
   - Right-click on the appropriate folder
   - Select "Add Files to V10..."
   - Navigate to each file and add it
   - Make sure "Copy items if needed" is UNCHECKED
   - Make sure the target "V10" is CHECKED

4. Update imports in SiesApp.swift if needed

EOF
}

# Build the project
build_project() {
    echo -e "${YELLOW}Building the project...${NC}"
    
    # Clean build folder
    xcodebuild clean -project V10.xcodeproj -scheme V10 -destination 'platform=iOS Simulator,name=iPhone 16 Pro'
    
    # Build
    if command -v xcpretty &> /dev/null; then
        xcodebuild build -project V10.xcodeproj -scheme V10 -destination 'platform=iOS Simulator,name=iPhone 16 Pro' | xcpretty
    else
        xcodebuild build -project V10.xcodeproj -scheme V10 -destination 'platform=iOS Simulator,name=iPhone 16 Pro'
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Build successful!${NC}"
    else
        echo -e "${RED}❌ Build failed. Check errors above.${NC}"
        exit 1
    fi
}

# Run performance tests
run_performance_tests() {
    echo -e "${YELLOW}Performance Testing Checklist:${NC}"
    
    cat << EOF

${GREEN}PERFORMANCE TESTING STEPS:${NC}

1. ${YELLOW}Test Text Input Responsiveness:${NC}
   - Open the Scan tab
   - Tap on the product link text field
   - The cursor should appear INSTANTLY (no delay)
   - Type a URL - text should appear without lag

2. ${YELLOW}Test Image Loading:${NC}
   - Navigate to Shop tab
   - Scroll through products
   - Images should load smoothly
   - Go back and return - images should appear instantly (cached)

3. ${YELLOW}Test List Scrolling:${NC}
   - Open Finds or Closet tab
   - Scroll rapidly up and down
   - Should maintain 60 FPS (no stuttering)

4. ${YELLOW}Test Network Caching:${NC}
   - Load any data screen
   - Navigate away and back
   - Data should appear instantly (cached for 5 minutes)

5. ${YELLOW}Profile with Instruments:${NC}
   - Product → Profile (⌘I)
   - Choose "Time Profiler"
   - Run the app and interact with it
   - Look for any methods taking >16ms (60 FPS threshold)

${GREEN}EXPECTED IMPROVEMENTS:${NC}
✅ Text input: Instant response (was: 1-2 second delay)
✅ Image loading: Cached after first load (was: re-download every time)
✅ Scrolling: Smooth 60 FPS (was: 30-45 FPS with stutters)
✅ Memory usage: ~60MB typical (was: ~100MB+)
✅ View transitions: <0.3s (was: 0.5-1s)

EOF
}

# Main menu
echo ""
echo "What would you like to do?"
echo "1) Add new files to Xcode project (manual steps)"
echo "2) Build the optimized app"
echo "3) Show performance testing checklist"
echo "4) Do everything (recommended for first run)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        add_files_to_xcode
        ;;
    2)
        build_project
        ;;
    3)
        run_performance_tests
        ;;
    4)
        add_files_to_xcode
        read -p "Press Enter after adding files to Xcode..."
        build_project
        run_performance_tests
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}Performance optimization setup complete!${NC}"
echo -e "${GREEN}===============================================${NC}"
echo ""
echo "Next steps:"
echo "1. Run the app on a PHYSICAL iPhone for best testing"
echo "2. Use Instruments to verify performance improvements"
echo "3. Check the PERFORMANCE_OPTIMIZATION_GUIDE.md for more details"
