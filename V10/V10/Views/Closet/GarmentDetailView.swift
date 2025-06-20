import SwiftUI

struct GarmentDetailView: View {
    let garment: ClosetGarment
    @Binding var isPresented: Bool
    
    var body: some View {
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
                
                // Fit Feedback
                if let feedback = garment.fitFeedback {
                    Text("Feedback: \(feedback)")
                        .font(.subheadline)
                }
                
                Spacer()
            }
            .padding()
            .navigationBarItems(trailing: Button("Done") {
                isPresented = false
            })
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
            createdAt: "2024-02-18",
            ownsGarment: true,
            productName: "Classic Oxford Shirt"
        ),
        isPresented: .constant(true)
    )
} 