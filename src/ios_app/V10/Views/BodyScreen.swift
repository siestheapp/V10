import SwiftUI

struct GarmentDetail: Identifiable {
    let id = UUID()
    let brand: String
    let productName: String
    let size: String
    let measurementDisplay: String
    let feedback: String
    let feedbackSource: String?
    let guideLevel: String
    let feedbackDate: Date?
}

class BodyMeasurementViewModel: ObservableObject {
    @Published var estimatedChest: String = ""
    @Published var estimatedNeck: String = ""
    @Published var estimatedArmLength: String = ""
    @Published var isLoading = false
    @Published var error: String?
    @Published var hasData = false
    
    @Published var chestDetails: [GarmentDetail] = []
    @Published var neckDetails: [GarmentDetail] = []
    @Published var armLengthDetails: [GarmentDetail] = []

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
                        
                        if let armLength = json["estimated_arm_length"] as? Double {
                            self.estimatedArmLength = String(format: "%.1f in", armLength)
                        }
                        
                        // Parse detailed garment data
                        if let chestDetailsData = json["chest_details"] as? [[String: Any]] {
                            self.chestDetails = self.parseGarmentDetails(chestDetailsData)
                        }
                        
                        if let neckDetailsData = json["neck_details"] as? [[String: Any]] {
                            self.neckDetails = self.parseGarmentDetails(neckDetailsData)
                        }
                        
                        if let armDetailsData = json["arm_length_details"] as? [[String: Any]] {
                            self.armLengthDetails = self.parseGarmentDetails(armDetailsData)
                        }
                        
                        // Check if we have any measurements
                        if !self.estimatedChest.isEmpty || !self.estimatedNeck.isEmpty || !self.estimatedArmLength.isEmpty {
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
    
    private func parseGarmentDetails(_ data: [[String: Any]]) -> [GarmentDetail] {
        let dateFormatter = ISO8601DateFormatter()
        
        return data.compactMap { item in
            guard let brand = item["brand"] as? String,
                  let productName = item["product_name"] as? String,
                  let size = item["size"] as? String,
                  let measurementDisplay = item["measurement_display"] as? String,
                  let feedback = item["feedback"] as? String,
                  let guideLevel = item["guide_level"] as? String else {
                return nil
            }
            
            // Parse feedback date from string
            var feedbackDate: Date?
            if let dateString = item["feedback_date"] as? String {
                feedbackDate = dateFormatter.date(from: dateString)
            }
            
            return GarmentDetail(
                brand: brand,
                productName: productName,
                size: size,
                measurementDisplay: measurementDisplay,
                feedback: feedback,
                feedbackSource: item["feedback_source"] as? String,
                guideLevel: guideLevel,
                feedbackDate: feedbackDate
            )
        }
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
                ScrollView {
                    VStack(spacing: 32) {
                        // Main measurements section
                        VStack(spacing: 20) {
                            MeasurementCard(title: "Chest", value: viewModel.estimatedChest, icon: "person.fill")
                            MeasurementCard(title: "Neck", value: viewModel.estimatedNeck, icon: "person.crop.circle")
                            MeasurementCard(title: "Arm Length", value: viewModel.estimatedArmLength, icon: "ruler")
                        }
                        
                        Text("Based on your garment feedback")
                            .font(.footnote)
                            .foregroundColor(.secondary)
                        
                        // Visual separator
                        Rectangle()
                            .fill(Color(.systemGray4))
                            .frame(height: 1)
                            .padding(.horizontal)
                        
                        // Detailed breakdown sections
                        VStack(spacing: 24) {
                            if !viewModel.chestDetails.isEmpty {
                                DetailedMeasurementSection(title: "Chest Data", details: viewModel.chestDetails)
                            }
                            
                            if !viewModel.neckDetails.isEmpty {
                                DetailedMeasurementSection(title: "Neck Data", details: viewModel.neckDetails)
                            }
                            
                            if !viewModel.armLengthDetails.isEmpty {
                                DetailedMeasurementSection(title: "Arm Length Data", details: viewModel.armLengthDetails)
                            }
                        }
                    }
                    .padding(.horizontal)
                    .padding(.bottom, 32)
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
        HStack(spacing: 16) {
            Image(systemName: icon)
                .font(.title)
                .foregroundColor(.blue)
                .frame(width: 40, height: 40)
                .background(Color.blue.opacity(0.1))
                .clipShape(Circle())
            
            VStack(alignment: .leading, spacing: 6) {
                Text(title)
                    .font(.headline)
                    .fontWeight(.semibold)
                    .foregroundColor(.primary)
                
                Text(value)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.blue)
            }
            
            Spacer()
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Color(.systemBackground))
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(Color(.systemGray5), lineWidth: 1)
        )
    }
}

struct DetailedMeasurementSection: View {
    let title: String
    let details: [GarmentDetail]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(title)
                .font(.title3)
                .fontWeight(.semibold)
                .foregroundColor(.primary)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            // Group garments by feedback type
            ForEach(groupedByFeedback.keys.sorted(), id: \.self) { feedbackType in
                if let garments = groupedByFeedback[feedbackType] {
                    VStack(alignment: .leading, spacing: 8) {
                        // Feedback header
                        HStack {
                            Circle()
                                .fill(feedbackColor(for: feedbackType))
                                .frame(width: 8, height: 8)
                            
                            Text(feedbackType)
                                .font(.callout)
                                .fontWeight(.medium)
                                .foregroundColor(feedbackColor(for: feedbackType))
                            
                            Spacer()
                        }
                        .padding(.bottom, 4)
                        
                        // Garments under this feedback type (most recent first)
                        ForEach(garments.sorted { first, second in
                            guard let firstDate = first.feedbackDate,
                                  let secondDate = second.feedbackDate else {
                                return false // Put items without dates at the end
                            }
                            return firstDate > secondDate // Most recent first
                        }) { detail in
                            HStack(spacing: 12) {
                                Text(detail.brand)
                                    .font(.callout)
                                    .fontWeight(.medium)
                                    .foregroundColor(.primary)
                                
                                Text(detail.size)
                                    .font(.callout)
                                    .foregroundColor(.secondary)
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(Color(.systemGray6))
                                    .cornerRadius(4)
                                
                                Text(detail.measurementDisplay)
                                    .font(.callout)
                                    .fontWeight(.medium)
                                    .foregroundColor(.blue)
                                
                                Spacer()
                            }
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .fill(Color(.systemBackground))
                                    .shadow(color: .black.opacity(0.02), radius: 2, x: 0, y: 1)
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(feedbackColor(for: feedbackType).opacity(0.2), lineWidth: 1)
                            )
                            .padding(.leading, 20)
                        }
                    }
                    .padding(.bottom, 8)
                }
            }
        }
        .padding(.horizontal, 4)
    }
    
    // Group garments by their feedback type
    private var groupedByFeedback: [String: [GarmentDetail]] {
        Dictionary(grouping: details) { $0.feedback }
    }
    
    private func feedbackColor(for feedback: String) -> Color {
        switch feedback.lowercased() {
        case "good fit":
            return .green
        case "tight but i like it", "slightly tight":
            return .orange
        case "loose but i like it", "slightly loose":
            return .blue
        case "too tight", "too loose":
            return .red
        default:
            return .gray
        }
    }
}

struct BodyScreen_Previews: PreviewProvider {
    static var previews: some View {
        BodyScreen()
    }
} 