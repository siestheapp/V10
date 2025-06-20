import Foundation

struct AppConfig {    // Changed from Config to AppConfig
    // Base URL for API endpoints
    static let baseURL: String = "http://localhost:8006"
    
    // Uniqlo URL template for product pages
    static let uniqloURLTemplate: String = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // User configuration
    static let defaultUserId: String = "18"  // Changed from "1" to "18"
    static let defaultUserName: String = "testuser@example.com"
} 