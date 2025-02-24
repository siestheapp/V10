import SwiftUI

struct ClosetGarment: Identifiable, Codable {
    let id: Int
    let brand: String
    let category: String
    let size: String
    let chestRange: String
    let fitFeedback: String?
    let createdAt: String
    let ownsGarment: Bool
}

struct ClosetListView: View {
    @State private var garments: [ClosetGarment] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var showingDetail = false
    @State private var selectedGarment: ClosetGarment?
    
    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView("Loading your closet...")
                } else if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                } else {
                    List {
                        ForEach(garments) { garment in
                            GarmentRow(garment: garment)
                                .contentShape(Rectangle())
                                .onTapGesture {
                                    selectedGarment = garment
                                }
                        }
                    }
                }
            }
            .navigationTitle("My Closet")
            .sheet(item: $selectedGarment) { garment in
                GarmentDetailView(
                    garment: garment,
                    isPresented: Binding(
                        get: { selectedGarment != nil },
                        set: { if !$0 { selectedGarment = nil } }
                    )
                )
            }
            .onAppear {
                loadGarments()
            }
        }
    }
    
    private func loadGarments() {
        guard let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/closet") else {
            errorMessage = "Invalid URL"
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                self.isLoading = false
                
                if let error = error {
                    self.errorMessage = error.localizedDescription
                    return
                }
                
                guard let data = data else {
                    self.errorMessage = "No data received"
                    return
                }
                
                do {
                    let garments = try JSONDecoder().decode([ClosetGarment].self, from: data)
                    self.garments = garments
                } catch {
                    self.errorMessage = "Failed to decode response: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
}

struct GarmentRow: View {
    let garment: ClosetGarment
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(garment.brand)
                .font(.headline)
            Text(garment.category)
                .foregroundColor(.gray)
            HStack {
                Text(garment.size)
                    .font(.subheadline)
                if let feedback = garment.fitFeedback {
                    Text("(\(feedback))")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }
            Text("Chest: \(garment.chestRange)")
                .font(.caption)
                .foregroundColor(.gray)
        }
        .padding(.vertical, 4)
    }
} 