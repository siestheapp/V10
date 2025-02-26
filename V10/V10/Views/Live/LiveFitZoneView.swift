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
                            ranges: data.tops
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
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    errorMessage = error.localizedDescription
                    return
                }
                
                guard let data = data else {
                    errorMessage = "No data received"
                    return
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
}

struct FitZoneBar: View {
    let label: String
    let ranges: FitZoneRanges
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(label)
                .font(.headline)
            
            // Tight range
            RangeBarView(
                label: "Tight",
                range: ranges.tightRange.asRange,
                color: .orange,
                description: "Fitted, compression-like fit"
            )
            
            // Good range
            RangeBarView(
                label: "Good",
                range: ranges.goodRange.asRange,
                color: .green,
                description: "Comfortable, standard fit"
            )
            
            // Relaxed range
            RangeBarView(
                label: "Relaxed",
                range: ranges.relaxedRange.asRange,
                color: .blue,
                description: "Loose, oversized fit"
            )
        }
    }
}

struct RangeBarView: View {
    let label: String
    let range: ClosedRange<Double>
    let color: Color
    let description: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(label)
                    .font(.subheadline)
                    .foregroundColor(color)
                
                Spacer()
                
                Text("\(range.lowerBound, specifier: "%.1f\"")-\(range.upperBound, specifier: "%.1f\"")")
                    .font(.subheadline)
                    .foregroundColor(color)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    // Background
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
                    
                    // Range indicator
                    RoundedRectangle(cornerRadius: 8)
                        .fill(color.opacity(0.3))
                        .frame(
                            width: width(for: range, in: geometry),
                            height: 24
                        )
                        .offset(x: position(for: range.lowerBound, in: geometry))
                }
            }
            .frame(height: 24)
            
            Text(description)
                .font(.caption)
                .foregroundColor(.gray)
        }
    }
    
    private func position(for value: Double, in geometry: GeometryProxy) -> CGFloat {
        let range = 20.0 // Total range in inches
        let start = 30.0 // Starting measurement
        let position = (value - start) / range
        return geometry.size.width * CGFloat(position)
    }
    
    private func width(for range: ClosedRange<Double>, in geometry: GeometryProxy) -> CGFloat {
        let totalRange = 20.0
        let width = (range.upperBound - range.lowerBound) / totalRange
        return geometry.size.width * CGFloat(width)
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