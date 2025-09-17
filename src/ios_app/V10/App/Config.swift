import Foundation

struct Config {
    // Temporarily using Render for performance baseline testing
    static let baseURL = "https://v10-2as4.onrender.com"
    
    // Original config commented out:
    // #if DEBUG
    // #if targetEnvironment(simulator)
    // static let baseURL = "http://127.0.0.1:8006"
    // #else
    // static let baseURL = "http://192.168.18.33:8006"
    // #endif
    // #else
    // static let baseURL = "https://v10-2as4.onrender.com"
    // #endif
    
    static let uniqloURLTemplate = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // Add default user configuration
    static let defaultUserId = "1"  // Updated to user_id=1 after cleanup
    static let defaultUserName = "user1@example.com"
} 