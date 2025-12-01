#!/bin/bash
# Script to prepare a safe contractor branch from revert-to-a42786

echo "🔒 Preparing contractor-safe branch from revert-to-a42786..."

# Make sure we're on the right branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "revert-to-a42786" ]; then
    echo "⚠️  You're on $CURRENT_BRANCH, switching to revert-to-a42786..."
    git checkout revert-to-a42786
fi

# Pull latest changes if any
echo "📥 Ensuring revert-to-a42786 is up to date..."
git pull origin revert-to-a42786 2>/dev/null || echo "Branch is up to date or not tracking remote"

# Create new contractor branch from your working branch
echo "🌿 Creating contractor branch from revert-to-a42786..."
git checkout -b contractor-ios-performance-2025-09

echo "📁 Removing sensitive files..."

# Remove all sensitive files
rm -f db_config.py
rm -f .env .env.* 
rm -rf database_dumps/
rm -rf database_exports/
rm -rf venv/
rm -rf __pycache__/
rm -f *.sql
rm -f *dump*.json
rm -f tailor3_*.sql
rm -rf daily-notes/  # Remove all daily notes with sensitive info

# Remove backend files with proprietary logic
echo "🔐 Removing proprietary backend algorithms..."
rm -f src/ios_app/Backend/body_measurement_estimator.py
rm -f src/ios_app/Backend/multi_dimensional_fit_analyzer.py
rm -f src/ios_app/Backend/unified_product_fetcher.py
rm -f src/ios_app/Backend/app.py
rm -f src/ios_app/Backend/app_unified_update.py
rm -f src/ios_app/Backend/category_normalizer.py

# Remove scraper files (proprietary scraping logic)
echo "🕷️ Removing scrapers..."
rm -rf scrapers/
rm -rf scripts/

echo "🔧 Creating mock configurations..."

# Create mock backend indicator
cat > src/ios_app/Backend/CONTRACTOR_MODE << 'EOF'
This backend directory has been sanitized for contractor access.
Only mock endpoints are available.
No real data or algorithms are present.
DO NOT attempt to access production servers.
EOF

# Create mock db_config to prevent errors
cat > db_config.py << 'EOF'
# Mock configuration for contractors
# DO NOT add real credentials here
DB_CONFIG = {
    'user': 'mock_user',
    'password': 'mock_password', 
    'host': 'localhost',
    'port': 5432,
    'database': 'mock_v10'
}

# Mock environment - no real connections
SUPABASE_URL = "https://mock.supabase.co"
SUPABASE_ANON_KEY = "mock-key"
EOF

echo "📱 Configuring iOS app for contractor mode..."

# Update iOS Config to force mock mode (backup original first)
if [ -f "src/ios_app/V10/App/Config.swift" ]; then
    cp src/ios_app/V10/App/Config.swift src/ios_app/V10/App/Config.swift.backup
fi

cat > src/ios_app/V10/App/Config.swift << 'EOF'
import Foundation

struct Config {
    // CONTRACTOR VERSION - Mock mode only
    // DO NOT MODIFY THESE VALUES
    static let baseURL = "mock://contractor-testing"
    static let contractorMode = true
    static let performanceTestingEnabled = true
    
    // Mock configuration for performance testing
    static let mockDataDelay = 0.0  // No delay for UI performance testing
    static let mockDataVolume = 1000  // Large dataset for stress testing
    
    // Mock user credentials
    static let defaultUserId = "mock-user"
    static let defaultUserName = "contractor@test.com"
    
    // Disabled features in contractor mode
    static let uniqloURLTemplate = "https://disabled.com"
}
EOF

echo "📝 Creating contractor documentation..."

cat > CONTRACTOR_README.md << 'EOF'
# V10 iOS Performance Optimization Project

## ⚠️ CONTRACTOR ACCESS VERSION
This is a sanitized version of the codebase. You have access to iOS code only.

## Your Mission
Optimize the V10 iOS app to eliminate UI lag when:
- Clicking buttons (currently ~350ms response time)
- Switching between tabs (currently ~450ms) 
- Scrolling through lists (currently ~20 FPS)
- Loading images (visible delays)

## Performance Targets
- **Tab switches**: < 200ms (currently ~450ms)
- **Scroll FPS**: > 55 FPS (currently ~20 FPS)  
- **Memory growth**: < 50MB per session
- **Button response**: < 100ms (currently ~350ms)

## What You Have Access To
✅ Complete iOS app source code (SwiftUI)
✅ Mock data provider for testing
✅ Xcode project files
✅ Performance baseline metrics

## What You DON'T Have Access To
❌ Production servers or APIs
❌ Real user data
❌ Database
❌ Backend algorithms
❌ API credentials
❌ Web scrapers
❌ Proprietary business logic

## Getting Started

1. **Open the project**:
   ```bash
   cd src/ios_app
   open V10.xcodeproj
   ```

2. **Build and run** on iPhone 15 Pro simulator (or similar)

3. **Profile with Instruments** (Cmd+I in Xcode):
   - Time Profiler (for CPU bottlenecks)
   - Core Animation (for FPS issues)
   - SwiftUI (for view updates)
   - Allocations (for memory leaks)

## Key Files to Investigate

### Tab Navigation Performance
- `src/ios_app/V10/Views/MainTabView.swift`
- `src/ios_app/V10/ViewModels/TabViewModel.swift`

### Scrolling Performance  
- `src/ios_app/V10/Views/Shop/ShopView.swift` - Grid with images
- `src/ios_app/V10/Views/Closet/TryOnHistoryView.swift` - Long lists
- `src/ios_app/V10/Views/Fit Feedback/FitFeedbackView.swift` - Complex forms

### Image Loading
- Look for AsyncImage usage
- Check for missing caching
- Verify image sizing

### Common SwiftUI Performance Issues to Check

1. **Unnecessary View Updates**:
   - Missing @StateObject vs @ObservedObject
   - Excessive @State changes
   - Missing .id() modifiers in lists

2. **Heavy View Bodies**:
   - Complex computations in body
   - Missing lazy loading
   - Nested ForEach without optimization

3. **Memory Leaks**:
   - Retain cycles in closures
   - Unneeded strong references
   - Images not released

## Deliverables Expected

### Week 1 (Audit Phase)
1. Performance audit document with Instruments screenshots
2. List of specific bottlenecks with measurements
3. Proposed fixes with expected improvements

### Week 2 (Implementation Phase)
1. Pull requests with optimizations
2. Before/after performance metrics
3. Documentation of changes made
4. Any trade-offs or considerations

## Submitting Changes

1. Create feature branches from `contractor-ios-performance-2025-09`
2. Name branches descriptively: `fix-tab-switching-lag`, `optimize-image-loading`, etc.
3. Submit pull requests with:
   - Clear description of the problem
   - Solution implemented
   - Performance measurements (before/after)
   - Screenshots from Instruments

## Communication

- Daily updates via Upwork messages
- Include specific metrics in updates
- Ask questions if business logic is unclear
- Don't make assumptions about intended behavior

## DO NOT

- Modify Config.swift URLs
- Attempt to access backend
- Add external dependencies without approval
- Remove existing functionality
- Add analytics or tracking
- Access any .env or database files
- Make network requests to external servers

## Testing with Mock Data

The app is configured with extensive mock data for stress testing:
- 1000+ garments in closet
- 500+ shop recommendations
- 200+ try-on sessions

This should be sufficient to identify and fix all performance issues.

## Questions?

Contact via Upwork messages. Response time: within 4 hours during business hours.
EOF

echo "🎯 Creating performance baseline document..."

cat > PERFORMANCE_BASELINE.md << 'EOF'
# V10 iOS App - Performance Baseline

> Measured on: iPhone 15 Pro Simulator, macOS Sonoma, Xcode 15
> Date: September 2025

## Current Performance Issues

### 1. Tab Switching Lag
**Current**: 380-520ms
**Target**: <200ms

Measurements:
- Shop → Closet: 450ms
- Closet → Scan: 380ms  
- Any → Fit Feedback: 520ms
- Scan → Shop: 410ms

### 2. Scrolling Performance
**Current**: 18-22 FPS
**Target**: 55-60 FPS

Measurements:
- Shop grid (200 items): 18 FPS during fast scroll
- Closet list (500 items): 22 FPS during fast scroll
- Try-on history: 20 FPS

### 3. Button Response Time
**Current**: 300-400ms
**Target**: <100ms

Measurements:
- "Add to Closet" button: 350ms
- Filter toggles: 300ms
- Navigation buttons: 400ms

### 4. Memory Usage
**Current**: Grows 200MB+ per session
**Target**: <50MB growth

Measurements:
- App launch: 125 MB
- After 5 min usage: 340 MB
- After 10 min: 450 MB+

### 5. Image Loading
**Current**: Visible loading delays
**Target**: Instant or progressive

Issues:
- No caching implementation
- Full-size images in thumbnails
- Sequential loading

## How to Measure

### Using Instruments

1. **Time Profiler**:
   - Look for main thread blocks >16ms
   - Identify functions >100ms
   - Find repeated expensive operations

2. **Core Animation**:
   - Monitor FPS during scrolling
   - Check for off-screen rendering
   - Identify compositing issues

3. **SwiftUI**:
   - Track body evaluations
   - Find unnecessary updates
   - Check dependency chains

4. **Allocations**:
   - Monitor memory growth
   - Find retain cycles
   - Check image memory

### Manual Testing

1. Use screen recording to capture lag
2. Count frames in recordings
3. Use stopwatch for operations
4. Monitor memory in Xcode debug gauge

## Success Criteria

- [ ] All tab switches <200ms
- [ ] Scrolling maintains 55+ FPS
- [ ] Buttons respond <100ms
- [ ] Memory growth <50MB per session
- [ ] No visible image loading delays
EOF

echo "✅ Contractor branch prepared successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Review the changes:"
echo "   git status"
echo ""
echo "2. Commit the sanitized version:"
echo "   git add -A"
echo "   git commit -m 'Sanitize codebase for contractor access'"
echo ""
echo "3. Push to remote:"
echo "   git push origin contractor-ios-performance-2025-09"
echo ""
echo "4. Share with contractor:"
echo "   - Repository URL"
echo "   - Branch: contractor-ios-performance-2025-09"
echo "   - Tell them to fork and work from their fork"
echo ""
echo "5. After project completion:"
echo "   - Review and merge approved changes back to revert-to-a42786"
echo "   - Delete contractor branch"
echo "   - Revoke access immediately"
echo ""
echo "⚠️  IMPORTANT: Review 'git status' before committing to ensure"
echo "    no sensitive files are included!"

# Return to original branch
echo ""
echo "Switching back to revert-to-a42786..."
git checkout revert-to-a42786
echo "✅ You're back on branch: revert-to-a42786"
