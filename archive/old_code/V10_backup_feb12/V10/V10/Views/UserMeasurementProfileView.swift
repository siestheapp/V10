import SwiftUI

struct MeasurementResponse: Codable {
    let measurementType: String
    let preferredRange: PreferredRange
    let measurements: [MeasurementItem]
}

struct PreferredRange: Codable {
    let min: Double
    let max: Double
}

struct MeasurementItem: Codable, Identifiable {
    let brand: String
    let garmentName: String
    let value: Double
    let size: String
    let ownsGarment: Bool
    let fitType: String?
    let feedback: String?
    
    var id: String { "\(brand)-\(garmentName)-\(size)" }
}

struct UserMeasurementProfileView: View {
    @State private var measurements: [MeasurementSummary] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var showingOwnedOnly = false
    
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
                        Toggle("Show Only Owned Items", isOn: $showingOwnedOnly)
                            .padding(.vertical, 4)
                        
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
                                    
                                    let filteredMeasurements = showingOwnedOnly ? 
                                        measurement.measurements.filter { $0.ownsGarment } :
                                        measurement.measurements
                                    
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
        guard let url = URL(string: "\(Config.baseURL)/user/\(Config.defaultUserId)/measurements") else {
            errorMessage = "Invalid URL"
            return
        }
        
        print("Loading measurements from: \(url)")  // Debug print
        
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
            
            // Debug print the raw response
            if let rawString = String(data: data, encoding: .utf8) {
                print("Raw response: \(rawString)")
            }
            
            do {
                let response = try JSONDecoder().decode(MeasurementResponse.self, from: data)
                // Debug print the decoded response
                print("Successfully decoded response: \(response)")
                
                DispatchQueue.main.async {
                    self.measurements = [
                        MeasurementSummary(
                            name: response.measurementType.capitalized,
                            measurements: response.measurements.map { item in
                                BrandMeasurement(
                                    brand: item.brand,
                                    garmentName: item.garmentName,
                                    measurementRange: MeasurementRange(value: item.value),
                                    size: item.size,
                                    ownsGarment: item.ownsGarment,
                                    fitContext: item.fitType,
                                    userFeedback: item.feedback,
                                    confidence: 0.9
                                )
                            },
                            preferredRange: MeasurementRange(
                                min: response.preferredRange.min,
                                max: response.preferredRange.max
                            )
                        )
                    ]
                    self.isLoading = false
                }
            } catch {
                print("Decoding error: \(error)")  // More detailed error print
                DispatchQueue.main.async {
                    self.errorMessage = "Failed to parse data: \(error)"
                    self.isLoading = false
                }
            }
        }.resume()
    }
}

#Preview {
    UserMeasurementProfileView()
} 