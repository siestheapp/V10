import Foundation
import SwiftUI

// Properly optimized FindsView model
@MainActor
class FindsViewModel: ObservableObject {
    @Published var scanHistory: [ScanHistoryItem] = []
    @Published var tryOnHistory: [TryOnHistoryItem] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private var hasLoaded = false
    
    // Load ONLY when tab is actually viewed, not on app startup
    func loadIfNeeded() async {
        guard !hasLoaded else { return }
        hasLoaded = true
        await loadAllFinds()
    }
    
    private func loadAllFinds() async {
        isLoading = true
        errorMessage = nil
        
        // Load both in parallel, not sequentially
        async let scans = loadScanHistory()
        async let tryOns = loadTryOnHistory()
        
        do {
            let (scanResults, tryOnResults) = try await (scans, tryOns)
            self.scanHistory = scanResults
            self.tryOnHistory = tryOnResults
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    private func loadScanHistory() async throws -> [ScanHistoryItem] {
        // Your actual API call here
        try await Task.sleep(nanoseconds: 500_000_000)
        return []
    }
    
    private func loadTryOnHistory() async throws -> [TryOnHistoryItem] {
        // Your actual API call here
        try await Task.sleep(nanoseconds: 500_000_000)
        return []
    }
}

