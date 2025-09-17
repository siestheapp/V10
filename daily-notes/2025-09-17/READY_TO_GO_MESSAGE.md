# Message to Send to Dilawer RIGHT NOW

```
Hi Dilawer,

Great to have you on board! Everything is ready for you to start.

## Repository & Backend Access

GitHub: https://github.com/siestheapp/V10
Branch: contractor-performance-simple
Backend: Already deployed and configured in the app

Please fork the repository and work from your fork. The iOS app is already configured to connect to our test backend with fake data.

## Performance Issues to Fix

Current measurements (iPhone 15 Pro simulator):
- Tab switching: ~450ms → Target: <200ms
- List scrolling: ~20 FPS → Target: 55+ FPS
- Button response: ~350ms → Target: <100ms
- Memory usage increases over time

## Quick Start

1. Fork the repo
2. Clone your fork
3. Checkout `contractor-performance-simple` branch
4. Open `src/ios_app/V10.xcodeproj` in Xcode
5. Run on iPhone 15 Pro simulator
6. Sign in with user1@example.com (any password works)
7. Use Instruments (Cmd+I) to profile

## Key Areas to Investigate

1. SwiftUI view re-rendering
2. API call patterns (too many requests?)
3. Image loading/caching (not implemented)
4. List virtualization (LazyVStack issues?)
5. Tab view memory management

## Note on Test Data

The user1 account has weird data (3XL marked "too small", etc.) - this is just test data from random clicking. Focus on performance, not data accuracy.

Let's have a quick 15-minute call to review the issues. What time works for you today or tomorrow?

Best,
Sean
```
