// FitFeedbackView.swift
// Handles user fit feedback for different scenarios.
// - Supports multiple use cases (manual entry, scanned garments, new brand).
// - Dynamically adjusts UI based on the `feedbackType` passed to it.

import SwiftUI

enum FeedbackType {
    case manualEntry      // When a user pastes a link & selects a size
    case scannedGarment   // When a garment is scanned
    case newBrand         // When a brand is missing from our Fit Zones
    case specialFit       // For cases like stretchy fabric vs. rigid fit
}

struct FitFeedbackView: View {
    let feedbackType: FeedbackType
    let selectedSize: String
    let productUrl: String?
    let brand: String?
    
    @State private var fitFeedback: [String: Int] = [:]
    @State private var isSubmitting = false
    @State private var showConfirmation = false
    
    // Initializers to support both old and new flows
    init(feedbackType: FeedbackType, selectedSize: String) {
        self.feedbackType = feedbackType
        self.selectedSize = selectedSize
        self.productUrl = nil
        self.brand = nil
    }
    
    init(feedbackType: FeedbackType, selectedSize: String, productUrl: String?, brand: String?) {
        self.feedbackType = feedbackType
        self.selectedSize = selectedSize
        self.productUrl = productUrl
        self.brand = brand
    }

    let fitOptions = [
        (1, "Too Tight"),
        (2, "Tight but I Like It"),
        (3, "Great Fit"),
        (4, "Loose but I Like It"),
        (5, "Too Loose")
    ]

    var body: some View {
        VStack(spacing: 20) {
            Text("Fit Feedback")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            // Description based on feedbackType
            Text(feedbackDescription)
                .font(.subheadline)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 30)

            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    ForEach(getMeasurementsForFeedbackType(), id: \.self) { measurement in
                        VStack(alignment: .leading, spacing: 10) {
                            Text("How does it fit in the \(measurement)?")
                                .font(.headline)

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
            .padding(.horizontal, 20)
            
            Button(action: submitFeedback) {
                if isSubmitting {
                    ProgressView()
                } else {
                    Text("Submit Feedback")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(10)
                }
            }
            .padding(.horizontal, 40)
            .disabled(isSubmitting)
            .alert("Feedback Submitted", isPresented: $showConfirmation) {
                Button("OK", role: .cancel) { }
            }
        }
        .padding(.top, 20)
    }
    
    /// Returns a description based on the `feedbackType`
    private var feedbackDescription: String {
        switch feedbackType {
        case .manualEntry:
            return "Based on your selected size (\(selectedSize)), tell us how this garment fits."
        case .scannedGarment:
            return "We scanned your tag! Let us know how this garment fits to improve recommendations."
        case .newBrand:
            return "This is a new brand for us! Your feedback will help us improve future suggestions."
        case .specialFit:
            return "Some fabrics fit differently. Help us refine fit accuracy for stretch vs. rigid fabrics."
        }
    }

    /// Returns different measurement questions depending on `feedbackType`
    private func getMeasurementsForFeedbackType() -> [String] {
        switch feedbackType {
        case .manualEntry:
            return ["Chest", "Waist", "Sleeve"]
        case .scannedGarment:
            return ["Chest", "Waist", "Sleeve", "Neck"]
        case .newBrand:
            return ["Chest", "Waist", "Sleeve", "Shoulders"]
        case .specialFit:
            return ["Chest", "Waist", "Hip", "Stretch Comfort"]
        }
    }
    
    /// Handles feedback submission
    private func submitFeedback() {
        isSubmitting = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            isSubmitting = false
            showConfirmation = true
        }
    }
}

/// Fit Feedback Button Component
struct FitFeedbackButton: View {
    let label: String
    let value: Int
    let measurement: String
    @Binding var selectedValue: Int

    var body: some View {
        Button(action: {
            selectedValue = value
        }) {
            Text(label)
                .frame(maxWidth: .infinity)
                .padding()
                .background(selectedValue == value ? Color.blue.opacity(0.8) : Color.gray.opacity(0.2))
                .foregroundColor(selectedValue == value ? .white : .black)
                .cornerRadius(10)
        }
    }
}
