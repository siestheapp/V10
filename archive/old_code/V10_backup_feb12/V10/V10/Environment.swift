enum Environment {
    #if DEBUG
    static let apiBaseURL = "http://localhost:8000"  // Local development server
    #else
    static let apiBaseURL = "https://your-production-server.com"  // For later
    #endif
} 