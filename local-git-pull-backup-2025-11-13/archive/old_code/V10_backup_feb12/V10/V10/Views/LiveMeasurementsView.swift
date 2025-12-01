import SwiftUI

struct IdealMeasurement: Codable, Identifiable {
    let type: String
    let value: Double
    let range: Range
    let confidence: Double
    let sourcesCount: Int
    
    struct Range: Codable {
        let min: Double
        let max: Double
    }
    
    var id: String { type }
    
    var displayName: String {
        type  // Using type as display name for now
    }
    
    private enum CodingKeys: String, CodingKey {
        case type, value, range, confidence
        case sourcesCount = "sourcesCount"  // Match the JSON field name
    }
}

struct LiveMeasurementsView: View {
    @State private var idealMeasurements: [IdealMeasurement] = []
    @State private var errorMessage: String?
    @State private var isLoading = true
    @State private var lastRefresh = Date()
    
    var body: some View {
        VStack {
            if isLoading {
                ProgressView("Loading your measurements...")
            } else if let error = errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .padding()
            } else if !idealMeasurements.isEmpty {
                VStack(spacing: 20) {
                    Text("Your Ideal Measurements")
                        .font(.title2)
                        .fontWeight(.medium)
                    
                    ForEach(idealMeasurements) { measurement in
                        IdealMeasurementRow(measurement: measurement)
                    }
                }
                .padding()
            } else {
                Text("No measurements found")
                    .font(.title)
            }
        }
        .onAppear {
            loadIdealMeasurements()
        }
        .refreshable {
            lastRefresh = Date()
            await loadIdealMeasurements()
        }
    }
    
    private func loadIdealMeasurements() {
        let urlString = "\(baseURL)/user/18/ideal_measurements?t=\(Date().timeIntervalSince1970)"
        guard let url = URL(string: urlString) else {
            errorMessage = "Invalid URL"
            return
        }
        
        print("🔍 Loading from:", url.absoluteString)  // Debug URL
        NetworkLogger.log(url: url)
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    print("❌ Network error:", error)  // Debug error
                    NetworkLogger.logError(error, url: url)
                    errorMessage = error.localizedDescription
                    return
                }
                
                if let httpResponse = response as? HTTPURLResponse {
                    print("📡 Status code:", httpResponse.statusCode)  // Debug response
                }
                
                guard let data = data else {
                    print("⚠️ No data received")  // Debug data
                    errorMessage = "No data received"
                    return
                }
                
                print("📦 Data size:", data.count, "bytes")  // Debug data size
                
                if let jsonString = String(data: data, encoding: .utf8) {
                    print("📄 Raw JSON:", jsonString)  // Debug JSON
                }
                
                do {
                    self.idealMeasurements = try JSONDecoder().decode([IdealMeasurement].self, from: data)
                    print("✅ Decoded measurements:", self.idealMeasurements.count)  // Debug decoded data
                    self.errorMessage = nil
                } catch {
                    print("❌ Decoding error:", error)  // Debug decoding error
                    errorMessage = "Decoding error: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
}

struct IdealMeasurementRow: View {
    let measurement: IdealMeasurement
    @State private var showingDetail = false
    
    var body: some View {
        Button {
            showingDetail = true
        } label: {
            VStack(alignment: .leading, spacing: 8) {
                Text(measurement.displayName)
                    .font(.headline)
                
                HStack {
                    Text("\(measurement.value, specifier: "%.1f")\"")
                        .font(.title3)
                        .foregroundColor(.blue)
                    
                    Spacer()
                    
                    Text("\(measurement.range.min, specifier: "%.1f")\" - \(measurement.range.max, specifier: "%.1f")\"")
                        .foregroundColor(.gray)
                }
                
                ProgressView(value: measurement.confidence)
                    .tint(confidence: measurement.confidence)
            }
        }
        .sheet(isPresented: $showingDetail) {
            DetailedMeasurementView(measurement: measurement, isPresented: $showingDetail)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

extension ProgressView {
    func tint(confidence: Double) -> some View {
        self.tint(
            confidence > 0.8 ? .green :
            confidence > 0.6 ? .blue :
            confidence > 0.4 ? .orange : .red
        )
    }
}

#Preview {
    LiveMeasurementsView()
} 