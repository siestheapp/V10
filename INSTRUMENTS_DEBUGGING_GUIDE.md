# Xcode Instruments Debugging Guide for V10 App

## How to Launch Instruments

1. **In Xcode with the app running:**
   - Debug menu → Profile (or press ⌘+I)
   - The app will rebuild in Release mode and launch Instruments

2. **Choose profiling template:**
   - **Time Profiler** - Start here to find slow functions
   - **SwiftUI** - For view update issues
   - **Allocations** - For memory leaks
   - **Core Animation** - For rendering problems

## What You'll See With Mock Data

### Time Profiler Results Example
When scrolling the Shop view with 200+ mock items, you'll see:
```
Call Tree:
├── Main Thread (100%)
    ├── SwiftUI.ViewRendererHost.render (45%) ⚠️ HIGH
    ├── ShopView.body.getter (22%) ⚠️ 
    ├── AsyncImage.load (18%)
    ├── ForEach<Range>.iteration (10%)
    └── Other (5%)
```

**Red Flag:** Any function > 16ms on main thread causes frame drops

### SwiftUI Instrument Findings
The mock data will expose:
```
View Updates:
- ShopView body: 500+ calls when scrolling ⚠️ Should be ~60
- GarmentRow body: 2000+ calls ⚠️ Excessive
- @StateObject created multiple times ⚠️ Memory issue
```

### Expected Performance Issues to Find

#### 1. Missing List Optimization
```swift
// BAD - Will show in Instruments as excessive redraws
ForEach(garments) { garment in
    GarmentRow(garment: garment)
}

// GOOD - Optimized
ForEach(garments, id: \.garment_id) { garment in
    GarmentRow(garment: garment)
        .id(garment.garment_id)  // Helps SwiftUI track identity
}
```

#### 2. Image Loading Issues
```swift
// BAD - Will show high memory in Allocations
AsyncImage(url: URL(string: imageURL))

// GOOD - With caching
CachedAsyncImage(url: URL(string: imageURL))
    .frame(width: 150, height: 200)
    .clipped()
```

#### 3. View Body Recalculation
```swift
// BAD - Instruments will show body called on every state change
struct ShopView: View {
    @State private var searchText = ""
    var body: some View {
        // Complex computation here
    }
}

// GOOD - Separate concerns
struct ShopView: View {
    @StateObject private var viewModel = ShopViewModel()
}
```

## Specific Areas to Profile

### 1. ScanTab (OptimizedScanTab.swift)
**Launch Instruments → Time Profiler**
- Tap the Scan tab
- Look for main thread blocking
- Expected issue: Camera preview setup

### 2. ShopView scrolling
**Launch Instruments → Core Animation**
- Navigate to Shop tab
- Scroll rapidly
- Look for:
  - Red areas (off-screen rendering)
  - Frame rate drops below 60fps
  - Memory growth during scrolling

### 3. FitFeedbackView interactions
**Launch Instruments → SwiftUI**
- Open Fit Feedback screen
- Toggle switches rapidly
- Watch for excessive view updates

### 4. Navigation transitions
**Launch Instruments → Time Profiler**
- Switch between tabs quickly
- Enter/exit detail views
- Look for animation hitches

## Interpreting Results

### CPU Usage Thresholds
- **Good:** < 40% CPU during scrolling
- **Acceptable:** 40-60% CPU
- **Bad:** > 60% CPU (will cause lag)
- **Critical:** > 80% CPU (severe lag)

### Memory Patterns
- **Good:** Stable memory during navigation
- **Bad:** Growing memory (indicates leaks)
- **Critical:** Memory warnings

### Frame Rate
- **Target:** 60 FPS (ProMotion: 120 FPS)
- **Acceptable:** > 50 FPS
- **Noticeable lag:** < 45 FPS
- **Severe:** < 30 FPS

## Recording a Trace

1. Click Record (red button)
2. Perform the laggy action in the app
3. Stop recording after 10-30 seconds
4. Save the trace file (.trace)
5. Share screenshots of bottlenecks

## Mock Data Stress Testing

The MockDataProvider includes:
- **500 garments** - Stresses list rendering
- **200 shop items** - Tests image loading
- **Simulated delays** - Reveals loading state issues

To increase stress for testing:
```swift
// In MockDataProvider.swift, change:
for i in 1...500  // to
for i in 1...2000 // For extreme testing
```

## Deliverables from Profiling

1. **Screenshots** of Instruments showing:
   - Heaviest stack trace
   - SwiftUI update counts
   - Memory allocations graph

2. **Specific functions** causing lag:
   - Function name
   - File location
   - Time percentage

3. **Recommended fixes** with:
   - Before/after code
   - Expected improvement

## Common Fixes You'll Implement

1. **Lazy loading containers**
   - Replace VStack with LazyVStack
   - Use List instead of ScrollView + ForEach

2. **Image optimization**
   - Implement proper caching
   - Reduce image resolution
   - Lazy load images

3. **View identity**
   - Add .id() modifiers
   - Use @StateObject vs @ObservedObject correctly
   - Minimize @State variables

4. **Computation optimization**
   - Move heavy logic out of body
   - Cache computed values
   - Use background queues

## Without Backend Connection

**Important:** The mock setup means:
- ✅ All UI performance issues are visible
- ✅ Rendering problems show accurately  
- ✅ Memory leaks are detectable
- ✅ SwiftUI inefficiencies are exposed
- ❌ Network latency (but mock delays simulate this)
- ❌ Backend processing time (not relevant for UI lag)

The lag issues are in the iOS rendering layer, not the backend, so this setup captures everything needed for debugging.

