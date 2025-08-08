import SwiftUI

struct UserMeasurementProfileView: View {
    @State private var measurements: [MeasurementSummary] = []
    @State private var isLoading = true
    @State private var  errorMessage: String?
    @State private var showingOwnedOnly = false
    @State private var comprehensiveData: ComprehensiveMeasurementData? = nil
    
    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView("Loading measurements...")
                } else if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                } else {
                    measurementListView
                }
            }
            .navigationTitle("My Measurements")
            .onAppear {
                loadMeasurements()
            }
        }
    }
    
    private var measurementListView: some View {
        List {
            // Comprehensive Fit Zone Ranges
            if let data = comprehensiveData {
                Section(header: Text("FIT ZONE RANGES").font(.headline)) {
                    // Chest Fit Zones
                    VStack(alignment: .leading, spacing: 12) {
                        Text("CHEST")
                            .font(.subheadline)
                            .fontWeight(.bold)
                            .foregroundColor(.primary)
                        
                        if let chestData = data.chest {
                            FitZoneBar(label: "Tops", ranges: chestData)
                        }
                    }
                    .padding(.vertical, 8)
                    
                    // Neck Fit Zone
                    VStack(alignment: .leading, spacing: 12) {
                        Text("NECK")
                            .font(.subheadline)
                            .fontWeight(.bold)
                            .foregroundColor(.primary)
                        
                        if let neckData = data.neck {
                            NeckFitZoneView(neckData: neckData)
                        }
                    }
                    .padding(.vertical, 8)
                    
                    // Sleeve Fit Zone
                    VStack(alignment: .leading, spacing: 12) {
                        Text("SLEEVE")
                            .font(.subheadline)
                            .fontWeight(.bold)
                            .foregroundColor(.primary)
                        
                        if let sleeveData = data.sleeve {
                            SleeveFitZoneView(sleeveData: sleeveData)
                        }
                    }
                    .padding(.vertical, 8)
                }
            }
            
            Toggle("Show Only Owned Items", isOn: $showingOwnedOnly)
                .padding(.vertical, 4)
            
            // Individual Dimension Sections
            if let data = comprehensiveData {
                // Chest Garments
                if let chestData = data.chest, !chestData.garments.isEmpty {
                    dimensionSection(
                        title: "CHEST GARMENTS",
                        garments: chestData.garments,
                        showingOwnedOnly: showingOwnedOnly
                    )
                }
                
                // Neck Garments
                if let neckData = data.neck, !neckData.garments.isEmpty {
                    dimensionSection(
                        title: "NECK GARMENTS", 
                        garments: neckData.garments,
                        showingOwnedOnly: showingOwnedOnly
                    )
                }
                
                // Sleeve Garments
                if let sleeveData = data.sleeve, !sleeveData.garments.isEmpty {
                    dimensionSection(
                        title: "SLEEVE GARMENTS",
                        garments: sleeveData.garments,
                        showingOwnedOnly: showingOwnedOnly
                    )
                }
            }
        }
    }
    
    private func dimensionSection(title: String, garments: [GarmentData], showingOwnedOnly: Bool) -> some View {
        Section {
            VStack(alignment: .leading, spacing: 12) {
                let filteredGarments = showingOwnedOnly ? garments.filter { $0.ownsGarment } : garments
                
                ForEach(filteredGarments, id: \.id) { garment in
                    GarmentDetailRow(garment: garment)
                }
            }
        } header: {
            Text(title)
                .font(.subheadline)
                .foregroundColor(.gray)
        }
    }
    
    private func loadMeasurements() {
        guard let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/measurements") else {
            errorMessage = "Invalid URL"
            return
        }
        print("Loading measurements from: \(url)")
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    self.errorMessage = "Error: \(error.localizedDescription)"
                    self.isLoading = false
                }
                return
            }
            guard let data = data else {
                DispatchQueue.main.async {
                    self.errorMessage = "No data received"
                    self.isLoading = false
                }
                return
            }
            if let rawString = String(data: data, encoding: .utf8) {
                print("Raw response: \(rawString)")
            }
            do {
                let response = try JSONDecoder().decode(ComprehensiveMeasurementResponse.self, from: data)
                DispatchQueue.main.async {
                    self.comprehensiveData = response.tops
                    self.isLoading = false
                }
            } catch {
                print("Decoding error: \(error)")
                DispatchQueue.main.async {
                    self.errorMessage = "Failed to parse data: \(error)"
                    self.isLoading = false
                }
            }
        }.resume()
    }
}



// MARK: - View Components
struct NeckFitZoneView: View {
    let neckData: DimensionData
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Good")
                    .font(.subheadline)
                    .foregroundColor(.green)
                Spacer()
                Text(String(format: "%.1f\"-%.1f\"", neckData.goodRange.min, neckData.goodRange.max))
                    .font(.subheadline)
                    .foregroundColor(.green)
            }
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.green.opacity(0.3))
                        .frame(
                            width: width(for: neckData.goodRange.asRange, in: geometry),
                            height: 24
                        )
                        .offset(x: position(for: neckData.goodRange.min, in: geometry))
                }
            }
            .frame(height: 24)
            Text("Comfortable, standard fit")
                .font(.caption)
                .foregroundColor(.gray)
        }
        .padding(.vertical, 8)
    }
    
    private func position(for value: Double, in geometry: GeometryProxy) -> CGFloat {
        let range = 10.0 // Total range in inches for neck
        let start = 14.0 // Starting measurement for neck
        let position = (value - start) / range
        return geometry.size.width * CGFloat(position)
    }
    
    private func width(for range: ClosedRange<Double>, in geometry: GeometryProxy) -> CGFloat {
        let totalRange = 10.0
        let width = (range.upperBound - range.lowerBound) / totalRange
        return geometry.size.width * CGFloat(width)
    }
}

struct SleeveFitZoneView: View {
    let sleeveData: DimensionData
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Good")
                    .font(.subheadline)
                    .foregroundColor(.green)
                Spacer()
                Text(String(format: "%.1f\"-%.1f\"", sleeveData.goodRange.min, sleeveData.goodRange.max))
                    .font(.subheadline)
                    .foregroundColor(.green)
            }
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.green.opacity(0.3))
                        .frame(
                            width: width(for: sleeveData.goodRange.asRange, in: geometry),
                            height: 24
                        )
                        .offset(x: position(for: sleeveData.goodRange.min, in: geometry))
                }
            }
            .frame(height: 24)
            Text("Comfortable, standard fit")
                .font(.caption)
                .foregroundColor(.gray)
        }
        .padding(.vertical, 8)
    }
    
    private func position(for value: Double, in geometry: GeometryProxy) -> CGFloat {
        let range = 15.0 // Total range in inches for sleeve
        let start = 30.0 // Starting measurement for sleeve
        let position = (value - start) / range
        return geometry.size.width * CGFloat(position)
    }
    
    private func width(for range: ClosedRange<Double>, in geometry: GeometryProxy) -> CGFloat {
        let totalRange = 15.0
        let width = (range.upperBound - range.lowerBound) / totalRange
        return geometry.size.width * CGFloat(width)
    }
}

struct GarmentDetailRow: View {
    let garment: GarmentData
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text("\(garment.brand) \(garment.size)")
                    .fontWeight(.medium)
                Spacer()
                Text(garment.range)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            if !garment.fitFeedback.isEmpty {
                Text(garment.fitFeedback)
                    .font(.caption)
                    .foregroundColor(.blue)
            }
            
            if !garment.feedback.isEmpty {
                Text(garment.feedback)
                    .font(.caption)
                    .foregroundColor(.orange)
            }
        }
        .padding(.vertical, 2)
    }
}

// MARK: - Existing Components (unchanged)
struct FitZoneBar: View {
    let label: String
    let ranges: DimensionData
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(label)
                .font(.headline)
            if let tightRange = ranges.tightRange {
                RangeBarView(label: "Tight", range: tightRange.asRange, color: .orange, description: "Fitted, compression-like fit")
            }
            RangeBarView(label: "Good", range: ranges.goodRange.asRange, color: .green, description: "Comfortable, standard fit")
            if let relaxedRange = ranges.relaxedRange {
                RangeBarView(label: "Relaxed", range: relaxedRange.asRange, color: .blue, description: "Loose, oversized fit")
            }
        }
        .padding(.vertical, 8)
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
                Text(String(format: "%.1f\"-%.1f\"", range.lowerBound, range.upperBound))
                    .font(.subheadline)
                    .foregroundColor(color)
            }
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
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

struct UserMeasurementProfileView_Previews: PreviewProvider {
    static var previews: some View {
        UserMeasurementProfileView()
    }
} 
