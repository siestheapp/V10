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
            
            Button(action: submitGarmentWithFeedback) {
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
    
    func submitGarmentWithFeedback() {
        isLoading = true
        errorMessage = nil
        
        // First submit the garment
        guard let submitURL = URL(string: "\(BASE_URL)/garments/submit") else {
            errorMessage = "Invalid URL"
            isLoading = false
            return
        }
        
        var submitRequest = URLRequest(url: submitURL)
        submitRequest.httpMethod = "POST"
        submitRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let submitBody: GarmentSubmission = GarmentSubmission(
            productLink: productLink,
            sizeLabel: sizeLabel,
            userId: 1  // Replace with actual user ID
        )
        
        do {
            submitRequest.httpBody = try JSONEncoder().encode(submitBody)
            
            // Debug log
            print("Submitting to URL: \(submitURL.absoluteString)")
            print("Request body: \(String(data: submitRequest.httpBody!, encoding: .utf8) ?? "none")")
            
            URLSession.shared.dataTask(with: submitRequest) { data, response, error in
                DispatchQueue.main.async {
                    if let error = error {
                        self.errorMessage = error.localizedDescription
                        self.isLoading = false
                        return
                    }
                    
                    guard let httpResponse = response as? HTTPURLResponse else {
                        self.errorMessage = "Invalid response"
                        self.isLoading = false
                        return
                    }
                    
                    if httpResponse.statusCode != 200 {
                        if let data = data, let errorStr = String(data: data, encoding: .utf8) {
                            self.errorMessage = "Server error: \(errorStr)"
                        } else {
                            self.errorMessage = "Server error: \(httpResponse.statusCode)"
                        }
                        self.isLoading = false
                        return
                    }
                    
                    guard let data = data,
                          let submitResponse = try? JSONDecoder().decode(GarmentSubmissionResponse.self, from: data) else {
                        self.errorMessage = "Invalid response data"
                        self.isLoading = false
                        return
                    }
                    
                    // Then fetch measurements using the returned brand_id
                    self.getBrandMeasurements(brandId: submitResponse.brandId)
                }
            }.resume()
            
        } catch {
            errorMessage = "Failed to encode submission: \(error.localizedDescription)"
            isLoading = false
        }
    }
    
    func getBrandMeasurements(brandId: Int) {
        guard let url = URL(string: "\(BASE_URL)/brands/\(brandId)/measurements") else {
            errorMessage = "Invalid URL"
            isLoading = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                self.isLoading = false
                
                if let error = error {
                    self.errorMessage = error.localizedDescription
                    return
                }
                
                guard let data = data else {
                    self.errorMessage = "No data received"
                    return
                }
                
                do {
                    let response = try JSONDecoder().decode(MeasurementsResponse.self, from: data)
                    self.measurements = response.measurements
                    self.showingFeedback = true
                } catch {
                    self.errorMessage = "Failed to decode response: \(error.localizedDescription)"
                }
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

// Add response model for garment submission
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