# Performance Baseline Analysis - September 17, 2025

## 🔴 Critical Performance Issues Found

### Main Thread Blocking: 87.9% (12.77s out of 14.54s)
This is causing all the UI lag - the main thread is almost completely blocked.

## Top Performance Killers (from Instruments):

### 1. UITextField Creation Hell - 554ms+ ⚠️
```
554.00 ms - UITextField _initWithFrame
318.00 ms - UITextField _inputController  
187.00 ms - UIFieldEditor _textInputController
```
**Problem**: TextFields are being CREATED instead of REUSED. This is extremely expensive.
**Location**: Likely in FitFeedbackViewWithPhoto or ScanTab
**Impact**: This alone adds ~0.5s delay to view transitions

### 2. SwiftUI Layout Thrashing - 7.63s 🔥
```
7.63 s - AG::Graph::UpdateStack::update()
3.53 s - LayoutProxy.size(in:)
2.13 s - DynamicLayoutComputer.updateValue()
```
**Problem**: Views are recalculating layouts constantly
**Causes**: 
- GeometryReader in hot paths
- Missing .id() on list items
- View identity changing unnecessarily

### 3. Excessive View Rebuilds - 3.67s
```
3.67 s - specialized implicit closure in Attribute.init
```
**Problem**: Entire view hierarchies rebuilding instead of updating

## Specific Files to Investigate:

1. **src/ios_app/V10/Views/Fit Feedback/FitFeedbackViewWithPhoto.swift**
   - Has TextField that's likely recreating
   - Line 106: TextField for photo caption

2. **src/ios_app/V10/Views/Scanning & Matching/ScanTab.swift**
   - Already has "performance fix" comments (lines 188-192)
   - TextField focus issues noted
   - Delayed TextField creation workaround

3. **src/ios_app/V10/Views/UserMeasurementProfileView.swift**
   - GeometryReader usage (lines 184, 233)
   - Could be causing layout recalculation

## Quick Wins for Contractor:

### Fix 1: TextField Reuse
```swift
// BAD - Creates new TextField
if showTextField {
    TextField("", text: $text)
}

// GOOD - Reuses TextField  
TextField("", text: $text)
    .opacity(showTextField ? 1 : 0)
    .disabled(!showTextField)
```

### Fix 2: Proper List IDs
```swift
// BAD - SwiftUI recreates views
ForEach(items) { item in
    ItemView(item: item)
}

// GOOD - SwiftUI updates existing views
ForEach(items) { item in
    ItemView(item: item)
        .id(item.id)  // Stable identity
}
```

### Fix 3: Lazy Loading
```swift
// BAD - Creates all views at once
VStack {
    ForEach(items) { ... }
}

// GOOD - Creates views as needed
LazyVStack {
    ForEach(items) { ... }
}
```

### Fix 4: Cache GeometryReader Results
```swift
// BAD - Recalculates constantly
GeometryReader { geo in
    SomeView()
        .frame(width: geo.size.width * 0.8)
}

// GOOD - Calculate once
@State private var calculatedWidth: CGFloat = 0
GeometryReader { geo in
    SomeView()
        .frame(width: calculatedWidth)
        .onAppear { 
            calculatedWidth = geo.size.width * 0.8 
        }
}
```

## Measured Performance:

### Current (BAD):
- **Total Time**: 14.54s for basic navigation
- **Main Thread Blocked**: 87.9%
- **TextField Creation**: 554ms per field
- **Layout Recalculation**: 7.63s

### Target (After Fix):
- **Total Time**: <3s for same navigation
- **Main Thread Blocked**: <20%
- **TextField Creation**: 0ms (reused)
- **Layout Recalculation**: <1s

## Priority Order:
1. **Fix TextField recreation** (Quick win - 500ms+ improvement)
2. **Add proper .id() to lists** (Moderate - better scrolling)
3. **Convert to LazyVStack/LazyHStack** (Moderate - memory & speed)
4. **Optimize GeometryReader usage** (Complex - but big gains)

## Contractor Instructions:
1. Start with FitFeedbackViewWithPhoto - fix TextField
2. Check all ForEach loops for missing .id()
3. Replace VStack with LazyVStack where appropriate
4. Profile after each fix to measure improvement
5. Target: Tab switches <200ms, Scrolling 55+ FPS
