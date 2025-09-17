import Foundation

struct Config {
    // CONTRACTOR VERSION - Always use Render test backend
    // No need to run backend locally!
    static let baseURL = "https://v10-2as4.onrender.com"
    
    static let uniqloURLTemplate = "https://www.uniqlo.com/us/en/products/E{product_code}-000"
    
    // Add default user configuration
    static let defaultUserId = "1"  // Updated to user_id=1 after cleanup
    static let defaultUserName = "user1@example.com"
} 