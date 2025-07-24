import SwiftUI

class BodyMeasurementViewModel: ObservableObject {
    @Published var estimatedChest: String = ""
    @Published var estimatedNeck: String = ""
    @Published var estimatedSleeve: String = ""
    @Published var isLoading = false
    @Published var error: String?
    @Published var hasData = false

    func fetchBodyMeasurements() {
        // Use user ID 1 which has data, or make this configurable
        guard let url = URL(string: "http://localhost:8006/user/1/body-measurements") else { 
            self.error = "Invalid URL"
            return 
        }
        
        isLoading = true
        error = nil

        URLSession.shared.dataTask(with: url) { data, response, err in
            DispatchQueue.main.async {
                self.isLoading = false
                
                if let err = err {
                    self.error = "Connection error: \(err.localizedDescription)"
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    self.error = "Invalid response"
                    return
                }
                
                guard httpResponse.statusCode == 200 else {
                    self.error = "Server error: \(httpResponse.statusCode)"
                    return
                }
                
                guard let data = data else {
                    self.error = "No data received"
                    return
                }
                
                do {
                    if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] {
                        
                        // Check if we have a message indicating no data
                        if let message = json["message"] as? String {
                            self.error = message
                            return
                        }
                        
                        // Parse measurements
                        if let chest = json["estimated_chest"] as? Double {
                            self.estimatedChest = String(format: "%.1f in", chest)
                        }
                        
                        if let neck = json["estimated_neck"] as? Double {
                            self.estimatedNeck = String(format: "%.1f in", neck)
                        }
                        
                        if let sleeve = json["estimated_sleeve"] as? Double {
                            self.estimatedSleeve = String(format: "%.1f in", sleeve)
                        }
                        
                        // Check if we have any measurements
                        if !self.estimatedChest.isEmpty || !self.estimatedNeck.isEmpty || !self.estimatedSleeve.isEmpty {
                            self.hasData = true
                        } else {
                            self.error = "No measurement data available"
                        }
                        
                    } else {
                        self.error = "Could not parse response"
                    }
                } catch {
                    self.error = "Parse error: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
}

struct BodyScreen: View {
    @StateObject private var viewModel = BodyMeasurementViewModel()

    var body: some View {
        VStack(spacing: 24) {
            Text("Body")
                .font(.largeTitle)
                .bold()
            
            Text("Body Measurements")
                .font(.title2)
                .foregroundColor(.secondary)
            
            if viewModel.isLoading {
                VStack(spacing: 16) {
                    ProgressView()
                        .scaleEffect(1.2)
                    Text("Calculating your measurements...")
                        .foregroundColor(.secondary)
                }
            } else if let error = viewModel.error {
                VStack(spacing: 16) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.system(size: 40))
                        .foregroundColor(.orange)
                    Text("Error")
                        .font(.headline)
                    Text(error)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                    Button("Retry") {
                        viewModel.fetchBodyMeasurements()
                    }
                    .buttonStyle(.borderedProminent)
                }
            } else if viewModel.hasData {
                VStack(spacing: 20) {
                    MeasurementCard(title: "Chest", value: viewModel.estimatedChest, icon: "person.fill")
                    MeasurementCard(title: "Neck", value: viewModel.estimatedNeck, icon: "person.crop.circle")
                    MeasurementCard(title: "Arm Length", value: viewModel.estimatedSleeve, icon: "ruler")
                    
                    Text("Based on your garment feedback")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding(.top)
                }
            } else {
                VStack(spacing: 16) {
                    Image(systemName: "ruler")
                        .font(.system(size: 40))
                        .foregroundColor(.blue)
                    Text("No measurements available")
                        .font(.headline)
                    Text("Add garments and provide fit feedback to get your estimated body measurements.")
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
            }
            
            Spacer()
        }
        .onAppear {
            viewModel.fetchBodyMeasurements()
        }
        .padding()
        .navigationTitle("Body")
    }
}

struct MeasurementCard: View {
    let title: String
    let value: String
    let icon: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.blue)
                .frame(width: 30)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(value)
                    .font(.title3)
                    .bold()
                    .foregroundColor(.primary)
            }
            
            Spacer()
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct BodyScreen_Previews: PreviewProvider {
    static var previews: some View {
        BodyScreen()
    }
} 