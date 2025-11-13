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
    
    // Add computed property for formatted date
    var formattedDate: String {
        guard let date = ISO8601DateFormatter().date(from: scannedAt) else {
            return scannedAt
        }
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

struct ScanHistoryView: View {
    @State private var history: [ScanHistoryItem] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView("Loading finds...")
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
                            }
                        }
                        .onTapGesture {
                            if let url = URL(string: item.productUrl) {
                                UIApplication.shared.open(url)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Finds")
            .onAppear {
                loadHistory()
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
}

#Preview {
    ScanHistoryView()
} 