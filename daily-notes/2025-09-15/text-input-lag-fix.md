# Text Input Lag Fix - V10 iOS App

## Issue
The user was experiencing lag when clicking into the text input field on the Scan tab's "Try On" feature. The console showed errors:
- `RTIInputSystemClient` session ID errors
- PPT (Performance Tools) communication errors

## Root Cause
The app was using the unoptimized `ScanTab` view which had performance issues with the text field, particularly around:
1. Missing focus state management
2. Heavy operations possibly triggered on text field interaction
3. Missing keyboard optimizations

## Solution
Switched from `ScanTab` to `OptimizedScanTab` in `SiesApp.swift` which includes:
- **@FocusState** for proper text field focus management
- **Lazy loading** of fit zones data (only loads when actually needed)
- **Text field optimizations**:
  - `.focused($isTextFieldFocused)` for focus tracking
  - `.autocorrectionDisabled()` to prevent autocorrect lag
  - `.textInputAutocapitalization(.never)` for URL input
  - `.keyboardType(.URL)` for appropriate keyboard
  - `.id(textFieldId)` as a simulator workaround
- **Removed onTapGesture** that was loading data and causing main thread blocking

## Files Modified
- `src/ios_app/V10/App/SiesApp.swift` - Changed line 32 from `ScanTab()` to `OptimizedScanTab()`

## Testing
The app builds successfully with the changes. The OptimizedScanTab includes all the performance fixes specifically designed to eliminate text input lag.

## Note
There are actually three versions of the scan tab in the codebase:
1. `ScanTab` - Original with performance issues
2. `OptimizedScanTab` - Fixed version with lazy loading and focus management
3. `UltraOptimizedScanTab` - Experimental version that removes NavigationStack entirely

We're using `OptimizedScanTab` as it maintains full functionality while fixing the performance issues.
