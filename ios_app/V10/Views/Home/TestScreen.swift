import SwiftUI

struct TestScreen: View {
    @State private var userData: UserTestData?
    @State private var liveMeasurements: LiveMeasurementsResponse?
    @State private var isLoading = true
    let timer = Timer.publish(every: 2, on: .main, in: .common).autoconnect() // Updates every 2 seconds
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                if isLoading {
                    ProgressView("Loading user data...")
                } else if let data = userData {
                    // User Basic Info Section
                    GroupBox("User Information") {
                        VStack(alignment: .leading, spacing: 8) {
                            InfoRow(label: "ID", value: "\(data.id)")
                            InfoRow(label: "Email", value: data.email)
                            InfoRow(label: "Created", value: data.createdAt)
                            InfoRow(label: "Gender", value: data.gender)
                            InfoRow(label: "Unit Preference", value: data.unitPreference)
                        }
                    }
                    
                    // Garments Summary Section
                    GroupBox("Garments Summary") {
                        VStack(alignment: .leading, spacing: 8) {
                            InfoRow(label: "Total Garments", value: "\(data.totalGarments)")
                            InfoRow(label: "Last Input", value: data.lastGarmentInput)
                            InfoRow(label: "Brands in Closet", value: data.brandsOwned.joined(separator: ", "))
                        }
                    }
                    
                    // Database Fit Zones Section (from /test/user/2)
                    GroupBox("Database Fit Zones") {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Direct from user_fit_zones table:")
                                .font(.headline)
                            Text("SELECT * FROM user_fit_zones WHERE user_id = 2")
                                .font(.caption)
                                .foregroundColor(.gray)
                            
                            VStack(alignment: .leading, spacing: 4) {
                                InfoRow(label: "Tight Range", value: "\(data.fitZones.tightMin) - \(data.fitZones.tightMax)")
                                InfoRow(label: "Good Range", value: "\(data.fitZones.goodMin) - \(data.fitZones.goodMax)")
                                InfoRow(label: "Relaxed Range", value: "\(data.fitZones.relaxedMin) - \(data.fitZones.relaxedMax)")
                            }
                            .padding(.leading)
                        }
                    }
                    
                    // Live Calculated Fit Zones Section (from /user/2/measurements)
                    GroupBox("Live Calculated Fit Zones") {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("From FitZoneCalculator:")
                                .font(.headline)
                            Text("Via /user/{id}/measurements endpoint")
                                .font(.caption)
                                .foregroundColor(.gray)
                            
                            if let live = liveMeasurements?.Tops {
                                VStack(alignment: .leading, spacing: 4) {
                                    InfoRow(label: "Tight Range", value: "\(live.tightRange.min) - \(live.tightRange.max)")
                                    InfoRow(label: "Good Range", value: "\(live.goodRange.min) - \(live.goodRange.max)")
                                    InfoRow(label: "Relaxed Range", value: "\(live.relaxedRange.min) - \(live.relaxedRange.max)")
                                }
                                .padding(.leading)
                            }
                        }
                    }
                    
                    // Recent Feedback Section
                    GroupBox("Recent Fit Feedback") {
                        ForEach(data.recentFeedback) { feedback in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(feedback.garmentName)
                                    .font(.headline)
                                Text("\(feedback.brand) - Size \(feedback.size)")
                                    .font(.subheadline)
                                Text("Feedback: \(feedback.feedback)")
                                    .foregroundColor(.secondary)
                            }
                            .padding(.vertical, 4)
                            
                            if feedback.id != data.recentFeedback.last?.id {
                                Divider()
                            }
                        }
                    }
                }
            }
            .padding()
        }
        .navigationTitle("Test Dashboard")
        .onAppear(perform: fetchData)
        .onReceive(timer) { _ in
            fetchData() // Refresh data periodically
        }
    }
    
    private func fetchData() {
        Task {
            async let userData = fetchUserTestData()
            async let liveMeasurements = fetchLiveMeasurements()
            
            do {
                let (user, live) = try await (userData, liveMeasurements)
                DispatchQueue.main.async {
                    self.userData = user
                    self.liveMeasurements = live
                    self.isLoading = false
                }
            } catch {
                print("Error fetching data: \(error)")
            }
        }
    }
}

// Helper Views
struct InfoRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .foregroundColor(.secondary)
                .frame(width: 120, alignment: .leading)
            Text(value)
        }
    }
}

// Data Models
struct UserTestData: Decodable {
    let id: Int
    let email: String
    let createdAt: String
    let gender: String
    let unitPreference: String
    let totalGarments: Int
    let lastGarmentInput: String
    let brandsOwned: [String]
    let fitZones: FitZones
    let recentFeedback: [FeedbackItem]
}

struct FitZones: Decodable {
    let tightMin: Double
    let tightMax: Double
    let goodMin: Double
    let goodMax: Double
    let relaxedMin: Double
    let relaxedMax: Double
}

struct FeedbackItem: Identifiable, Decodable {
    let id: Int
    let garmentName: String
    let brand: String
    let size: String
    let feedback: String
}

// Add new model for live measurements
struct LiveFitZones: Decodable {
    struct Range: Decodable {
        let min: Double
        let max: Double
    }
    
    let tightRange: Range
    let goodRange: Range
    let relaxedRange: Range
}

struct LiveMeasurementsResponse: Decodable {
    let Tops: TopsMeasurements
    
    struct TopsMeasurements: Decodable {
        let tightRange: Range
        let goodRange: Range
        let relaxedRange: Range
        
        struct Range: Decodable {
            let min: Double
            let max: Double
        }
    }
}

// API Function
func fetchUserTestData() async throws -> UserTestData {
    let url = URL(string: "http://localhost:8006/test/user/2")!
    let (data, _) = try await URLSession.shared.data(from: url)
    let decoder = JSONDecoder()
    return try decoder.decode(UserTestData.self, from: data)
}

// Add new API function
func fetchLiveMeasurements() async throws -> LiveMeasurementsResponse {
    let url = URL(string: "http://localhost:8006/user/2/measurements")!
    let (data, _) = try await URLSession.shared.data(from: url)
    let decoder = JSONDecoder()
    return try decoder.decode(LiveMeasurementsResponse.self, from: data)
} 