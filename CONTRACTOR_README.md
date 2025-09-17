# V10 iOS Performance Optimization Project

## 🎯 Your Mission
Fix iOS app performance issues:
- Tab switching: Currently ~450ms → Target <200ms
- Scrolling: Currently ~20 FPS → Target 55+ FPS  
- Button taps: Currently ~350ms → Target <100ms

## 🚀 Quick Setup

### 1. iOS App
```bash
cd src/ios_app
open V10.xcodeproj
```

### 2. Backend (Optional - for testing with real API)
The iOS app can work with mock data, but if you want to test with the backend:

```bash
cd src/ios_app/Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# You'll need to set up a local PostgreSQL database
# The app uses test data for user1@example.com
python app.py
```

### 3. Update Config.swift
Point to your local backend or use mock mode:
```swift
// For local backend testing:
static let baseURL = "http://127.0.0.1:8006"

// Or use mock mode (no backend needed)
static let useMockData = true
```

## 📊 Test Data
- The app has test data for user1@example.com
- This data is intentionally inconsistent (for testing)
- 3XL marked as "too small", S marked as "too big" - this is normal
- Focus on performance, not data accuracy

## 🔍 Performance Analysis

Use Xcode Instruments (Cmd+I) to profile:
1. Time Profiler - for CPU usage
2. Core Animation - for FPS and rendering
3. System Trace - for overall performance
4. SwiftUI - for view updates

## 📁 Project Structure

```
src/ios_app/
├── V10.xcodeproj       # Xcode project
├── V10/
│   ├── App/            # App configuration
│   ├── Views/          # SwiftUI views (FOCUS HERE)
│   ├── Models/         # Data models
│   └── Services/       # API services
└── Backend/            # Python backend (optional)
```

## ⚠️ Known Performance Issues

1. **FitFeedbackView**: Complex form causing lag
2. **ShopTab**: Grid/List scrolling is choppy
3. **Tab Switching**: Slow transitions between tabs
4. **Image Loading**: No caching implemented
5. **List Rendering**: Not using lazy loading properly

## ✅ Deliverables

1. **Day 3**: Performance audit with Instruments traces
2. **Day 7**: Initial optimizations implemented
3. **Day 14**: Final fixes + documentation

## 📝 Notes

- All product/brand data is included for testing
- The backend uses a test database with fake data
- Focus on iOS UI performance, not backend optimization
- Document all changes you make

Good luck! Looking forward to seeing those performance improvements!
