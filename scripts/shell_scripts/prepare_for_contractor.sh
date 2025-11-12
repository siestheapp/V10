#!/bin/bash

# Script to prepare codebase for contractor
# This creates a clean version without sensitive data

echo "🔧 Preparing V10 codebase for contractor..."

# Create contractor branch
echo "Creating contractor branch..."
git checkout -b contractor-debug-$(date +%Y%m%d)

# Create contractor directory
CONTRACTOR_DIR="V10-contractor-version"
echo "Creating $CONTRACTOR_DIR directory..."

# Copy iOS app only (no backend secrets)
mkdir -p $CONTRACTOR_DIR
cp -R src/ios_app $CONTRACTOR_DIR/
cp CONTRACTOR_SETUP_GUIDE.md $CONTRACTOR_DIR/README.md

# Remove sensitive backend files
echo "Removing sensitive files..."
rm -rf $CONTRACTOR_DIR/ios_app/Backend/body_measurement_estimator.py
rm -rf $CONTRACTOR_DIR/ios_app/Backend/multi_dimensional_fit_analyzer.py
rm -rf $CONTRACTOR_DIR/ios_app/Backend/fit_zone_calculator.py
rm -rf $CONTRACTOR_DIR/ios_app/Backend/app.py
rm -rf $CONTRACTOR_DIR/ios_app/Backend/main.py

# Create mock backend file instead
cat > $CONTRACTOR_DIR/ios_app/Backend/mock_backend.py << 'EOF'
"""
Mock backend for contractor debugging
Real backend implementation not included for security
"""
print("This is a mock backend file. Use the iOS mock data provider instead.")
EOF

# Remove any .env files
find $CONTRACTOR_DIR -name ".env*" -delete
find $CONTRACTOR_DIR -name "*.sql" -delete
find $CONTRACTOR_DIR -name "db_config.py" -delete

# Create a .gitignore for safety
cat > $CONTRACTOR_DIR/.gitignore << 'EOF'
.env
.env.*
*.sql
db_config.py
*.p12
*.cer
*.mobileprovision
.DS_Store
EOF

# Create setup script for contractor
cat > $CONTRACTOR_DIR/setup.sh << 'EOF'
#!/bin/bash
echo "V10 iOS App Setup"
echo "================="
echo ""
echo "1. Open src/ios_app/V10.xcodeproj in Xcode"
echo "2. Select an iPhone simulator"
echo "3. Build and run (Cmd+R)"
echo ""
echo "The app will run in mock mode with test data."
echo "See README.md for performance debugging instructions."
EOF

chmod +x $CONTRACTOR_DIR/setup.sh

# Create a zip file
echo "Creating zip file..."
zip -r V10-contractor-version.zip $CONTRACTOR_DIR -x "*.DS_Store" "*__pycache__*"

echo "✅ Done! Contractor version prepared:"
echo "   Directory: $CONTRACTOR_DIR/"
echo "   Zip file: V10-contractor-version.zip"
echo ""
echo "⚠️  Before sharing:"
echo "   1. Review $CONTRACTOR_DIR/ to ensure no sensitive data"
echo "   2. Have contractor sign NDA"
echo "   3. Share only the zip file via Upwork"
echo ""
echo "📝 Next steps:"
echo "   1. git add -A && git commit -m 'Contractor version'"
echo "   2. Upload V10-contractor-version.zip to Upwork"
echo "   3. Share CONTRACTOR_SETUP_GUIDE.md separately"

