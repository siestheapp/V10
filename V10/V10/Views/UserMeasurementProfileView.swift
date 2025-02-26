import SwiftUI

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
                
                // Create some sample measurements for testing
                let sampleMeasurements = [
                    BrandMeasurement(
                        brand: "J.Crew",
                        garmentName: "Cotton Oxford Shirt",
                        value: response.tops.goodRange.min,
                        size: "M",
                        ownsGarment: true,
                        fitType: "Good",
                        feedback: "Perfect fit in shoulders"
                    ),
                    BrandMeasurement(
                        brand: "Uniqlo",
                        garmentName: "Supima Cotton T-Shirt",
                        value: response.tops.goodRange.max,
                        size: "L",
                        ownsGarment: true,
                        fitType: "Relaxed",
                        feedback: "Slightly loose but comfortable"
                    )
                ]
                
                DispatchQueue.main.async {
                    self.measurements = [
                        MeasurementSummary(
                            name: "Tops",
                            measurements: sampleMeasurements,
                            preferredRange: response.tops.goodRange
                        )
                    ]
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

#Preview {
    UserMeasurementProfileView()
} 