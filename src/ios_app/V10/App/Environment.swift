enum AppEnvironment {
    #if DEBUG
    static let apiBaseURL = "http://192.168.18.32:8006"  // Local development server with IP for iOS simulator
    #else
    static let apiBaseURL = "https://your-production-server.com"  // For later
    #endif
} 