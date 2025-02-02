import SwiftUI

struct ScanHistoryItem: Codable, Identifiable {
    let id: Int
    let productCode: String
    let scannedSize: String?
    let scannedPrice: Double?
    let scannedAt: Date
    let name: String
    let category: String
    let imageUrl: String
    let productUrl: String
}

struct ScanHistoryView: View {
    @State private var history: [ScanHistoryItem] = []
    @State private var isLoading = true
    
    var body: some View {
        NavigationView {
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
                        Text(item.category)
                            .font(.subheadline)
                            .foregroundColor(.gray)
                        if let size = item.scannedSize {
                            Text("Size: \(size)")
                                .font(.caption)
                        }
                    }
                }
                .onTapGesture {
                    if let url = URL(string: item.productUrl) {
                        UIApplication.shared.open(url)
                    }
                }
            }
            .navigationTitle("Scan History")
            .onAppear {
                loadHistory()
            }
        }
    }
    
    private func loadHistory() {
        guard let url = URL(string: "\(Config.baseURL)/scan_history") else { return }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            defer { isLoading = false }
            
            if let data = data {
                do {
                    let items = try JSONDecoder().decode([ScanHistoryItem].self, from: data)
                    DispatchQueue.main.async {
                        self.history = items
                    }
                } catch {
                    print("Decoding error: \(error)")
                }
            }
        }.resume()
    }
} 