# Updated Contractor Message (Using Render Backend)

## Send This to the Contractor:

```
Hi [Name],

The app has performance issues we need fixed:
- Tab switching: 450ms → need <200ms
- Scrolling: 20 FPS → need 55+ FPS
- Button taps: 350ms → need <100ms

## Setup Instructions:

1. Fork the repository (I'll add you with read access)
2. Work from branch: contractor-performance-simple
3. Open src/ios_app/V10.xcodeproj in Xcode

4. **IMPORTANT: Update Config.swift to use our test server:**
   Change line 7 from:
   static let baseURL = "http://127.0.0.1:8006"
   
   To:
   static let baseURL = "https://v10-2as4.onrender.com"

5. Build and run on iPhone 15 Pro simulator
6. The app will connect to our live test backend (no local setup needed!)

The backend has test data for user1@example.com with intentionally nonsensical 
feedback (3XL marked "too small", S marked "too big" - it's all fake test data).

Focus on iOS UI performance only. The backend response times are fine.

Use Instruments (Cmd+I) to profile and identify the bottlenecks.

Submit PRs with your fixes and performance measurements.
```

## Or Even Simpler - Create a Contractor Config:

```swift
// Config_Contractor.swift - Give them this file
import Foundation

struct Config {
    // Contractor version - points to live test backend
    static let baseURL = "https://v10-2as4.onrender.com"
    
    static let uniqloURLTemplate = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    static let defaultUserId = "1"
    static let defaultUserName = "user1@example.com"
}
```

Tell them: "Replace Config.swift with Config_Contractor.swift"
