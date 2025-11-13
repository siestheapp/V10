import SwiftUI

struct GarmentDetailView: View {
    let garment: ClosetGarment
    @Binding var isPresented: Bool
    var onGarmentUpdated: (() -> Void)? = nil  // Add callback
    @State private var showingFeedbackView = false
    
    var body: some View {
        Text("DEBUG: GarmentDetailView")
        NavigationView {
            VStack(alignment: .leading, spacing: 16) {
                // Brand and Product Name
                Group {
                    Text(garment.brand)
                        .font(.title)
                    if let productName = garment.productName {
                        Text(productName)
                            .font(.title2)
                            .foregroundColor(.gray)
                    }
                    Text(garment.category)
                        .font(.headline)
                        .foregroundColor(.gray)
                }
                
                // Size and Measurements
                Group {
                    Text("Size: \(garment.size)")
                        .font(.headline)
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Measurements")
                            .font(.headline)
                        
                        ForEach(Array(garment.measurements.keys.sorted()), id: \.self) { key in
                            if let value = garment.measurements[key], !value.isEmpty {
                                HStack {
                                    Text(key.capitalized)
                                        .font(.subheadline)
                                    Spacer()
                                    Text(value)
                                        .font(.subheadline)
                                }
                            }
                        }
                    }
                }
                
                // Fit Feedback Section
                VStack(alignment: .leading, spacing: 8) {
                    Text("Fit Feedback")
                        .font(.headline)
                    
                    if let feedback = garment.fitFeedback {
                        Text("Overall: \(feedback)")
                            .font(.subheadline)
                            .foregroundColor(.blue)
                    } else {
                        Text("No feedback yet")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    if let chest = garment.chestFit, !chest.isEmpty {
                        Text("Chest: \(chest)")
                            .font(.subheadline)
                    }
                    if let sleeve = garment.sleeveFit, !sleeve.isEmpty {
                        Text("Sleeve: \(sleeve)")
                            .font(.subheadline)
                    }
                    if let neck = garment.neckFit, !neck.isEmpty {
                        Text("Neck: \(neck)")
                            .font(.subheadline)
                    }
                    if let waist = garment.waistFit, !waist.isEmpty {
                        Text("Waist: \(waist)")
                            .font(.subheadline)
                    }
                    Button(action: {
                        showingFeedbackView = true
                    }) {
                        HStack {
                            Image(systemName: "square.and.pencil")
                            Text(garment.fitFeedback == nil ? "Add Feedback" : "Update Feedback")
                        }
                        .font(.subheadline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(8)
                    }
                }
                
                Spacer()
            }
            .padding()
            .navigationBarItems(trailing: Button("Done") {
                isPresented = false
            })
            .sheet(isPresented: $showingFeedbackView) {
                GarmentFeedbackView(
                    garment: garment,
                    isPresented: $showingFeedbackView,
                    onFeedbackSubmitted: {
                        // Call the callback to refresh parent view
                        onGarmentUpdated?()
                    }
                )
            }
        }
    }
}

#Preview {
    GarmentDetailView(
        garment: ClosetGarment(
            id: 1,
            brand: "J.Crew",
            category: "Tops",
            size: "L",
            measurements: [
                "chest": "41-43",
                "sleeve": "34-35",
                "waist": "32-34"
            ],
            fitFeedback: "Good Fit",
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