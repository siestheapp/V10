import SwiftUI

struct ClosetGarment: Identifiable, Codable {
    let id: Int
    let brand: String
    let category: String
    let size: String
    let measurements: [String: String]
    let fitFeedback: String?
    let chestFit: String?
    let sleeveFit: String?
    let neckFit: String?
    let waistFit: String?
    let createdAt: String?
    let ownsGarment: Bool
    let productName: String?
    let imageUrl: String?
    let productUrl: String?
    
    enum CodingKeys: String, CodingKey {
        case id, brand, category, size, measurements
        case fitFeedback = "fitFeedback"
        case chestFit = "chestFit"
        case sleeveFit = "sleeveFit"
        case neckFit = "neckFit"
        case waistFit = "waistFit"
        case createdAt = "createdAt"
        case ownsGarment = "ownsGarment"
        case productName = "productName"
        case imageUrl = "imageUrl"
        case productUrl = "productUrl"
    }
}

struct ClosetListView: View {
    @State private var garments: [ClosetGarment] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var showingDetail = false
    @State private var selectedGarment: ClosetGarment?
    @State private var showingFinds = false
    
    // Group garments by category
    private var garmentsByCategory: [String: [ClosetGarment]] {
        Dictionary(grouping: garments) { $0.category }
    }
    
    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView("Loading your closet...")
                } else if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                } else {
                    VStack {
                        List {
                            ForEach(Array(garmentsByCategory.keys.sorted()), id: \.self) { category in
                                Section {
                                    ForEach(garmentsByCategory[category] ?? []) { garment in
                                        GarmentRow(garment: garment)
                                            .contentShape(Rectangle())
                                            .onTapGesture {
                                                selectedGarment = garment
                                            }
                                    }
                                } header: {
                                    Text(category)
                                        .font(.title2)
                                        .fontWeight(.bold)
                                        .foregroundColor(.primary)
                                        .textCase(nil)
                                        .padding(.vertical, 8)
                                }
                            }
                        }
                        .listStyle(PlainListStyle())
                    }
                }
            }
            .navigationTitle("My Closet")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingFinds = true
                    }) {
                        HStack {
                            Image(systemName: "list.bullet")
                            Text("Finds")
                        }
                    }
                }
            }
            .sheet(item: $selectedGarment) { garment in
                GarmentDetailView(
                    garment: garment,
                    isPresented: Binding(
                        get: { selectedGarment != nil },
                        set: { if !$0 { selectedGarment = nil } }
                    ),
                    onGarmentUpdated: {
                        // Refresh garment data when feedback is updated
                        loadGarments()
                    }
                )
            }
            .sheet(isPresented: $showingFinds) {
                NavigationView {
                    FindsView()
                        .toolbar {
                            ToolbarItem(placement: .navigationBarTrailing) {
                                Button("Done") {
                                    showingFinds = false
                                }
                            }
                        }
                }
            }
            .onAppear {
                // Load garments on first appearance or when empty
                if garments.isEmpty {
                    loadGarments()
                }
            }
        }
    }
    
    private func loadGarments() {
        isLoading = true
        errorMessage = nil
        
        print("🔧 Debug Config values:")
        print("   Config.baseURL = \(Config.baseURL)")
        print("   Config.defaultUserId = \(Config.defaultUserId)")
        
        let urlString = "\(Config.baseURL)/user/\(Config.defaultUserId)/closet"
        print("🔍 Loading garments from: \(urlString)")
        
        guard let url = URL(string: urlString) else {
            errorMessage = "Invalid URL: \(urlString)"
            print("❌ Invalid URL: \(urlString)")
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                self.isLoading = false
                
                if let error = error {
                    self.errorMessage = error.localizedDescription
                    print("❌ Network error: \(error.localizedDescription)")
                    return
                }
                
                if let httpResponse = response as? HTTPURLResponse {
                    print("📡 HTTP Status: \(httpResponse.statusCode)")
                }
                
                guard let data = data else {
                    self.errorMessage = "No data received"
                    print("❌ No data received")
                    return
                }
                
                // Add debug logging
                if let rawString = String(data: data, encoding: .utf8) {
                    print("📦 Raw response data: \(rawString)")
                }
                
                do {
                    let garments = try JSONDecoder().decode([ClosetGarment].self, from: data)
                    print("✅ Successfully decoded \(garments.count) garments")
                    self.garments = garments
                } catch {
                    print("❌ Decoding error details: \(error)")
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
            HStack {
                // Garment image
                if let imageUrl = garment.imageUrl, let url = URL(string: imageUrl) {
                    AsyncImage(url: url) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                    } placeholder: {
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .overlay(
                                Image(systemName: "tshirt")
                                    .foregroundColor(.gray)
                            )
                    }
                    .frame(width: 60, height: 60)
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                } else {
                    // Placeholder when no image
                    Rectangle()
                        .fill(Color.gray.opacity(0.3))
                        .frame(width: 60, height: 60)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                        .overlay(
                            Image(systemName: "tshirt")
                                .foregroundColor(.gray)
                        )
                }
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(garment.brand)
                        .font(.headline)
                    
                    if let productName = garment.productName {
                        Text(productName)
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                }
                
                Spacer()
                
                // Feedback indicator
                if let feedback = garment.fitFeedback {
                    HStack(spacing: 4) {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                            .font(.caption)
                        Text(feedback)
                            .font(.caption)
                            .foregroundColor(.green)
                    }
                } else {
                    HStack(spacing: 4) {
                        Image(systemName: "exclamationmark.circle")
                            .foregroundColor(.orange)
                            .font(.caption)
                        Text("Add feedback")
                            .font(.caption)
                            .foregroundColor(.orange)
                    }
                }
            }
            
            HStack {
                Text(garment.size)
                    .font(.subheadline)
                    .foregroundColor(.gray)
                
                Spacer()
                
                // Show measurements that are available
                if let chest = garment.measurements["chest"] {
                    HStack(spacing: 8) {
                        Text("Chest: \(chest)")
                            .font(.caption)
                            .foregroundColor(.gray)
                        
                        let additionalMeasurements = garment.measurements.filter { key, _ in
                            key != "chest"
                        }.count
                        
                        if additionalMeasurements > 0 {
                            Text("+ \(additionalMeasurements) more")
                                .font(.caption)
                                .foregroundColor(.blue)
                        }
                    }
                }
            }
        }
        .padding(.vertical, 4)
    }
} 