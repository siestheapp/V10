import Foundation

// CONTRACTOR VERSION - Safe configuration for performance testing
// This file should replace Config.swift in the contractor branch

struct Config {
    // CONTRACTOR MODE - Mock data only, no real backend access
    #if DEBUG
    static let baseURL = "mock://contractor-performance-testing"
    #else 
    static let baseURL = "mock://contractor-performance-testing"
    #endif
    
    // Performance testing flags
    static let contractorMode = true
    static let performanceTestingEnabled = true
    static let usesMockDataOnly = true
    
    // Mock data configuration for stress testing
    struct MockData {
        // Data volumes - set high for performance testing
        static let numberOfMockGarments = 1000      // Stress test closet
        static let numberOfShopItems = 500          // Stress test shop grid
        static let numberOfTryOnSessions = 200      // Stress test history
        static let numberOfBrands = 50              // Test brand filtering
        
        // Performance testing settings
        static let simulatedNetworkDelay = 0.0      // No delay for UI testing
        static let useHighResImages = true          // Test image performance
        static let imagePlaceholderURL = "https://picsum.photos/400/600"
        
        // Memory testing
        static let preloadAllData = false           // Don't preload to test lazy loading
        static let cacheImages = true               // Should be true for good UX
        static let maxImageCacheSize = 100_000_000  // 100MB cache limit
    }
    
    // User configuration (mock only)
    static let defaultUserId = "mock-contractor-user"
    static let defaultUserName = "performance@test.com"
    
    // Features configuration
    struct Features {
        static let barcodeScanning = true           // Test camera performance
        static let photoCapture = true              // Test photo handling
        static let fitFeedback = true               // Test form performance
        static let recommendations = true           // Test recommendation engine
        
        // Disabled in contractor mode
        static let realAPIcalls = false
        static let databaseAccess = false
        static let productScraping = false
        static let analyticsTracking = false
    }
    
    // Performance targets (for contractor reference)
    struct PerformanceTargets {
        static let maxTabSwitchTime: TimeInterval = 0.2      // 200ms
        static let minScrollFPS = 55                         // 55+ FPS
        static let maxButtonResponseTime: TimeInterval = 0.1 // 100ms
        static let maxMemoryGrowth = 50_000_000             // 50MB per session
        static let maxInitialLoadTime: TimeInterval = 2.0    // 2 seconds
    }
    
    // URLs (all disabled in contractor mode)
    static let uniqloURLTemplate = "disabled://no-access"
    static let jcrewURLTemplate = "disabled://no-access"
    static let productionAPIURL = "disabled://no-access"
    
    // Security check
    static var isContractorMode: Bool {
        return contractorMode && baseURL.starts(with: "mock://")
    }
    
    // Validate configuration on init
    static func validate() {
        #if DEBUG
        print("⚠️ CONTRACTOR MODE ACTIVE")
        print("- Using mock data only")
        print("- No backend access")
        print("- Performance testing enabled")
        print("- Mock garments: \(MockData.numberOfMockGarments)")
        print("- Mock shop items: \(MockData.numberOfShopItems)")
        #endif
        
        assert(isContractorMode, "Contractor mode must use mock:// URLs only")
        assert(!Features.realAPIcalls, "Real API calls must be disabled")
        assert(!Features.databaseAccess, "Database access must be disabled")
    }
}
