import Foundation

struct Config {
    static let baseURL = "http://127.0.0.1:8006"  // Using tailor2 database
    
    static let uniqloURLTemplate = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // Add default user configuration
    static let defaultUserId = "1"
    static let defaultUserName = "testuser@example.com"
} 