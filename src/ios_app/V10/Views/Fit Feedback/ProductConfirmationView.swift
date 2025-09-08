import SwiftUI

struct ProductConfirmationView: View {
    let session: TryOnSession
    @State private var isConfirming = false
    @State private var navigateToFeedback = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Product Image
                AsyncImage(url: URL(string: session.productImage)) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                } placeholder: {
                    Rectangle()
                        .fill(Color(.systemGray5))
                        .aspectRatio(3/4, contentMode: .fit)
                        .overlay(
                            VStack {
                                Image(systemName: "photo")
                                    .font(.largeTitle)
                                    .foregroundColor(.gray)
                                Text("Loading...")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                        )
                }
                .frame(maxHeight: 400)
                .cornerRadius(12)
                .shadow(radius: 4)
                
                // Product Info
                VStack(alignment: .leading, spacing: 16) {
                    // Brand
                    Text(session.brand)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .textCase(.uppercase)
                        .fontWeight(.medium)
                    
                    // Product Name
                    Text(session.productName)
                        .font(.title2)
                        .fontWeight(.bold)
                        .multilineTextAlignment(.leading)
                    
                    // Available Sizes
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Available Sizes")
                            .font(.headline)
                            .foregroundColor(.primary)
                        
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 6), spacing: 8) {
                            ForEach(session.sizeOptions, id: \.self) { size in
                                Text(size)
                                    .font(.caption)
                                    .fontWeight(.medium)
                                    .foregroundColor(.secondary)
                                    .frame(width: 40, height: 30)
                                    .background(Color(.systemGray6))
                                    .cornerRadius(6)
                            }
                        }
                    }
                    
                    // Confirmation Message
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Is this the item you're trying on?")
                            .font(.headline)
                            .foregroundColor(.primary)
                        
                        Text("We'll ask you about the fit once you confirm this is the right product.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                
                Spacer(minLength: 20)
                
                // Action Buttons
                VStack(spacing: 12) {
                    // Confirm Button
                    Button(action: {
                        isConfirming = true
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                            navigateToFeedback = true
                        }
                    }) {
                        HStack {
                            if isConfirming {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    .scaleEffect(0.8)
                            } else {
                                Image(systemName: "checkmark.circle.fill")
                            }
                            Text("Yes, I'm trying this on")
                                .font(.headline)
                                .fontWeight(.semibold)
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(12)
                    }
                    .disabled(isConfirming)
                    
                    // Cancel Button
                    Button(action: {
                        // Navigate back
                    }) {
                        Text("No, this isn't right")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding()
        }
        .navigationTitle("Confirm Product")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(isPresented: $navigateToFeedback) {
            TryOnFeedbackView(session: session)
        }
    }
}

#Preview {
    NavigationView {
        ProductConfirmationView(session: TryOnSession(
            sessionId: "test_123",
            brand: "J.Crew",
            brandId: 4,
            productName: "Broken-in organic cotton oxford shirt",
            productUrl: "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996",
            productImage: "https://via.placeholder.com/300x400/000000/ffffff?text=J.Crew",
            availableMeasurements: ["overall", "chest", "neck", "sleeve"],
            feedbackOptions: [
                FeedbackOption(value: 1, label: "Too Tight"),
                FeedbackOption(value: 2, label: "Tight but I Like It"),
                FeedbackOption(value: 3, label: "Good Fit"),
                FeedbackOption(value: 4, label: "Loose but I Like It"),
                FeedbackOption(value: 5, label: "Too Loose")
            ],
            sizeOptions: ["XS", "S", "M", "L", "XL", "XXL"],
            nextStep: "size_selection_and_feedback"
        ))
    }
}
