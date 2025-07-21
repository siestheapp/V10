import Foundation

struct AppConfig {    // Changed from Config to AppConfig
    // Base URL for API endpoints
    static let baseURL: String = "http://127.0.0.1:8006"  // Restored to working URL
    
    // Uniqlo URL template for product pages
    static let uniqloURLTemplate: String = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // User configuration
    static let defaultUserId: String = "2"  // Restored to working user ID
    static let defaultUserName: String = "testuser@example.com"
} 