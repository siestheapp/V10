// TryOnSessionView.swift
// Main modal view for try-on sessions with sequential feedback

import SwiftUI

struct TryOnSessionView: View {
    let garment: Garment
    let productUrl: String
    @Environment(\.dismiss) private var dismiss
    @StateObject private var sessionState = TryOnSessionState()
    @State private var currentStep: TryOnStep = .sizeSelection
    @State private var showingSummary = false
    @State private var sessionId: Int?
    
    enum TryOnStep {
        case sizeSelection
        case dimensionFeedback
        case summary
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                // Background gradient
                LinearGradient(
                    colors: [Color(.systemBackground), Color(.systemGray6)],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()
                
                VStack {
                    // Progress indicator
                    if currentStep == .dimensionFeedback {
                        ProgressView(value: sessionState.progress)
                            .tint(.blue)
                            .padding(.horizontal)
                    }
                    
                    // Main content
                    Group {
                        switch currentStep {
                        case .sizeSelection:
                            SizeSelectionView(
                                garment: garment,
                                selectedSize: $sessionState.selectedSize,
                                onContinue: {
                                    startSession()
                                }
                            )
                        
                        case .dimensionFeedback:
                            if let dimension = sessionState.currentDimension {
                                DimensionFeedbackView(
                                    dimension: dimension,
                                    feedbackValue: Binding(
                                        get: { sessionState.feedbackValues[dimension] },
                                        set: { sessionState.feedbackValues[dimension] = $0 }
                                    ),
                                    onNext: handleNextDimension,
                                    onSkip: {
                                        sessionState.skipCurrentDimension()
                                        handleNextDimension()
                                    },
                                    onPrevious: sessionState.currentDimensionIndex > 0 ? {
                                        sessionState.previousDimension()
                                    } : nil
                                )
                            }
                        
                        case .summary:
                            TryOnSummaryView(
                                garment: garment,
                                sizeTried: sessionState.selectedSize,
                                feedbackSummary: sessionState.getFeedbackSummary(),
                                onTryDifferentSize: {
                                    // Reset for new size
                                    sessionState.reset()
                                    currentStep = .sizeSelection
                                },
                                onBuyThis: {
                                    submitFeedback(finalDecision: "bought", purchaseSize: sessionState.selectedSize)
                                },
                                onTryDifferentItem: {
                                    submitFeedback(finalDecision: "passed")
                                    dismiss()
                                }
                            )
                        }
                    }
                    .padding()
                    
                    Spacer()
                }
            }
            .navigationTitle("Try-On Session")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Save & Exit") {
                        saveAndExit()
                    }
                    .foregroundColor(.blue)
                }
            }
        }
        .interactiveDismissDisabled(false)
        .onDisappear {
            // Auto-save session if dismissed without explicit save
            if currentStep != .sizeSelection && sessionId != nil {
                saveSessionInBackground()
            }
        }
    }
    
    private func startSession() {
        guard !sessionState.selectedSize.isEmpty else { return }
        
        // Create session in database
        createTryOnSession { success in
            if success {
                currentStep = .dimensionFeedback
            }
        }
    }
    
    private func handleNextDimension() {
        if sessionState.isLastDimension {
            // Move to summary
            currentStep = .summary
        } else {
            sessionState.nextDimension()
        }
    }
    
    private func createTryOnSession(completion: @escaping (Bool) -> Void) {
        // TODO: Implement API call to create session
        // For now, mock the session creation
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.sessionId = Int.random(in: 1000...9999)
            completion(true)
        }
    }
    
    private func submitFeedback(finalDecision: String? = nil, purchaseSize: String? = nil) {
        // TODO: Implement API call to submit feedback
        print("Submitting feedback:")
        print("  Session ID: \(sessionId ?? 0)")
        print("  Size: \(sessionState.selectedSize)")
        print("  Feedback: \(sessionState.getFeedbackSummary())")
        print("  Decision: \(finalDecision ?? "pending")")
        
        dismiss()
    }
    
    private func saveAndExit() {
        // Save current progress and exit
        saveSessionInBackground()
        dismiss()
    }
    
    private func saveSessionInBackground() {
        // TODO: Implement background save
        print("Saving session in background...")
    }
}

// MARK: - Size Selection View

struct SizeSelectionView: View {
    let garment: Garment
    @Binding var selectedSize: String
    let onContinue: () -> Void
    
    let sizes = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
    
    var body: some View {
        VStack(spacing: 24) {
            // Product info
            VStack(spacing: 12) {
                Text(garment.brand)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .textCase(.uppercase)
                
                Text(garment.productName)
                    .font(.title2)
                    .fontWeight(.bold)
                    .multilineTextAlignment(.center)
            }
            .padding()
            .frame(maxWidth: .infinity)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(.systemGray6))
            )
            
            // Size selection
            VStack(alignment: .leading, spacing: 16) {
                Text("Select Size to Try On")
                    .font(.headline)
                
                LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 4), spacing: 12) {
                    ForEach(sizes, id: \.self) { size in
                        Button(action: {
                            selectedSize = size
                        }) {
                            Text(size)
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(selectedSize == size ? .white : .primary)
                                .frame(height: 44)
                                .frame(maxWidth: .infinity)
                                .background(
                                    RoundedRectangle(cornerRadius: 8)
                                        .fill(selectedSize == size ? Color.blue : Color(.systemGray5))
                                )
                        }
                    }
                }
            }
            
            Spacer()
            
            // Continue button
            Button(action: onContinue) {
                Text("Start Try-On")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(12)
            }
            .disabled(selectedSize.isEmpty)
            .opacity(selectedSize.isEmpty ? 0.6 : 1.0)
        }
    }
}

// MARK: - Dimension Feedback View

struct DimensionFeedbackView: View {
    let dimension: FitDimension
    @Binding var feedbackValue: Int?
    let onNext: () -> Void
    let onSkip: () -> Void
    let onPrevious: (() -> Void)?
    
    var body: some View {
        VStack(spacing: 32) {
            // Question
            Text(dimension.questionText)
                .font(.title)
                .fontWeight(.bold)
                .multilineTextAlignment(.center)
                .padding(.top, 40)
            
            // Feedback options
            VStack(spacing: 16) {
                ForEach(1...5, id: \.self) { value in
                    FeedbackButton(
                        value: value,
                        isSelected: feedbackValue == value,
                        onTap: {
                            feedbackValue = value
                        }
                    )
                }
            }
            .padding(.horizontal)
            
            Spacer()
            
            // Navigation buttons
            HStack(spacing: 16) {
                if let onPrevious = onPrevious {
                    Button(action: onPrevious) {
                        Text("Back")
                            .font(.headline)
                            .foregroundColor(.blue)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.blue, lineWidth: 2)
                            )
                    }
                }
                
                Button(action: onSkip) {
                    Text("Skip")
                        .font(.headline)
                        .foregroundColor(.gray)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.gray, lineWidth: 1)
                        )
                }
                
                Button(action: onNext) {
                    Text("Next")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(12)
                }
                .disabled(feedbackValue == nil)
                .opacity(feedbackValue == nil ? 0.6 : 1.0)
            }
        }
    }
}

// MARK: - Feedback Button

struct FeedbackButton: View {
    let value: Int
    let isSelected: Bool
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 16) {
                Text(DimensionFeedback.getFeedbackEmoji(for: value))
                    .font(.title2)
                
                Text(DimensionFeedback.getFeedbackText(for: value))
                    .font(.headline)
                    .foregroundColor(isSelected ? .white : .primary)
                
                Spacer()
                
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.white)
                }
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(isSelected ? Color.blue : Color(.systemGray5))
            )
        }
    }
}

// MARK: - Summary View

struct TryOnSummaryView: View {
    let garment: Garment
    let sizeTried: String
    let feedbackSummary: [(dimension: String, feedback: String)]
    let onTryDifferentSize: () -> Void
    let onBuyThis: () -> Void
    let onTryDifferentItem: () -> Void
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header
                Text("Try-On Summary")
                    .font(.title)
                    .fontWeight(.bold)
                
                // Product & Size
                VStack(spacing: 8) {
                    Text(garment.brand)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .textCase(.uppercase)
                    
                    Text(garment.productName)
                        .font(.headline)
                    
                    Text("Size \(sizeTried)")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.blue)
                }
                .padding()
                .frame(maxWidth: .infinity)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(.systemGray6))
                )
                
                // Feedback Summary
                VStack(alignment: .leading, spacing: 12) {
                    Text("Your Feedback")
                        .font(.headline)
                    
                    ForEach(feedbackSummary, id: \.dimension) { item in
                        HStack {
                            Text(item.dimension)
                                .foregroundColor(.secondary)
                            Spacer()
                            Text(item.feedback)
                                .fontWeight(.medium)
                        }
                        .padding(.vertical, 4)
                    }
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(.systemBackground))
                        .shadow(color: .black.opacity(0.05), radius: 2, x: 0, y: 1)
                )
                
                // Action buttons
                VStack(spacing: 12) {
                    Button(action: onBuyThis) {
                        Label("I'm Buying This", systemImage: "bag.fill")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .cornerRadius(12)
                    }
                    
                    Button(action: onTryDifferentSize) {
                        Label("Try Different Size", systemImage: "arrow.triangle.2.circlepath")
                            .font(.headline)
                            .foregroundColor(.blue)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.blue, lineWidth: 2)
                            )
                    }
                    
                    Button(action: onTryDifferentItem) {
                        Text("Try Different Item")
                            .font(.headline)
                            .foregroundColor(.gray)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.gray, lineWidth: 1)
                            )
                    }
                }
                .padding(.top)
            }
            .padding()
        }
    }
}

// MARK: - Preview

struct TryOnSessionView_Previews: PreviewProvider {
    static var previews: some View {
        TryOnSessionView(
            garment: Garment(
                id: 1,
                brand: "J.Crew",
                productName: "Broken-in Organic Cotton Oxford Shirt",
                productUrl: "https://example.com",
                imageUrl: nil,
                category: "Tops",
                sizeLabel: "L",
                ownsGarment: false,
                fitFeedback: nil,
                feedbackTimestamp: nil
            ),
            productUrl: "https://example.com"
        )
    }
}
