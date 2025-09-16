import Foundation

// Configuration for contractor/debugging without backend
struct MockConfig {
    // Switch between real and mock mode
    static let useMockData = true  // Set to true for contractor
    
    // Mock API endpoint (can be a simple JSON server or mock responses)
    static let mockBaseURL = "https://api.mockapi.io/v1/your-mock-endpoint"
    
    // Or use local JSON files
    static let useLocalJSON = true
}

// Extension to handle mock responses
extension URLSession {
    static var mockSession: URLSession {
        let config = URLSessionConfiguration.ephemeral
        // Add mock protocol handler here if needed
        return URLSession(configuration: config)
    }
}

