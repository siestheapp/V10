#!/bin/bash

echo "======================================"
echo "Fixing Xcode File References"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Files that need to be added to Xcode:${NC}"
echo ""
echo "✅ V10/Utilities/ImageCache.swift"
echo "✅ V10/Utilities/PerformanceOptimizedNetworkManager.swift"
echo "✅ V10/Views/Scanning & Matching/OptimizedScanTab.swift"
echo "✅ V10/Views/Shop/OptimizedShopView.swift"
echo ""

echo -e "${YELLOW}INSTRUCTIONS:${NC}"
echo ""
echo "1. In Xcode, select ALL files with question marks (?) and press Delete"
echo "   Choose 'Remove Reference' (not 'Move to Trash')"
echo ""
echo "2. Drag and drop these files from Finder into Xcode:"
echo ""

# Get full paths for easy copying
echo "   Copy these paths:"
pwd_path=$(pwd)
echo "   $pwd_path/V10/Utilities/ImageCache.swift"
echo "   $pwd_path/V10/Utilities/PerformanceOptimizedNetworkManager.swift"
echo "   $pwd_path/V10/Views/Scanning & Matching/OptimizedScanTab.swift"
echo "   $pwd_path/V10/Views/Shop/OptimizedShopView.swift"
echo ""
echo "3. When dragging files into Xcode:"
echo "   - Drag directly onto the correct folder"
echo "   - In the dialog:"
echo "     ❌ UNCHECK 'Copy items if needed'"
echo "     ✅ CHECK 'V10' target"
echo "     ✅ SELECT 'Create groups'"
echo ""
echo -e "${GREEN}Opening Finder to the right location...${NC}"

# Open Finder windows for easy drag-and-drop
open "V10/Utilities/"
open "V10/Views/Scanning & Matching/"
open "V10/Views/Shop/"

echo ""
echo "Finder windows opened! Drag the .swift files into Xcode."
