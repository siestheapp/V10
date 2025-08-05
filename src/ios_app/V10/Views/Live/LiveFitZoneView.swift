import SwiftUI

struct LiveFitZoneView: View {
    @State private var selectedCategory = "Tops"
    @State private var fitZoneData: FitZoneResponse?
    @State private var isLoading = true
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                if isLoading {
                    ProgressView("Loading fit zones...")
                } else if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                } else if let data = fitZoneData {
                    // Category Picker
                    Picker("Category", selection: $selectedCategory) {
                        Text("Tops").tag("Tops")
                        Text("Bottoms").tag("Bottoms")
                        Text("Outerwear").tag("Outerwear")
                    }
                    .pickerStyle(.segmented)
                    .padding()
                    
                    // Fit Zone Visualization
                    VStack(alignment: .leading, spacing: 30) {
                        FitZoneBar(
                            label: selectedCategory,
                            ranges: convertToChestDimensionData(data.tops)
                        )
                    }
                    .padding()
                    
                    Spacer()
                }
            }
            .navigationTitle("Live Fit Zones")
            .onAppear {
                loadFitZones()
            }
        }
    }
    
    private func loadFitZones() {
        guard let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/measurements") else {
            errorMessage = "Invalid URL"
            return
        }
        print("🔍 LiveFitZoneView: Loading from \(url)")
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    errorMessage = error.localizedDescription
                    print("❌ LiveFitZoneView: Network error:", error)
                    return
                }
                
                guard let data = data else {
                    errorMessage = "No data received"
                    print("⚠️ LiveFitZoneView: No data received")
                    return
                }
                
                if let jsonString = String(data: data, encoding: .utf8) {
                    print("📄 LiveFitZoneView Raw JSON:", jsonString)
                }
                
                do {
                    fitZoneData = try JSONDecoder().decode(FitZoneResponse.self, from: data)
                } catch {
                    errorMessage = "Failed to decode: \(error.localizedDescription)"
                    print("Decode error: \(error)")
                }
            }
        }.resume()
    }
    
    // Convert FitZoneRanges to DimensionData for chest measurements
    private func convertToChestDimensionData(_ fitZoneRanges: FitZoneRanges) -> DimensionData {
        return DimensionData(
            tightRange: fitZoneRanges.tightRange,
            goodRange: fitZoneRanges.goodRange,
            relaxedRange: fitZoneRanges.relaxedRange,
            garments: fitZoneRanges.garments.map { garment in
                GarmentData(
                    brand: garment.brand,
                    garmentName: garment.garmentName,
                    range: garment.chestRange ?? "",
                    value: garment.chestValue,
                    size: garment.size,
                    fitFeedback: garment.fitFeedback,
                    feedback: garment.feedback,
                    ownsGarment: true
                )
            }
        )
    }
}

struct MarkerView: View {
    let value: Double
    let color: Color
    let label: String
    
    var body: some View {
        VStack(spacing: 4) {
            RoundedRectangle(cornerRadius: 8)
                .fill(color)
                .frame(width: 4, height: 30)
            Text(label)
                .font(.caption2)
                .foregroundColor(color)
        }
    }
} 