import SwiftUI

struct TryOnFeedbackView: View {
    let session: TryOnSession
    @State private var selectedSize: String = ""
    @State private var fitFeedback: [String: Int] = [:]
    @State private var notes: String = ""
    @State private var isSubmitting = false
    @State private var showConfirmation = false
    @State private var insights: TryOnInsights?
    
    let fitOptions = [
        (1, "Too Tight"),
        (2, "Tight but I Like It"),
        (3, "Good Fit"),
        (4, "Loose but I Like It"),
        (5, "Too Loose")
    ]

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Product Info Header
                ProductInfoHeader(session: session)
                
                // Size Selection
                SizeSelectionView(
                    sizeOptions: session.sizeOptions,
                    selectedSize: $selectedSize
                )
                
                // Feedback Collection
                if !selectedSize.isEmpty {
                    FeedbackCollectionView(
                        measurements: session.availableMeasurements,
                        fitOptions: fitOptions,
                        fitFeedback: $fitFeedback
                    )
                    
                    // Notes Section
                    NotesSection(notes: $notes)
                    
                    // Submit Button
                    SubmitButton(
                        isSubmitting: isSubmitting,
                        onSubmit: submitTryOnFeedback
                    )
                }
                
                // Insights Display
                if let insights = insights {
                    TryOnInsightsCard(insights: insights)
                }
            }
            .padding()
        }
        .navigationTitle("Try-On Feedback")
        .navigationBarTitleDisplayMode(.inline)
        .alert("Try-On Logged!", isPresented: $showConfirmation) {
            Button("OK") {
                // Navigate back or show next steps
            }
        } message: {
            Text("Your feedback has been saved and insights generated.")
        }
    }
    
    private func submitTryOnFeedback() {
        guard !selectedSize.isEmpty else { return }
        
        isSubmitting = true
        
        let requestBody: [String: Any] = [
            "user_id": "1",
            "session_id": session.sessionId,
            "product_url": session.productUrl,
            "brand_id": session.brandId,
            "size_tried": selectedSize,
            "feedback": fitFeedback,
            "notes": notes,
            "try_on_location": "Store"
        ]
        
        guard let url = URL(string: "\(Config.baseURL)/tryon/submit"),
              let jsonData = try? JSONSerialization.data(withJSONObject: requestBody) else {
            isSubmitting = false
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                isSubmitting = false
                
                if let data = data,
                   let response = try? JSONDecoder().decode(TryOnResponse.self, from: data) {
                    self.insights = response.insights
                    self.showConfirmation = true
                }
            }
        }.resume()
    }
}

// MARK: - Supporting Views

struct ProductInfoHeader: View {
    let session: TryOnSession
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(session.brand)
                .font(.caption)
                .foregroundColor(.secondary)
                .textCase(.uppercase)
            
            Text(session.productName)
                .font(.headline)
                .multilineTextAlignment(.leading)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }
}

struct SizeSelectionView: View {
    let sizeOptions: [String]
    @Binding var selectedSize: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("What size did you try on?")
                .font(.headline)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 4), spacing: 12) {
                ForEach(sizeOptions, id: \.self) { size in
                    Button(action: {
                        selectedSize = size
                    }) {
                        Text(size)
                            .font(.headline)
                            .foregroundColor(selectedSize == size ? .white : .primary)
                            .frame(width: 60, height: 40)
                            .background(selectedSize == size ? Color.blue : Color(.systemGray5))
                            .cornerRadius(8)
                    }
                }
            }
        }
    }
}

struct FeedbackCollectionView: View {
    let measurements: [String]
    let fitOptions: [(Int, String)]
    @Binding var fitFeedback: [String: Int]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("How did it fit?")
                .font(.headline)
            
            ForEach(measurements, id: \.self) { measurement in
                VStack(alignment: .leading, spacing: 10) {
                    if measurement == "overall" {
                        Text("How does it fit overall?")
                            .font(.subheadline)
                            .fontWeight(.medium)
                    } else {
                        Text("How does it fit in the \(measurement)?")
                            .font(.subheadline)
                            .fontWeight(.medium)
                    }
                    
                    ForEach(fitOptions, id: \.0) { option in
                        Button(action: {
                            fitFeedback[measurement] = option.0
                        }) {
                            Text(option.1)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(fitFeedback[measurement] == option.0 ? Color.blue.opacity(0.8) : Color.gray.opacity(0.2))
                                .foregroundColor(fitFeedback[measurement] == option.0 ? .white : .black)
                                .cornerRadius(10)
                        }
                    }
                }
                .padding(.vertical, 8)
            }
        }
    }
}

struct NotesSection: View {
    @Binding var notes: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Additional Notes (Optional)")
                .font(.headline)
            
            TextField("Any other observations about the fit...", text: $notes, axis: .vertical)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .lineLimit(3...6)
        }
    }
}

struct SubmitButton: View {
    let isSubmitting: Bool
    let onSubmit: () -> Void
    
    var body: some View {
        Button(action: onSubmit) {
            if isSubmitting {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
            } else {
                Text("Submit Try-On Feedback")
                    .font(.headline)
                    .foregroundColor(.white)
            }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.blue)
        .cornerRadius(10)
        .disabled(isSubmitting)
    }
}

struct TryOnInsightsCard: View {
    let insights: TryOnInsights
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "sparkles")
                    .foregroundColor(.yellow)
                Text("Fit Intelligence")
                    .font(.headline)
                Spacer()
            }
            
            Text(insights.summary)
                .font(.subheadline)
                .foregroundColor(.primary)
            
            if !insights.keyFindings.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Key Findings:")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.secondary)
                    
                    ForEach(insights.keyFindings, id: \.self) { finding in
                        Text("• \(finding)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            if !insights.recommendations.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Recommendations:")
                        .font(.caption)
                        .fontWeight(.medium)
                        .foregroundColor(.secondary)
                    
                    ForEach(insights.recommendations, id: \.self) { recommendation in
                        Text("• \(recommendation)")
                            .font(.caption)
                            .foregroundColor(.blue)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}
