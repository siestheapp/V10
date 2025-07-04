import Foundation

enum NetworkLogger {
    static func log(url: URL, method: String = "GET", body: [String: Any]? = nil) {
        print("🌐 Network Request:")
        print("URL: \(url.absoluteString)")
        print("Method: \(method)")
        if let body = body {
            print("Body: \(body)")
        }
        print("-------------------")
    }
    
    static func logError(_ error: Error, url: URL) {
        print("❌ Network Error:")
        print("URL: \(url.absoluteString)")
        print("Error: \(error.localizedDescription)")
        print("-------------------")
    }
    
    static func logSuccess(_ data: Data?, url: URL) {
        print("✅ Network Success:")
        print("URL: \(url.absoluteString)")
        if let data = data,
           let json = try? JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
            print("Response: \(json)")
        }
        print("-------------------")
    }
} 