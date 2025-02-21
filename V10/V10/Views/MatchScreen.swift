import SwiftUI

let BASE_URL = "http://127.0.0.1:8005"  // or your actual server URL

struct MatchScreen: View {
    @State private var productLink: String = ""
    @State private var sizeLabel: String = ""
    @State private var measurements: [String] = []
    @State private var feedback: [String: Int] = [:]
    @State private var showingFeedback: Bool = false
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    
    var body: some View {
        VStack {
            // Input Section
            TextField("Product Link", text: $productLink)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding()
            
            TextField("Size", text: $sizeLabel)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding()
            
            if let error = errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .padding()
            }
            
            Button(action: getBrandMeasurements) {
                if isLoading {
                    ProgressView()
                } else {
                    Text("Submit")
                }
            }
            .disabled(productLink.isEmpty || sizeLabel.isEmpty || isLoading)
            .padding()
            
            if showingFeedback {
                ScrollView {
                    // Feedback Section
                    ForEach(measurements, id: \.self) { measurement in
                        VStack(alignment: .leading) {
                            Text("How does it fit in the \(measurement)?")
                                .font(.headline)
                            
                            Picker("Fit", selection: Binding(
                                get: { feedback[measurement] ?? 3 },
                                set: { feedback[measurement] = $0 }
                            )) {
                                Text("Too tight").tag(1)
                                Text("Tight but I like it").tag(2)
                                Text("Good").tag(3)
                                Text("Loose but I like it").tag(4)
                                Text("Too loose").tag(5)
                            }
                            .pickerStyle(SegmentedPickerStyle())
                        }
                        .padding()
                    }
                    
                    Button("Submit Feedback") {
                        submitGarmentWithFeedback()
                    }
                    .padding()
                }
            }
        }
        .padding()
    }
    
    func getBrandMeasurements() {
        isLoading = true
        errorMessage = nil
        
        guard let brandId = extractBrandId(from: productLink) else {
            errorMessage = "Could not determine brand from URL"
            isLoading = false
            return
        }
        
        guard let url = URL(string: "\(BASE_URL)/brands/\(brandId)/measurements") else {
            errorMessage = "Invalid URL"
            isLoading = false
            return
        }
        
        print("Fetching measurements from: \(url.absoluteString)")
        
        var request = URLRequest(url: url)
        request.timeoutInterval = 30
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    print("Network error: \(error)")
                    errorMessage = "Network error: \(error.localizedDescription)"
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    errorMessage = "Invalid response"
                    return
                }
                
                print("HTTP Status: \(httpResponse.statusCode)")
                
                guard httpResponse.statusCode == 200 else {
                    if let data = data, let errorMessage = String(data: data, encoding: .utf8) {
                        print("Server error: \(errorMessage)")
                        self.errorMessage = "Server error: \(errorMessage)"
                    } else {
                        self.errorMessage = "Server error: \(httpResponse.statusCode)"
                    }
                    return
                }
                
                guard let data = data else {
                    errorMessage = "No data received"
                    return
                }
                
                do {
                    print("Raw response: \(String(data: data, encoding: .utf8) ?? "none")")
                    
                    // Add debug decoder
                    let decoder = JSONDecoder()
                    
                    // Try decoding individual fields first
                    let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                    print("Parsed JSON: \(json ?? [:])")
                    print("Keys in response: \(json?.keys.joined(separator: ", ") ?? "")")
                    
                    let response = try decoder.decode(MeasurementsResponse.self, from: data)
                    self.measurements = response.measurements
                    self.showingFeedback = true
                } catch {
                    print("Decode error: \(error)")
                    if let decodingError = error as? DecodingError {
                        switch decodingError {
                        case .keyNotFound(let key, let context):
                            print("Missing key: \(key.stringValue)")
                            print("Context: \(context.debugDescription)")
                            print("Coding path: \(context.codingPath)")
                        default:
                            print("Other decoding error: \(decodingError)")
                        }
                    }
                    errorMessage = "Failed to decode response: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
    
    func submitGarmentWithFeedback() {
        isLoading = true
        errorMessage = nil
        
        guard let url = URL(string: "\(BASE_URL)/garments/submit") else {
            errorMessage = "Invalid URL"
            isLoading = false
            return
        }
        
        let submission = GarmentSubmission(
            productLink: productLink,
            sizeLabel: sizeLabel,
            userId: 1  // Replace with actual user ID
        )
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            let encoder = JSONEncoder()
            request.httpBody = try encoder.encode(submission)
            
            // Debug log
            print("Submitting to URL: \(url.absoluteString)")
            print("Request body: \(String(data: request.httpBody!, encoding: .utf8) ?? "none")")
        } catch {
            errorMessage = "Failed to encode submission: \(error.localizedDescription)"
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isLoading = false
                
                if let error = error {
                    print("Network error: \(error)")
                    errorMessage = error.localizedDescription
                    return
                }
                
                if let httpResponse = response as? HTTPURLResponse {
                    print("HTTP Status: \(httpResponse.statusCode)")
                    
                    if httpResponse.statusCode != 200 {
                        if let data = data, let errorStr = String(data: data, encoding: .utf8) {
                            print("Server error: \(errorStr)")
                            errorMessage = "Server error: \(errorStr)"
                        } else {
                            errorMessage = "Server error: \(httpResponse.statusCode)"
                        }
                        return
                    }
                }
                
                // Reset form on success
                self.productLink = ""
                self.sizeLabel = ""
                self.measurements = []
                self.feedback = [:]
                self.showingFeedback = false
            }
        }.resume()
    }
    
    // Helper function to extract brand ID from product link
    private func extractBrandId(from url: String) -> Int? {
        // This is a simplified example - you'll need to implement proper URL parsing
        // For now, just return 1 for testing
        return 1
    }
}

// Response models
struct MeasurementsResponse: Codable {
    let measurements: [String]
    let feedbackOptions: [FeedbackOption]  // Use camelCase in Swift
    
    enum CodingKeys: String, CodingKey {
        case measurements
        case feedbackOptions  // No mapping needed since names match
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