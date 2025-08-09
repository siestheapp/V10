import SwiftUI

struct GarmentFeedbackView: View {
    let garment: ClosetGarment
    @Binding var isPresented: Bool
    var onFeedbackSubmitted: (() -> Void)? = nil
    @State private var selectedFeedback: [String: Int] = [:]
    @State private var selectedGarmentFeedback: [String: Int] = [:]
    @State private var isSubmitting = false
    @State private var showConfirmation = false
    @State private var errorMessage: String?
    @State private var garmentMeasurements: [String: String] = [:]
    
    // Body measurement feedback options (existing)
    let feedbackOptions = [
        (1, "Too Tight"),
        (2, "Tight but I Like It"),
        (3, "Good"),
        (4, "Loose but I Like It"),
        (5, "Too Loose")
    ]
    
    // Garment measurement feedback options (new)
    let garmentFeedbackOptions = [
        "center_back_length": [
            (30, "Too Long"),
            (31, "Too Short"), 
            (32, "Right Length")
        ],
        "shoulder_width": [
            (33, "Too Wide"),
            (34, "Too Narrow"),
            (35, "Right Width")
        ],
        "chest_width": [
            (36, "Too Wide"),
            (37, "Too Narrow"),
            (38, "Right Width")
        ],
        "sleeve_length": [
            (39, "Too Long"),
            (40, "Too Short"),
            (41, "Right Length")
        ]
    ]
    
    // Available measurements for this garment
    private var availableMeasurements: [String] {
        return Array(garment.measurements.keys).sorted()
    }
    
    // Convert feedback text to numeric value
    private func feedbackTextToValue(_ feedbackText: String?) -> Int? {
        guard let text = feedbackText else { return nil }
        
        switch text {
        case "Too Tight": return 1
        case "Tight but I Like It": return 2
        case "Good", "Good Fit": return 3
        case "Loose but I Like It": return 4
        case "Too Loose": return 5
        default: return nil
        }
    }
    
    // Pre-populate existing feedback values
    private func loadExistingFeedback() {
        var existingFeedback: [String: Int] = [:]
        
        // Load overall feedback
        if let overallValue = feedbackTextToValue(garment.fitFeedback) {
            existingFeedback["overall"] = overallValue
        }
        
        // Load dimension-specific feedback
        if let chestValue = feedbackTextToValue(garment.chestFit) {
            existingFeedback["chest"] = chestValue
        }
        
        if let sleeveValue = feedbackTextToValue(garment.sleeveFit) {
            existingFeedback["sleeve"] = sleeveValue
        }
        
        if let neckValue = feedbackTextToValue(garment.neckFit) {
            existingFeedback["neck"] = neckValue
        }
        
        if let waistValue = feedbackTextToValue(garment.waistFit) {
            existingFeedback["waist"] = waistValue
        }
        
        selectedFeedback = existingFeedback
    }
    
    // Fetch garment measurements from the API
    private func loadGarmentMeasurements() {
        let url = URL(string: "\(Config.baseURL)/garment/\(garment.id)/measurements")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                if let data = data,
                   let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let measurements = json["measurements"] as? [String: String] {
                    self.garmentMeasurements = measurements
                }
            }
        }.resume()
    }
    
    // Get display name for garment measurement type
    private func garmentMeasurementDisplayName(_ type: String) -> String {
        switch type {
        case "center_back_length": return "Body Length Back"
        case "shoulder_width": return "Shoulder Width"
        case "chest_width": return "Body Width" 
        case "sleeve_length": return "Sleeve Length"
        default: return type.capitalized
        }
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
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
                    
                    // SECTION 1: Body Measurements Feedback
                    VStack(alignment: .leading, spacing: 16) {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Image(systemName: "person.fill")
                                    .foregroundColor(.blue)
                                Text("Section 1: How does the size fit your body?")
                                    .font(.title3)
                                    .fontWeight(.semibold)
                            }
                            
                            Text("Based on the brand's size guide measurements")
                                .font(.caption)
                                .foregroundColor(.gray)
                                .italic()
                        }
                        .padding(.horizontal)
                        
                        // Overall Feedback
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Overall fit")
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
                        
                        // Body measurements feedback
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
                            .padding(.horizontal)
                        }
                    }
                    .padding(.vertical, 16)
                    .background(Color.blue.opacity(0.05))
                    .cornerRadius(12)
                    .padding(.horizontal)
                    
                    // SECTION 2: Garment Measurements Feedback
                    if !garmentMeasurements.isEmpty {
                        VStack(alignment: .leading, spacing: 16) {
                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    Image(systemName: "ruler.fill")
                                        .foregroundColor(.green)
                                    Text("Section 2: How do you feel about the garment dimensions?")
                                        .font(.title3)
                                        .fontWeight(.semibold)
                                }
                                
                                Text("Based on the actual garment measurements")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                                    .italic()
                            }
                            .padding(.horizontal)
                            
                            // Garment measurements feedback
                            ForEach(Array(garmentMeasurements.keys).sorted(), id: \.self) { measurementType in
                                if let options = garmentFeedbackOptions[measurementType] {
                                    VStack(alignment: .leading, spacing: 12) {
                                        HStack {
                                            Text(garmentMeasurementDisplayName(measurementType))
                                                .font(.headline)
                                            
                                            Spacer()
                                            
                                            if let measurementValue = garmentMeasurements[measurementType] {
                                                Text(measurementValue)
                                                    .font(.caption)
                                                    .foregroundColor(.gray)
                                                    .padding(.horizontal, 8)
                                                    .padding(.vertical, 4)
                                                    .background(Color.gray.opacity(0.1))
                                                    .cornerRadius(4)
                                            }
                                        }
                                        
                                        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 8) {
                                            ForEach(options, id: \.0) { option in
                                                Button(action: {
                                                    selectedGarmentFeedback[measurementType] = option.0
                                                }) {
                                                    Text(option.1)
                                                        .font(.caption)
                                                        .frame(maxWidth: .infinity)
                                                        .padding(.vertical, 12)
                                                        .background(selectedGarmentFeedback[measurementType] == option.0 ? Color.green : Color.gray.opacity(0.2))
                                                        .foregroundColor(selectedGarmentFeedback[measurementType] == option.0 ? .white : .black)
                                                        .cornerRadius(8)
                                                }
                                            }
                                        }
                                    }
                                    .padding(.horizontal)
                                }
                            }
                        }
                        .padding(.vertical, 16)
                        .background(Color.green.opacity(0.05))
                        .cornerRadius(12)
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
                                VStack(spacing: 4) {
                                    Text("Submit Feedback")
                                        .font(.headline)
                                        .foregroundColor(.white)
                                    
                                    let bodyCount = selectedFeedback.count
                                    let garmentCount = selectedGarmentFeedback.count
                                    if bodyCount > 0 || garmentCount > 0 {
                                        Text("Body: \(bodyCount), Garment: \(garmentCount)")
                                            .font(.caption)
                                            .foregroundColor(.white.opacity(0.8))
                                    }
                                }
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background((selectedFeedback.isEmpty && selectedGarmentFeedback.isEmpty) ? Color.gray : Color.blue)
                        .cornerRadius(10)
                        .disabled((selectedFeedback.isEmpty && selectedGarmentFeedback.isEmpty) || isSubmitting)
                    }
                    .padding(.horizontal)
                }
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
                    onFeedbackSubmitted?()
                    isPresented = false
                }
            } message: {
                Text("Your feedback has been saved successfully!")
            }
            .onAppear {
                loadExistingFeedback()
                loadGarmentMeasurements()
            }
        }
    }
    
    private func submitFeedback() {
        guard !selectedFeedback.isEmpty || !selectedGarmentFeedback.isEmpty else { return }
        
        isSubmitting = true
        errorMessage = nil
        
        let url = URL(string: "\(Config.baseURL)/garment/\(garment.id)/feedback")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Combine body and garment feedback
        var combinedFeedback: [String: Int] = selectedFeedback
        
        // Add garment feedback with "garment_" prefix
        for (measurementType, feedbackValue) in selectedGarmentFeedback {
            combinedFeedback["garment_\(measurementType)"] = feedbackValue
        }
        
        let requestBody: [String: Any] = [
            "user_id": Config.defaultUserId,
            "feedback": combinedFeedback
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