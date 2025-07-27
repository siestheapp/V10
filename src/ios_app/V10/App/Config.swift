import Foundation

struct Config {
    static let baseURL = "http://127.0.0.1:8006"  // Restored to working URL
    
    static let uniqloURLTemplate = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // Add default user configuration
    static let defaultUserId = "1"  // Updated to user_id=1 after cleanup
    static let defaultUserName = "user1@example.com"
} 