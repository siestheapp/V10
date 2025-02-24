import Foundation

struct Config {
    static let baseURL: String = {
        #if DEBUG
        return "http://localhost:8005"
        #else
        return "https://your-production-server.com"
        #endif
    }()
    
    static let uniqloURLTemplate = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // Add default user configuration
    static let defaultUserId = "1"
    static let defaultUserName = "testuser@example.com"
} 