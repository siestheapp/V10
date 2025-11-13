import SwiftUI

struct AllFindsView: View {
    @State private var scanHistory: [ScanHistoryItem] = []
    @State private var tryOnHistory: [TryOnHistoryItem] = []
    @State private var isLoading = false  // Start as false, will be set to true when loading
    @State private var hasLoadedInitialData = false
    @State private var errorMessage: String?
    @State private var selectedTryOn: TryOnHistoryItem?
    
    init() {
        print("🎯 AllFindsView INIT - View created")
    }
    
    var body: some View {
        let _ = print("📊 AllFindsView body - isLoading: \(isLoading), scans: \(scanHistory.count), tryOns: \(tryOnHistory.count)")
        
        Group {
            if isLoading {
                loadingView
            } else if let error = errorMessage {
                errorView(error)
            } else if scanHistory.isEmpty && tryOnHistory.isEmpty {
                emptyStateView
            } else {
                allFindsList
            }
        }
        .onAppear {
            // Load data when view appears (lazy loading)
            if !hasLoadedInitialData {
                print("🚀 AllFindsView appeared for first time, loading data...")
                hasLoadedInitialData = true
                loadAllFinds()
            } else {
                print("📊 AllFindsView re-appeared, data already loaded")
            }
        }
        .refreshable {
            // Pull to refresh
            loadAllFinds()
        }
        .sheet(item: $selectedTryOn) { tryOn in
            TryOnDetailView(tryOn: tryOn)
        }
    }
    
    private var loadingView: some View {
        ProgressView("Loading all finds...")
            .onAppear {
                print("🎯 ALL FINDS: Loading scan history and try-ons...")
            }
    }
    
    private func errorView(_ error: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.largeTitle)
                .foregroundColor(.orange)
            Text("Could not load finds")
                .font(.headline)
            Text(error)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            Button("Try Again") {
                loadAllFinds()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
    
    private var emptyStateView: some View {
        VStack(spacing: 24) {
            ZStack {
                Circle()
                    .fill(LinearGradient(colors: [.blue.opacity(0.1), .blue.opacity(0.05)], startPoint: .topLeading, endPoint: .bottomTrailing))
                    .frame(width: 120, height: 120)
                
                Image(systemName: "magnifyingglass")
                    .font(.system(size: 40))
                    .foregroundColor(.blue)
            }
            
            VStack(spacing: 12) {
                Text("No Finds Yet")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text("Scan garment tags or paste product links to start building your personalized fit collection!")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 20)
            }
            
            VStack(spacing: 12) {
                HStack(spacing: 8) {
                    Image(systemName: "camera.fill")
                        .foregroundColor(.blue)
                    Text("Scan tags for instant analysis")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                
                HStack(spacing: 8) {
                    Image(systemName: "link")
                        .foregroundColor(.blue)
                    Text("Paste links for size recommendations")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(40)
    }
    
    private var allFindsList: some View {
        List {
            // Try-On Items Section (if any)
            if !tryOnHistory.isEmpty {
                Section("Recent Try-Ons") {
                    ForEach(tryOnHistory.prefix(3)) { tryOn in
                        TryOnHistoryRow(tryOn: tryOn)
                            .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
                            .contentShape(Rectangle())
                            .onTapGesture {
                                selectedTryOn = tryOn
                                print("🎯 ALL FINDS: Tapped try-on - \(tryOn.brand) \(tryOn.productName)")
                            }
                    }
                    
                    // Show "View All" if there are more than 3 try-ons
                    if tryOnHistory.count > 3 {
                        HStack {
                            Text("View All \(tryOnHistory.count) Try-Ons")
                                .font(.subheadline)
                                .foregroundColor(.blue)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .font(.caption)
                                .foregroundColor(.blue)
                        }
                        .padding(.vertical, 8)
                        .contentShape(Rectangle())
                        .onTapGesture {
                            // This will switch to the Try-Ons tab
                            print("🎯 ALL FINDS: Switching to Try-Ons tab to view all")
                        }
                    }
                }
            }
            
            // Scanned Items Section
            if !scanHistory.isEmpty {
                Section(tryOnHistory.isEmpty ? "All Finds" : "Scanned Items") {
                    ForEach(scanHistory) { item in
                        ScanHistoryRow(item: item)
                            .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
                    }
                }
            }
        }
        .listStyle(PlainListStyle())
    }
    
    private func loadAllFinds() {
        // Prevent duplicate loads
        guard !isLoading else {
            print("🔄 Already loading finds, skipping...")
            return
        }
        
        isLoading = true
        errorMessage = nil
        print("🎯 Starting to load all finds...")
        
        Task {
            // Load both in parallel using async/await
            async let scanTask = loadScanHistoryAsync()
            async let tryOnTask = loadTryOnHistoryAsync()
            
            do {
                let (scans, tryOns) = try await (scanTask, tryOnTask)
                
                // Update UI on main thread
                await MainActor.run {
                    self.scanHistory = scans
                    self.tryOnHistory = tryOns
                    self.isLoading = false
                    print("✅ ALL FINDS: Loaded \(scans.count) scans, \(tryOns.count) try-ons")
                    
                    if scans.isEmpty && tryOns.isEmpty {
                        print("ℹ️ No finds data to display (both lists empty)")
                    }
                }
            } catch {
                await MainActor.run {
                    print("❌ Error loading finds: \(error)")
                    self.errorMessage = error.localizedDescription
                    self.isLoading = false
                }
            }
        }
    }
    
    private func loadScanHistoryAsync() async throws -> [ScanHistoryItem] {
        guard let url = URL(string: "\(Config.baseURL)/scan_history?user_id=\(Config.defaultUserId)") else {
            throw URLError(.badURL)
        }
        
        print("🔗 Fetching scan history from: \(url)")
        let (data, _) = try await URLSession.shared.data(from: url)
        
        print("📦 Received \(data.count) bytes for scan history")
        
        // Try to decode
        do {
            let items = try JSONDecoder().decode([ScanHistoryItem].self, from: data)
            print("✅ Decoded \(items.count) scan items")
            return items
        } catch {
            // If it's an empty array, that's ok
            if data.count < 10 {
                return []
            }
            throw error
        }
    }
    
    private func loadTryOnHistoryAsync() async throws -> [TryOnHistoryItem] {
        guard let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/tryons") else {
            throw URLError(.badURL)
        }
        
        print("🔗 Fetching try-on history from: \(url)")
        let (data, _) = try await URLSession.shared.data(from: url)
        
        print("📦 Received \(data.count) bytes for try-ons")
        
        // Try to decode
        do {
            let items = try JSONDecoder().decode([TryOnHistoryItem].self, from: data)
            print("✅ Decoded \(items.count) try-on items")
            return items
        } catch {
            // If it's an empty array, that's ok
            if data.count < 10 {
                return []
            }
            throw error
        }
    }
}

// Simple row view for scan history items in the unified list
struct ScanHistoryRow: View {
    let item: ScanHistoryItem
    
    var body: some View {
        HStack(spacing: 12) {
            // Product Image
            AsyncImage(url: URL(string: item.imageUrl)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
                    .overlay(
                        Image(systemName: "tag")
                            .foregroundColor(.gray)
                    )
            }
            .frame(width: 60, height: 60)
            .clipShape(RoundedRectangle(cornerRadius: 8))
            
            // Product Info
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(item.brand)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .textCase(.uppercase)
                    Spacer()
                    Text(item.formattedDate)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                
                Text(item.name)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .lineLimit(2)
                
                HStack {
                    if let size = item.scannedSize {
                        Text("Size \(size)")
                            .font(.caption)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 2)
                            .background(Color.green.opacity(0.1))
                            .foregroundColor(.green)
                            .clipShape(Capsule())
                    }
                    
                    Spacer()
                    
                    // Scanned badge
                    HStack(spacing: 4) {
                        Image(systemName: "tag.fill")
                            .font(.caption2)
                        Text("Scanned")
                            .font(.caption)
                            .fontWeight(.medium)
                    }
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(Color.blue.opacity(0.1))
                    .foregroundColor(.blue)
                    .clipShape(Capsule())
                }
            }
            
            Spacer()
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    AllFindsView()
}
