# V10 iOS App - Contractor Setup Guide

## Quick Start (iOS-Only Debugging)

### Prerequisites
- Xcode 15.0 or later
- Mac with macOS Sonoma or later
- Git

### Setup Steps

1. **Clone the repository**
```bash
git clone [repository-url]
cd V10
```

2. **Open the iOS project**
```bash
cd src/ios_app
open V10.xcodeproj
```

3. **Enable Mock Mode**
In Xcode, open `V10/App/Config.swift` and change:
```swift
// Change this line:
static let baseURL = "http://127.0.0.1:8006"
// To this:
static let baseURL = "mock://localhost"  // Triggers mock mode
```

4. **Build and Run**
- Select iPhone 15 Pro simulator (or any recent model)
- Press Cmd+R to build and run
- The app will use mock data for all API calls

## Performance Testing Data

The mock data provider includes:
- **500+ garments** for testing scrolling performance in closet view
- **200+ shop recommendations** with images for testing lazy loading
- **Simulated network delays** (0.5s default) to test loading states
- **Large image URLs** from placeholder services

## Key Areas to Test for Lag

### 1. Main Performance Bottlenecks
- **ScanTab.swift** - Barcode scanning and product lookup
- **ShopView.swift** - Product grid with images
- **FitFeedbackView.swift** - Complex form with multiple inputs
- **TryOnHistoryView.swift** - List with potentially hundreds of items
- **GarmentDetailView.swift** - Image carousel and measurements

### 2. Common SwiftUI Performance Issues to Check

**View Recomposition:**
```swift
// Check for unnecessary @State updates
// Look for views that rebuild too often
```

**Image Loading:**
```swift
// Current implementation may not cache properly
// Check AsyncImage usage in ShopView
```

**List Performance:**
```swift
// Check for missing .id() modifiers
// Look for complex views in ForEach loops
```

## Running Performance Profiling

### ✅ YES - Instruments Works Perfectly with Mock Data!

**Why it works:** Instruments profiles the iOS app's performance, not the data source. Whether using real API data or mock data, the UI rendering, memory usage, and CPU utilization are measured exactly the same way.

### Using Instruments

1. **In Xcode:** Product → Profile (Cmd+I)
2. **The app will rebuild and launch with Instruments**
3. **Select Template:** 
   - **Time Profiler** - For CPU usage (START HERE)
   - **SwiftUI** - For view update tracking
   - **Core Animation** - For UI rendering issues
   - **Allocations** - For memory leaks

**The mock data is specifically designed with 500+ items to stress test and expose performance issues in Instruments!**

### What to Look For

#### Time Profiler
- Main thread blocking > 16ms (causes frame drops)
- Functions taking > 100ms
- Repeated expensive operations

#### SwiftUI Instrument
- Views updating more than once per user action
- Body evaluations in idle state
- Unnecessary dependency tracking

#### Memory Issues
- Growing memory during navigation
- Images not being released
- Retained view models

## Testing Scenarios

### Scenario 1: Heavy Scrolling Test
1. Navigate to Shop tab
2. Scroll rapidly up and down
3. Monitor for:
   - Frame drops
   - Image loading delays
   - Memory growth

### Scenario 2: Navigation Stress Test
1. Rapidly switch between tabs
2. Enter and exit detail views quickly
3. Check for:
   - Transition lag
   - Memory leaks
   - Zombie views

### Scenario 3: Data Entry Performance
1. Go to Fit Feedback view
2. Rapidly toggle switches and sliders
3. Monitor:
   - UI responsiveness
   - State update delays

## Mock Data Customization

To test specific performance scenarios, modify `MockDataProvider.swift`:

```swift
// Increase data volume for stress testing
func getMockGarments() -> [[String: Any]] {
    // Change 500 to 2000 for extreme testing
    for i in 1...2000 {
        // ...
    }
}

// Add artificial delays to simulate slow network
func simulateAPICall<T>(...) async throws -> T {
    // Change delay to test different network conditions
    let actualDelay = 2.0  // Simulate very slow network
}
```

## Deliverables Checklist

- [ ] Performance audit using Instruments
- [ ] List of specific files/functions causing lag
- [ ] Before/after performance metrics
- [ ] Recommended fixes with code examples
- [ ] Memory leak identification and fixes
- [ ] Updated code with optimizations

## Code Changes Guidelines

1. **Never modify:**
   - Database credentials
   - API keys
   - Production URLs

2. **Focus on:**
   - View optimizations
   - Caching implementations
   - Async operation improvements
   - Memory management

3. **Document all changes:**
   - Add comments explaining optimizations
   - Note performance improvements achieved
   - List any tradeoffs made

## Communication

- Daily progress updates with specific metrics
- Screenshots of Instruments showing issues
- Clear documentation of each optimization
- Questions about business logic before making assumptions

## Security Notice

This is a mock environment. You do not have access to:
- Real user data
- Production database
- Backend business logic
- Actual API endpoints

All testing should be done with the provided mock data only.
