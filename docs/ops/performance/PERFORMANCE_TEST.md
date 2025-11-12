# Performance Fix Test Guide

## Before & After Test

### Option A: Test with Original App
1. Keep using `SiesApp.swift` (your current main app)
2. Run Instruments (⌘+I)
3. Note the startup time (currently ~4 seconds)

### Option B: Test with Optimized App  
1. Change your main app file:
   - In Xcode, find `SiesApp.swift`
   - Remove `@main` from line 3
   - Open `OptimizedSiesApp.swift`
   - Add `@main` before `struct OptimizedSiesApp`
2. Run Instruments again
3. Startup should be <1 second!

### What Changed:
- **Before:** All 5 tabs load data on startup = 3.93s
- **After:** Only ScanTab loads = ~800ms
- **Savings:** 3+ seconds!

## Quick Switch Method

In `SiesApp.swift`, temporarily replace your TabView with:
```swift
TabView(selection: $selectedTab) {
    ScanTab()
        .tabItem { Label("Scan", systemImage: "camera") }
        .tag(0)
    
    // Comment out other tabs temporarily
    Text("Finds - Not Loaded")
        .tabItem { Label("Finds", systemImage: "list.bullet") }
        .tag(1)
    
    Text("Closet - Not Loaded")
        .tabItem { Label("Closet", systemImage: "tshirt") }
        .tag(2)
    
    Text("Fit - Not Loaded")
        .tabItem { Label("Fit", systemImage: "ruler") }
        .tag(3)
    
    Text("More - Not Loaded")
        .tabItem { Label("More", systemImage: "ellipsis") }
        .tag(4)
}
```

This proves the tabs are the problem!

