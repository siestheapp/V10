import SwiftUI

struct UserMeasurementProfileView: View {
    @State private var measurements: [MeasurementSummary] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            Group {
                if isLoading {
                    ProgressView("Loading measurements...")
                } else if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                } else {
                    List {
                        ForEach(measurements) { measurement in
                            Section {
                                VStack(alignment: .leading, spacing: 12) {
                                    HStack {
                                        Text("Preferred Range")
                                            .fontWeight(.medium)
                                        Spacer()
                                        Text(String(format: "%.1f-%.1f\"",
                                             measurement.preferredRange.min,
                                             measurement.preferredRange.max))
                                    }
                                    
                                    Text("Based on owned items:")
                                        .font(.caption)
                                        .foregroundColor(.gray)
                                        .padding(.top, 4)
                                    
                                    ForEach(measurement.measurements) { brandMeasurement in
                                        MeasurementDetailRow(measurement: brandMeasurement)
                                    }
                                }
                            } header: {
                                Text(measurement.name.uppercased())
                                    .font(.subheadline)
                                    .foregroundColor(.gray)
                            }
                        }
                    }
                }
            }
            .navigationTitle("My Measurements")
            .onAppear {
                loadMeasurements()
            }
        }
    }
    
    private func loadMeasurements() {
        guard let url = URL(string: "\(Config.baseURL)/user/measurements") else {
            errorMessage = "Invalid URL"
            return
        }
        
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
            
            // TODO: Parse response and update measurements
            // For now, let's add some sample data
            DispatchQueue.main.async {
                self.measurements = [
                    MeasurementSummary(
                        name: "Chest",
                        measurements: [
                            BrandMeasurement(brand: "Uniqlo", garmentName: "Waffle T-Shirt", measurementRange: MeasurementRange(value: 41.0), size: "L", ownsGarment: true, fitContext: nil, userFeedback: nil, confidence: 0.9),
                            BrandMeasurement(brand: "J.Crew", garmentName: "Cotton Sweater", measurementRange: MeasurementRange(value: 43.0), size: "L", ownsGarment: true, fitContext: nil, userFeedback: nil, confidence: 0.9)
                        ],
                        preferredRange: MeasurementRange(min: 41.0, max: 43.0)
                    )
                ]
                self.isLoading = false
            }
        }.resume()
    }
}

#Preview {
    UserMeasurementProfileView()
} 