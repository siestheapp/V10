enum AppEnvironment {
    #if DEBUG
    static let apiBaseURL = "http://127.0.0.1:8006"  // Local development server
    #else
    static let apiBaseURL = "https://your-production-server.com"  // For later
    #endif
} 