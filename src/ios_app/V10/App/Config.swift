import Foundation

struct Config {
    // Using the existing Render deployment - test data only
    static let baseURL = "https://v10-2as4.onrender.com"
    static let useMockData = false
    static let isContractorMode = true
    
    // Add default user configuration for auto-login
    static let defaultUserId = "1"  // User ID 1 with test data
    static let defaultUserName = "user1@example.com"
}