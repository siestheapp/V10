#!/bin/bash
# Super simple contractor preparation - since data is all fake anyway

echo "🚀 Simple Contractor Branch Setup"
echo "================================="
echo "Since all user1 data is fake test data, we can keep this simple!"
echo ""

# Make sure we're on your working branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "revert-to-a42786" ]; then
    echo "Switching to revert-to-a42786..."
    git checkout revert-to-a42786
fi

# Create contractor branch
echo "Creating contractor branch..."
git checkout -b contractor-performance-simple

echo ""
echo "🗑️  Removing ONLY the proprietary stuff..."

# Remove scrapers - this is your actual IP
rm -rf scrapers/
rm -f scripts/*scraper*.py
rm -f scripts/jcrew*.py
rm -f scripts/reiss*.py
rm -f scripts/precise*.py
git rm -rf scrapers/ 2>/dev/null || true
git rm scripts/*scraper*.py 2>/dev/null || true

# Optional: Remove production deployment configs
rm -f .env.production
rm -f railway.json
rm -f nixpacks.toml
rm -f Procfile

# Create a README for the contractor
cat > CONTRACTOR_README.md << 'EOF'
# V10 iOS Performance Optimization

## Quick Start

1. **Run the backend locally**:
   ```bash
   cd src/ios_app/Backend
   python app.py
   ```
   Backend will run on http://localhost:8006

2. **Open iOS project**:
   ```bash
   cd src/ios_app
   open V10.xcodeproj
   ```

3. **Make sure Config.swift points to localhost**:
   ```swift
   static let baseURL = "http://127.0.0.1:8006"
   ```

4. **Test with user1 account**
   - This account has random test data
   - Data is intentionally inconsistent (3XL too small, S too big, etc.)
   - This is fake data created by random button clicking

## Performance Issues to Fix

Current performance:
- Tab switching: ~450ms (target: <200ms)
- Scrolling: ~20 FPS (target: 55+ FPS)  
- Button taps: ~350ms (target: <100ms)

## What You Have

- Full iOS source code
- Backend API source
- Test database with fake user1 data
- All product/brand data

## What's Missing

- Web scrapers (proprietary, not needed for performance)
- Production credentials (not needed)

## Focus Areas

1. SwiftUI view performance
2. List/Grid scrolling optimization
3. Image loading and caching
4. Tab switching animations
5. Form responsiveness

Use Instruments to profile and identify bottlenecks.
EOF

echo ""
echo "📝 Creating simple database instructions..."

cat > DATABASE_INFO.md << 'EOF'
# Database Information

The database contains TEST DATA ONLY for user1@example.com

## To Connect Locally

1. The backend uses the connection in db_config.py
2. All data for user1 is fake/test data
3. Feel free to read any data needed for testing

## Sample Data Characteristics

- user1 has random garments with inconsistent feedback
- Sizes don't make sense (3XL marked "too small", S marked "too big")
- This is intentional - created by random testing
- There are ~50-100 test garments
- Multiple brands and products

This should be sufficient for performance testing.
EOF

echo ""
echo "✅ Simple contractor branch ready!"
echo ""
echo "📋 Next steps:"
echo "1. Review the changes:"
echo "   git status"
echo ""
echo "2. Commit the contractor version:"
echo "   git add -A"
echo "   git commit -m 'Contractor version - removed scrapers only'"
echo ""
echo "3. Push to GitHub:"
echo "   git push origin contractor-performance-simple"
echo ""
echo "4. Share with contractor:"
echo "   - Give them the branch: contractor-performance-simple"
echo "   - Explain the user1 data is all fake"
echo "   - They can run everything locally"
echo ""
echo "5. After project ends:"
echo "   - Delete the contractor branch"
echo "   - Merge any good changes back to revert-to-a42786"
echo ""

# Switch back
git checkout revert-to-a42786
echo "✅ Switched back to your working branch: revert-to-a42786"
