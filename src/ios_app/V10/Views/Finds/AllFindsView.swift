import SwiftUI

struct AllFindsView: View {
    @State private var scanHistory: [ScanHistoryItem] = []
    @State private var tryOnHistory: [TryOnHistoryItem] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var selectedTryOn: TryOnHistoryItem?
    
    var body: some View {
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
        VStack(spacing: 16) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 60))
                .foregroundColor(.gray)
            Text("No Finds Yet")
                .font(.title2)
                .fontWeight(.semibold)
            Text("Scan tags or paste product links to start building your garment collection!")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
        .padding()
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
        isLoading = true
        errorMessage = nil
        
        let group = DispatchGroup()
        
        // Load scan history
        group.enter()
        loadScanHistory { result in
            switch result {
            case .success(let items):
                self.scanHistory = items
            case .failure(let error):
                print("❌ Failed to load scan history: \(error)")
            }
            group.leave()
        }
        
        // Load try-on history
        group.enter()
        loadTryOnHistory { result in
            switch result {
            case .success(let items):
                self.tryOnHistory = items
            case .failure(let error):
                print("❌ Failed to load try-on history: \(error)")
            }
            group.leave()
        }
        
        group.notify(queue: .main) {
            self.isLoading = false
            print("✅ ALL FINDS: Loaded \(self.scanHistory.count) scanned items and \(self.tryOnHistory.count) try-ons")
        }
    }
    
    private func loadScanHistory(completion: @escaping (Result<[ScanHistoryItem], Error>) -> Void) {
        guard let url = URL(string: "\(Config.baseURL)/scan_history?user_id=\(Config.defaultUserId)") else {
            completion(.failure(URLError(.badURL)))
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(URLError(.badServerResponse)))
                return
            }
            
            do {
                let items = try JSONDecoder().decode([ScanHistoryItem].self, from: data)
                completion(.success(items))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    private func loadTryOnHistory(completion: @escaping (Result<[TryOnHistoryItem], Error>) -> Void) {
        guard let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/tryons") else {
            completion(.failure(URLError(.badURL)))
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(URLError(.badServerResponse)))
                return
            }
            
            do {
                let items = try JSONDecoder().decode([TryOnHistoryItem].self, from: data)
                completion(.success(items))
            } catch {
                completion(.failure(error))
            }
        }.resume()
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
