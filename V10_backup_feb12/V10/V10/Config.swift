import Foundation

struct Config {
    static let baseURL: String = {
        #if DEBUG
        return "http://127.0.0.1:8001"
        #else
        return "https://your-production-server.com"
        #endif
    }()
    
    static let uniqloURLTemplate = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // Add default user configuration
    static let defaultUserId = "18"
    static let defaultUserName = "user1"
} 