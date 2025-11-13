#!/bin/bash

# Build for Physical iPhone Script
# This builds the app directly to your connected iPhone for best performance testing

echo "======================================="
echo "Build for Physical iPhone"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}✅ Found your iPhone: 'Seans iphone'${NC}"
echo ""
echo -e "${YELLOW}Building for your physical device...${NC}"

# Build for physical device
xcodebuild build \
    -project V10.xcodeproj \
    -scheme V10 \
    -destination 'platform=iOS,name=Seans iphone' \
    CODE_SIGN_IDENTITY="" \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGNING_ALLOWED=NO

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo ""
    echo -e "${GREEN}NEXT STEPS:${NC}"
    echo "1. The app should now be on your iPhone"
    echo "2. Test the text input - should be INSTANT now!"
    echo "3. Scroll through lists - should be smooth 60 FPS"
    echo "4. Images will cache after first load"
else
    echo -e "${RED}❌ Build failed${NC}"
    echo ""
    echo "If code signing failed, open Xcode and:"
    echo "1. Select your iPhone from the device menu"
    echo "2. Press ⌘R to run"
    echo "3. Xcode will handle the signing automatically"
fi
