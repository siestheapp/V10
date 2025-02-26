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
                    
                    Text("Chest: \(garment.chestRange)")
                        .font(.subheadline)
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
            chestRange: "41-43",
            fitFeedback: "Good Fit",
            createdAt: "2024-02-18",
            ownsGarment: true,
            productName: "Classic Oxford Shirt"
        ),
        isPresented: .constant(true)
    )
} 