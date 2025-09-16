import Foundation

struct Config {
    #if DEBUG
    // Development environment
    #if targetEnvironment(simulator)
    static let baseURL = "http://127.0.0.1:8006"  // Simulator → host Mac
    #else
    static let baseURL = "http://192.168.18.33:8006"  // Physical device → Mac LAN IP
    #endif
    #else
    // Production environment - CHANGE THIS to your deployed backend URL
    static let baseURL = "https://v10-backend.up.railway.app"  // TODO: Replace with actual URL
    #endif
    
    static let uniqloURLTemplate = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // Add default user configuration
    static let defaultUserId = "1"  // Updated to user_id=1 after cleanup
    static let defaultUserName = "user1@example.com"
} 