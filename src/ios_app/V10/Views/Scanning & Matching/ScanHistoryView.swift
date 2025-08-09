import SwiftUI

struct ScanHistoryItem: Codable, Identifiable {
    let id: Int
    let productCode: String
    let scannedSize: String?
    let scannedPrice: Double?
    let scannedAt: String  // Change from Date to String for now
    let name: String
    let category: String
    let imageUrl: String
    let productUrl: String
    let brand: String
    
    // Add computed property for formatted date in EST
    var formattedDate: String {
        guard let date = ISO8601DateFormatter().date(from: scannedAt) else {
            return scannedAt
        }
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        formatter.timeZone = TimeZone(identifier: "America/New_York") // EST/EDT
        return formatter.string(from: date)
    }
}

struct ScanHistoryView: View {
    @State private var history: [ScanHistoryItem] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var selectedItem: ScanHistoryItem?
    @State private var sizeRecommendation: SizeRecommendationResponse?
    @State private var isAnalyzing = false
    @State private var userFitZones: ComprehensiveMeasurementData?
    
    var body: some View {
        NavigationStack {
            Group {
                    if isLoading {
                    ProgressView("Loading finds...")
                        .onAppear {
                            print("🔍 FINDS TAB: ScanHistoryView is loading...")
                        }
                } else if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                } else if history.isEmpty {
                    Text("No finds yet! Scan a tag to get started.")
                        .foregroundColor(.gray)
                } else {
                    List(history) { item in
                        HStack(spacing: 15) {
                            AsyncImage(url: URL(string: item.imageUrl)) { image in
                                image.resizable()
                                    .aspectRatio(contentMode: .fit)
                            } placeholder: {
                                Color.gray.opacity(0.3)
                            }
                            .frame(width: 60, height: 60)
                            
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.name)
                                    .font(.headline)
                                Text(item.brand)
                                    .font(.subheadline)
                                    .foregroundColor(.gray)
                                if let size = item.scannedSize {
                                    Text("Size: \(size)")
                                        .font(.caption)
                                }
                                Text(item.formattedDate)  // Add this
                                    .font(.caption2)
                                    .foregroundColor(.gray)
                                
                                // Subtle indicator that this is clickable
                                if !item.productUrl.isEmpty {
                                    HStack {
                                        Image(systemName: "magnifyingglass.circle")
                                            .font(.caption2)
                                            .foregroundColor(.blue)
                                        Text("Tap to see size recommendation")
                                            .font(.caption2)
                                            .foregroundColor(.blue)
                                    }
                                }
                            }
                        }
                        .onTapGesture {
                            print("🔍 FINDS: Clicked on \(item.brand) - \(item.name)")
                            selectedItem = item
                            fetchSizeRecommendation(for: item)
                        }
                        .overlay(
                            Group {
                                if isAnalyzing && selectedItem?.id == item.id {
                                    HStack {
                                        ProgressView()
                                            .scaleEffect(0.8)
                                        Text("Loading recommendation...")
                                            .font(.caption)
                                            .foregroundColor(.secondary)
                                    }
                                    .padding(8)
                                    .background(Color(.systemBackground).opacity(0.9))
                                    .cornerRadius(8)
                                }
                            }
                        )
                    }
                }
            }
            .navigationTitle("Finds")
                    .onAppear {
            print("📱 FINDS TAB: ScanHistoryView appeared - starting to load history")
            // Only load history if we don't have any data yet
            if history.isEmpty {
                loadHistory()
            }
            // Only load fit zones if we don't have them yet
            if userFitZones == nil {
                loadUserFitZones()
            }
        }
            .navigationDestination(isPresented: Binding(
                get: { sizeRecommendation != nil },
                set: { if !$0 { sizeRecommendation = nil; selectedItem = nil } }
            )) {
                if let recommendation = sizeRecommendation {
                    SizeRecommendationScreen(recommendation: recommendation, userFitZones: userFitZones)
                }
            }
        }
    }
    
    private func loadHistory() {
        guard let url = URL(string: "\(Config.baseURL)/scan_history?user_id=\(Config.defaultUserId)") else {
            errorMessage = "Invalid URL"
            return
        }
        
        print("Loading history from: \(url)")  // Debug print
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                print("Network error: \(error)")  // Debug print
                DispatchQueue.main.async {
                    self.errorMessage = "Network error: \(error.localizedDescription)"
                }
                return
            }
            
            if let data = data {
                do {
                    let items = try JSONDecoder().decode([ScanHistoryItem].self, from: data)
                    print("Loaded \(items.count) items")  // Debug print
                    DispatchQueue.main.async {
                        self.history = items
                        self.isLoading = false
                    }
                } catch {
                    print("Decoding error: \(error)")  // Debug print
                    DispatchQueue.main.async {
                        self.errorMessage = "Could not load finds: \(error.localizedDescription)"
                    }
                }
            }
            
            DispatchQueue.main.async {
                self.isLoading = false
            }
        }.resume()
    }
    
    private func fetchSizeRecommendation(for item: ScanHistoryItem) {
        guard !item.productUrl.isEmpty else {
            print("⚠️ No product URL for item: \(item.name)")
            return
        }
        
        guard let url = URL(string: "\(Config.baseURL)/garment/size-recommendation") else {
            print("⚠️ Invalid API URL for size recommendation")
            return
        }
        
        isAnalyzing = true
        
        let requestBody = [
            "product_url": item.productUrl,
            "user_id": Config.defaultUserId
        ]
        
        guard let jsonData = try? JSONSerialization.data(withJSONObject: requestBody) else {
            print("⚠️ Failed to encode request for size recommendation")
            isAnalyzing = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        print("🔄 FINDS: Fetching size recommendation for \(item.brand) - \(item.name)")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isAnalyzing = false
                
                if let error = error {
                    print("❌ FINDS: Network error fetching recommendation: \(error.localizedDescription)")
                    return
                }
                
                guard let data = data else {
                    print("❌ FINDS: No data received for recommendation")
                    return
                }
                
                do {
                    let recommendation = try JSONDecoder().decode(SizeRecommendationResponse.self, from: data)
                    print("✅ FINDS: Successfully fetched recommendation for \(item.name)")
                    self.sizeRecommendation = recommendation
                } catch {
                    print("❌ FINDS: Failed to parse recommendation: \(error.localizedDescription)")
                }
            }
        }.resume()
    }
    
    private func loadUserFitZones() {
        guard let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/measurements") else {
            print("⚠️ Invalid URL for fit zones")
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    print("❌ FINDS: Error loading fit zones: \(error.localizedDescription)")
                    return
                }
                
                guard let data = data else {
                    print("❌ FINDS: No fit zones data received")
                    return
                }
                
                do {
                    let response = try JSONDecoder().decode(ComprehensiveMeasurementResponse.self, from: data)
                    self.userFitZones = response.tops
                    print("✅ FINDS: Loaded user fit zones")
                } catch {
                    print("❌ FINDS: Failed to parse fit zones: \(error)")
                }
            }
        }.resume()
    }
}

#Preview {
    ScanHistoryView()
} 