import SwiftUI

struct UserMeasurementProfileView: View {
    @State private var measurements: [MeasurementSummary] = []
    @State private var isLoading = true
    @State private var  errorMessage: String?
    @State private var showingOwnedOnly = false
    @State private var fitZoneRanges: FitZoneRanges? = nil
    
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
            // Fit Zone Ranges Bar at the top
            if let fitZoneRanges = fitZoneRanges {
                Section(header: Text("Fit Zone Ranges").font(.headline)) {
                    FitZoneBar(label: "Tops", ranges: fitZoneRanges)
                }
            }
            
            Toggle("Show Only Owned Items", isOn: $showingOwnedOnly)
                .padding(.vertical, 4)
            
            ForEach(measurements) { measurement in
                measurementSection(for: measurement)
            }
        }
    }
    
    private func measurementSection(for measurement: MeasurementSummary) -> some View {
        Section {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text("Preferred Range")
                        .fontWeight(.medium)
                    Spacer()
                    Text(String(format: "%.1f-%.1f\"", measurement.preferredRange.min, measurement.preferredRange.max))
                }
                
                Text("Based on owned items:")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.top, 4)
                
                let filteredMeasurements = showingOwnedOnly ? measurement.measurements.filter { $0.ownsGarment } : measurement.measurements
                
                ForEach(filteredMeasurements) { brandMeasurement in
                    MeasurementDetailRow(measurement: brandMeasurement)
                }
            }
        } header: {
            Text(measurement.name.uppercased())
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
                let response = try JSONDecoder().decode(FitZoneResponse.self, from: data)
                let measurements = response.tops.garments.map { garment in
                    BrandMeasurement(
                        brand: garment.brand,
                        garmentName: garment.garmentName,
                        value: garment.chestValue,
                        chestRange: garment.chestRange,
                        size: garment.size,
                        ownsGarment: true,
                        fitType: garment.fitFeedback,
                        feedback: garment.feedback
                    )
                }
                DispatchQueue.main.async {
                    self.measurements = [
                        MeasurementSummary(
                            name: "Tops",
                            measurements: measurements,
                            preferredRange: response.tops.goodRange
                        )
                    ]
                    self.fitZoneRanges = response.tops
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

// --- FitZoneBar and RangeBarView from LiveFitZoneView ---
struct FitZoneBar: View {
    let label: String
    let ranges: FitZoneRanges
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(label)
                .font(.headline)
            RangeBarView(label: "Tight", range: ranges.tightRange.asRange, color: .orange, description: "Fitted, compression-like fit")
            RangeBarView(label: "Good", range: ranges.goodRange.asRange, color: .green, description: "Comfortable, standard fit")
            RangeBarView(label: "Relaxed", range: ranges.relaxedRange.asRange, color: .blue, description: "Loose, oversized fit")
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
