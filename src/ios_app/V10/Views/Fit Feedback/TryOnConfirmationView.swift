// TryOnConfirmationView.swift
// Handles try-on session confirmation and size selection before feedback.
// Replaces the deleted ProductConfirmationView for TryOnSession flow.

import SwiftUI

struct TryOnConfirmationView: View {
    let session: TryOnSession
    @State private var selectedSize: String = ""
    @State private var navigateToFeedback = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Product Header
                VStack(spacing: 16) {
                    if !session.productImage.isEmpty {
                        AsyncImage(url: URL(string: session.productImage)) { image in
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                        } placeholder: {
                            Rectangle()
                                .fill(Color.gray.opacity(0.3))
                                .aspectRatio(1, contentMode: .fit)
                        }
                        .frame(maxHeight: 200)
                        .cornerRadius(12)
                    }
                    
                    VStack(spacing: 8) {
                        Text(session.brand)
                            .font(.headline)
                            .foregroundColor(.secondary)
                            .textCase(.uppercase)
                        
                        Text(session.productName)
                            .font(.title2)
                            .fontWeight(.bold)
                            .multilineTextAlignment(.center)
                    }
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(.systemGray6))
                )
                
                // Size Selection
                VStack(alignment: .leading, spacing: 16) {
                    Text("Select Your Size")
                        .font(.headline)
                        .fontWeight(.bold)
                    
                    LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 12) {
                        ForEach(session.sizeOptions, id: \.self) { size in
                            Button(action: {
                                print("🔍 Size button tapped: '\(size)'")
                                selectedSize = size
                                print("🔍 Selected size is now: '\(selectedSize)'")
                            }) {
                                Text(size)
                                    .font(.headline)
                                    .foregroundColor(selectedSize == size ? .white : .primary)
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(
                                        RoundedRectangle(cornerRadius: 8)
                                            .fill(selectedSize == size ? Color.blue : Color(.systemGray5))
                                    )
                            }
                        }
                    }
                }
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(.systemBackground))
                        .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
                )
                
                // Available Measurements Info
                if !session.availableMeasurements.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Available Measurements")
                            .font(.headline)
                            .fontWeight(.bold)
                        
                        Text("We can analyze: \(session.availableMeasurements.joined(separator: ", "))")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color(.systemGray6))
                    )
                }
                
                // Next Step Info
                if !session.nextStep.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Next Steps")
                            .font(.headline)
                            .fontWeight(.bold)
                        
                        Text(session.nextStep)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color(.systemGray6))
                    )
                }
                
                Spacer(minLength: 20)
            }
            .padding()
        }
        .navigationTitle("Confirm Try-On")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Continue") {
                    print("🔍 Continue button tapped")
                    print("🔍 Selected size: '\(selectedSize)'")
                    print("🔍 Is empty: \(selectedSize.isEmpty)")
                    navigateToFeedback = true
                }
                .disabled(selectedSize.isEmpty)
                .fontWeight(.semibold)
                .onAppear {
                    print("🔍 Continue button appeared - selectedSize: '\(selectedSize)', isEmpty: \(selectedSize.isEmpty)")
                }
            }
        }
        .sheet(isPresented: $navigateToFeedback) {
            NavigationView {
                FitFeedbackView(
                    feedbackType: .manualEntry,
                    selectedSize: selectedSize,
                    productUrl: session.productUrl,
                    brand: session.brand
                )
            }
        }
        .onAppear {
            print("🔍 TryOnConfirmationView appeared")
            print("🔍 Session size options: \(session.sizeOptions)")
            print("🔍 Available measurements: \(session.availableMeasurements)")
            print("🔍 Selected size: '\(selectedSize)'")
            
            // Auto-select first size if only one option
            if session.sizeOptions.count == 1 {
                selectedSize = session.sizeOptions.first ?? ""
                print("🔍 Auto-selected size: '\(selectedSize)'")
            }
        }
    }
}

#Preview {
    NavigationView {
        TryOnConfirmationView(session: TryOnSession(
            sessionId: "test-123",
            brand: "NN07",
            brandId: 1,
            productName: "Classic Oxford Shirt",
            productUrl: "https://example.com/shirt",
            productImage: "",
            availableMeasurements: ["Chest", "Neck", "Sleeve"],
            feedbackOptions: [],
            sizeOptions: ["S", "M", "L", "XL"],
            nextStep: "Try on the garment and provide feedback on how it fits."
        ))
    }
}
