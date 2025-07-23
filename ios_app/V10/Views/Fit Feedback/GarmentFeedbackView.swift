import SwiftUI

struct GarmentFeedbackView: View {
    let garment: ClosetGarment
    @Binding var isPresented: Bool
    @State private var selectedFeedback: [String: Int] = [:]
    @State private var isSubmitting = false
    @State private var showConfirmation = false
    @State private var errorMessage: String?
    
    let feedbackOptions = [
        (1, "Too Tight"),
        (2, "Tight but I Like It"),
        (3, "Good"),
        (4, "Loose but I Like It"),
        (5, "Too Loose")
    ]
    
    // Available measurements for this garment
    private var availableMeasurements: [String] {
        return Array(garment.measurements.keys).sorted()
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Garment Info Header
                VStack(alignment: .leading, spacing: 8) {
                    Text(garment.brand)
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    if let productName = garment.productName {
                        Text(productName)
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    
                    Text("Size: \(garment.size)")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal)
                
                // Overall Feedback Selection
                VStack(alignment: .leading, spacing: 12) {
                    Text("How does this garment fit overall?")
                        .font(.headline)
                    LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                        ForEach(feedbackOptions, id: \.0) { option in
                            Button(action: {
                                selectedFeedback["overall"] = option.0
                            }) {
                                Text(option.1)
                                    .font(.caption)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 12)
                                    .background(selectedFeedback["overall"] == option.0 ? Color.blue : Color.gray.opacity(0.2))
                                    .foregroundColor(selectedFeedback["overall"] == option.0 ? .white : .black)
                                    .cornerRadius(8)
                            }
                        }
                    }
                }
                .padding(.horizontal)
                
                // Feedback Selection
                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        ForEach(availableMeasurements, id: \.self) { measurement in
                            VStack(alignment: .leading, spacing: 12) {
                                HStack {
                                    Text("How does it fit in the \(measurement)?")
                                        .font(.headline)
                                    
                                    Spacer()
                                    
                                    if let measurementValue = garment.measurements[measurement] {
                                        Text(measurementValue)
                                            .font(.caption)
                                            .foregroundColor(.gray)
                                            .padding(.horizontal, 8)
                                            .padding(.vertical, 4)
                                            .background(Color.gray.opacity(0.1))
                                            .cornerRadius(4)
                                    }
                                }
                                
                                LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                                    ForEach(feedbackOptions, id: \.0) { option in
                                        Button(action: {
                                            selectedFeedback[measurement] = option.0
                                        }) {
                                            Text(option.1)
                                                .font(.caption)
                                                .frame(maxWidth: .infinity)
                                                .padding(.vertical, 12)
                                                .background(selectedFeedback[measurement] == option.0 ? Color.blue : Color.gray.opacity(0.2))
                                                .foregroundColor(selectedFeedback[measurement] == option.0 ? .white : .black)
                                                .cornerRadius(8)
                                        }
                                    }
                                }
                            }
                            .padding(.vertical, 8)
                        }
                    }
                    .padding(.horizontal)
                }
                
                // Submit Button
                VStack(spacing: 12) {
                    if let errorMessage = errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                    
                    Button(action: submitFeedback) {
                        if isSubmitting {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Text("Submit Feedback")
                                .font(.headline)
                                .foregroundColor(.white)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(selectedFeedback.isEmpty ? Color.gray : Color.blue)
                    .cornerRadius(10)
                    .disabled(selectedFeedback.isEmpty || isSubmitting)
                }
                .padding(.horizontal)
                
                Spacer()
            }
            .navigationTitle("Fit Feedback")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        isPresented = false
                    }
                }
            }
            .alert("Feedback Submitted", isPresented: $showConfirmation) {
                Button("OK") {
                    isPresented = false
                }
            } message: {
                Text("Your feedback has been saved successfully!")
            }
        }
    }
    
    private func submitFeedback() {
        guard !selectedFeedback.isEmpty else { return }
        
        isSubmitting = true
        errorMessage = nil
        
        let url = URL(string: "\(Config.baseURL)/garment/\(garment.id)/feedback")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody: [String: Any] = [
            "user_id": Config.defaultUserId,
            "feedback": selectedFeedback
        ]
        
        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        } catch {
            errorMessage = "Error preparing request: \(error.localizedDescription)"
            isSubmitting = false
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isSubmitting = false
                
                if let error = error {
                    errorMessage = "Network error: \(error.localizedDescription)"
                    return
                }
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    errorMessage = "Invalid response"
                    return
                }
                
                if httpResponse.statusCode == 200 {
                    showConfirmation = true
                } else {
                    if let data = data, let errorString = String(data: data, encoding: .utf8) {
                        errorMessage = "Server error: \(errorString)"
                    } else {
                        errorMessage = "Server error: \(httpResponse.statusCode)"
                    }
                }
            }
        }.resume()
    }
}

#Preview {
    GarmentFeedbackView(
        garment: ClosetGarment(
            id: 1,
            brand: "Banana Republic",
            category: "Tops",
            size: "M",
            measurements: [
                "chest": "40-42",
                "sleeve": "33-34",
                "waist": "32-34"
            ],
            fitFeedback: nil,
            chestFit: nil,
            sleeveFit: nil,
            neckFit: nil,
            waistFit: nil,
            createdAt: "2024-02-18",
            ownsGarment: true,
            productName: "Classic Oxford Shirt",
            imageUrl: nil,
            productUrl: nil
        ),
        isPresented: .constant(true)
    )
} 