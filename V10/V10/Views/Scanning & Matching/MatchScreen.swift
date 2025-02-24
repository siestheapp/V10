import SwiftUI

let BASE_URL = "http://127.0.0.1:8005"  // Replace with your actual server URL

struct MatchScreen: View {
    @EnvironmentObject var userSettings: UserSettings
    @State private var productLink: String = ""
    @State private var sizeLabel: String = "M"
    @State private var measurements: [String] = []
    @State private var feedback: [String: Int] = [:]
    @State private var showingFeedback: Bool = false
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @State private var showError: Bool = false
    
    let sizeOptions = ["XS", "S", "M", "L", "XL", "XXL"]
    
    var body: some View {
        VStack {
            VStack(alignment: .leading) {
                Text("Paste Product Link")
                    .font(.headline)
                TextField("e.g., https://store.com/product", text: $productLink)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .keyboardType(.URL)
                    .autocapitalization(.none)
            }
            .padding()
            
            VStack(alignment: .leading) {
                Text("Select Your Size")
                    .font(.headline)
                Picker("Size", selection: $sizeLabel) {
                    ForEach(sizeOptions, id: \.self) { size in
                        Text(size).tag(size)
                    }
                }
                .pickerStyle(MenuPickerStyle())
            }
            .padding()
            
            Button(action: {
                Task {
                    await submitGarmentWithFeedback()
                }
            }) {
                if isLoading {
                    ProgressView()
                } else {
                    Text("Submit")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
            }
            .disabled(productLink.isEmpty || isLoading)
            .padding()
            
            if showingFeedback {
                fitFeedbackSection
            }
        }
        .padding()
        .overlay(
            Group {
                if showError {
                    Text(errorMessage ?? "Unknown error")
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.red)
                        .cornerRadius(8)
                        .transition(.move(edge: .top))
                        .padding(.top, 10)
                }
            },
            alignment: .top
        )
        .animation(.easeInOut, value: showError)
    }
    
    private var fitFeedbackSection: some View {
        ScrollView {
            VStack(alignment: .leading) {
                Text("Fit Feedback")
                    .font(.title2)
                    .bold()
                    .padding(.bottom, 5)
                
                ForEach(measurements, id: \.self) { measurement in
                    VStack(alignment: .leading) {
                        Text("How does it fit in the \(measurement)?")
                            .font(.headline)
                        
                        HStack {
                            feedbackButton(label: "😣 Too Tight", value: 1, measurement: measurement)
                            feedbackButton(label: "👍 Tight but Good", value: 2, measurement: measurement)
                            feedbackButton(label: "👌 Perfect Fit", value: 3, measurement: measurement)
                            feedbackButton(label: "😏 Loose but Good", value: 4, measurement: measurement)
                            feedbackButton(label: "😅 Too Loose", value: 5, measurement: measurement)
                        }
                    }
                    .padding(.vertical, 8)
                }
                
                Button("Submit Feedback") {
                    Task {
                        await submitGarmentWithFeedback()
                    }
                }
                .padding()
            }
        }
        .padding()
    }
    
    private func feedbackButton(label: String, value: Int, measurement: String) -> some View {
        Button(action: { feedback[measurement] = value }) {
            Text(label)
                .frame(maxWidth: .infinity)
                .padding()
                .background(feedback[measurement] == value ? Color.blue.opacity(0.7) : Color.gray.opacity(0.2))
                .foregroundColor(.black)
                .cornerRadius(10)
        }
    }
    
    func submitGarmentWithFeedback() async {
        isLoading = true
        errorMessage = nil
        showError = false
        
        guard let submitURL = URL(string: "\(BASE_URL)/garments/submit") else {
            showError("Invalid URL")
            return
        }
        
        let submitBody = GarmentSubmission(
            productLink: productLink,
            sizeLabel: sizeLabel,
            userId: 1 // Replace with actual user ID
        )
        
        do {
            var request = URLRequest(url: submitURL)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONEncoder().encode(submitBody)
            
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                showError("Server error: \(String(data: data, encoding: .utf8) ?? "Unknown")")
                return
            }
            
            let submitResponse = try JSONDecoder().decode(GarmentSubmissionResponse.self, from: data)
            await getBrandMeasurements(brandId: submitResponse.brandId)
        } catch {
            showError("Submission failed: \(error.localizedDescription)")
        }
        
        isLoading = false
    }
    
    func getBrandMeasurements(brandId: Int) async {
        guard let url = URL(string: "\(BASE_URL)/brands/\(brandId)/measurements") else {
            showError("Invalid URL")
            return
        }
        
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            let response = try JSONDecoder().decode(MeasurementsResponse.self, from: data)
            await MainActor.run {
                self.measurements = response.measurements
                self.showingFeedback = true
            }
        } catch {
            showError("Failed to fetch measurements: \(error.localizedDescription)")
        }
    }
    
    func showError(_ message: String) {
        errorMessage = message
        showError = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            self.showError = false
        }
        isLoading = false
    }
}

struct MeasurementsResponse: Codable {
    let measurements: [String]
    let feedbackOptions: [FeedbackOption]
    
    enum CodingKeys: String, CodingKey {
        case measurements
        case feedbackOptions
    }
}

struct FeedbackOption: Codable {
    let value: Int
    let label: String
}

struct GarmentSubmission: Codable {
    let productLink: String
    let sizeLabel: String
    let userId: Int
}

struct GarmentSubmissionResponse: Codable {
    let garmentId: Int
    let brandId: Int
    let status: String
    
    enum CodingKeys: String, CodingKey {
        case garmentId = "garment_id"
        case brandId = "brand_id"
        case status
    }
}

class UserSettings: ObservableObject {
    @Published var useMetricSystem: Bool {
        didSet {
            UserDefaults.standard.set(useMetricSystem, forKey: "useMetricSystem")
        }
    }
    
    init() {
        self.useMetricSystem = UserDefaults.standard.bool(forKey: "useMetricSystem")
    }
} 