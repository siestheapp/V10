import Foundation

struct AppConfig {    // Changed from Config to AppConfig
    // Base URL for API endpoints
    static let baseURL: String = "http://10.17.13.215:8006"  // Physical device → Mac LAN IP
    
    // Uniqlo URL template for product pages
    static let uniqloURLTemplate: String = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // User configuration
    static let defaultUserId: String = "1"  // Updated to user_id=1 after cleanup
    static let defaultUserName: String = "user1@example.com"
} 