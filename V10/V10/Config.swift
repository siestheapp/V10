import Foundation

struct Config {
    static let baseURL: String = {
        #if DEBUG
        return "http://localhost:8000"  // Local development server
        #else
        return "https://your-production-server.com"  // For later
        #endif
    }()
} 