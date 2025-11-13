import Foundation
import Combine
import SwiftUI

// MARK: - Response Cache
final class ResponseCache {
    static let shared = ResponseCache()
    
    private var cache = [String: (data: Data, timestamp: Date)]()
    private let cacheQueue = DispatchQueue(label: "com.v10.responsecache", attributes: .concurrent)
    private let maxCacheAge: TimeInterval = 300 // 5 minutes
    
    private init() {
        // Clean cache periodically
        Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { _ in
            self.cleanExpiredCache()
        }
    }
    
    func get(for key: String) -> Data? {
        cacheQueue.sync {
            guard let cached = cache[key] else { return nil }
            
            if Date().timeIntervalSince(cached.timestamp) > maxCacheAge {
                cache.removeValue(forKey: key)
                return nil
            }
            
            return cached.data
        }
    }
    
    func set(_ data: Data, for key: String) {
        cacheQueue.async(flags: .barrier) {
            self.cache[key] = (data, Date())
        }
    }
    
    private func cleanExpiredCache() {
        cacheQueue.async(flags: .barrier) {
            let now = Date()
            self.cache = self.cache.filter { _, value in
                now.timeIntervalSince(value.timestamp) <= self.maxCacheAge
            }
        }
    }
}

// MARK: - Optimized Network Manager
@MainActor
final class OptimizedNetworkManager: ObservableObject {
    static let shared = OptimizedNetworkManager()
    
    private let session: URLSession
    private let decoder = JSONDecoder()
    private let processingQueue = DispatchQueue(label: "com.v10.network.processing", qos: .userInitiated)
    
    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        config.waitsForConnectivity = true
        config.urlCache = URLCache(
            memoryCapacity: 20 * 1024 * 1024,  // 20 MB memory cache
            diskCapacity: 100 * 1024 * 1024,    // 100 MB disk cache
            diskPath: "com.v10.urlcache"
        )
        config.requestCachePolicy = .returnCacheDataElseLoad
        
        self.session = URLSession(configuration: config)
    }
    
    // Async function for modern Swift concurrency
    func fetch<T: Decodable>(
        _ type: T.Type,
        from url: URL,
        method: String = "GET",
        body: Data? = nil,
        useCache: Bool = true
    ) async throws -> T {
        let cacheKey = "\(method):\(url.absoluteString):\(body?.base64EncodedString() ?? "")"
        
        // Check cache first if enabled
        if useCache, method == "GET", let cachedData = ResponseCache.shared.get(for: cacheKey) {
            return try await decodeOnBackground(cachedData, as: type)
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.httpBody = body
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }
        
        // Cache successful GET responses
        if useCache && method == "GET" {
            ResponseCache.shared.set(data, for: cacheKey)
        }
        
        return try await decodeOnBackground(data, as: type)
    }
    
    // Decode on background thread to avoid blocking UI
    private func decodeOnBackground<T: Decodable>(_ data: Data, as type: T.Type) async throws -> T {
        return try await withCheckedThrowingContinuation { continuation in
            processingQueue.async {
                do {
                    let decoded = try self.decoder.decode(type, from: data)
                    continuation.resume(returning: decoded)
                } catch {
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    // Batch fetch for multiple URLs
    func batchFetch<T: Decodable>(
        _ type: T.Type,
        from urls: [URL]
    ) async -> [Result<T, Error>] {
        return await withTaskGroup(of: Result<T, Error>.self) { group in
            for url in urls {
                group.addTask {
                    do {
                        let result = try await self.fetch(type, from: url)
                        return .success(result)
                    } catch {
                        return .failure(error)
                    }
                }
            }
            
            var results: [Result<T, Error>] = []
            for await result in group {
                results.append(result)
            }
            return results
        }
    }
}

// MARK: - Debounced Text Field Modifier
struct DebouncedModifier: ViewModifier {
    @Binding var text: String
    let delay: TimeInterval
    let onTextChange: (String) -> Void
    
    @State private var task: DispatchWorkItem?
    
    func body(content: Content) -> some View {
        content
            .onChange(of: text) { _, newValue in
                task?.cancel()
                
                let newTask = DispatchWorkItem {
                    onTextChange(newValue)
                }
                
                task = newTask
                DispatchQueue.main.asyncAfter(deadline: .now() + delay, execute: newTask)
            }
    }
}

extension View {
    func debounced(
        text: Binding<String>,
        delay: TimeInterval = 0.5,
        onTextChange: @escaping (String) -> Void
    ) -> some View {
        modifier(DebouncedModifier(text: text, delay: delay, onTextChange: onTextChange))
    }
}
