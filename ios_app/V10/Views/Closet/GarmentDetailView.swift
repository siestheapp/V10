import SwiftUI
import SafariServices

struct GarmentDetailView: View {
    let garment: ClosetGarment
    @Binding var isPresented: Bool
    @State private var showingFeedbackView = false
    @State private var showingSafari = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Product Image
                    if let imageUrl = garment.imageUrl, let url = URL(string: imageUrl) {
                        AsyncImage(url: url) { phase in
                            switch phase {
                            case .empty:
                                ProgressView()
                                    .frame(height: 300)
                            case .success(let image):
                                image
                                    .resizable()
                                    .aspectRatio(contentMode: .fit)
                                    .frame(maxHeight: 300)
                                    .onTapGesture {
                                        if garment.productUrl != nil {
                                            showingSafari = true
                                        }
                                    }
                            case .failure:
                                Rectangle()
                                    .fill(Color.gray.opacity(0.3))
                                    .frame(height: 200)
                                    .overlay(
                                        Image(systemName: "photo")
                                            .foregroundColor(.gray)
                                    )
                            @unknown default:
                                EmptyView()
                            }
                        }
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
                        )
                        .padding(.horizontal)
                        
                        // Click indicator if product URL exists
                        if garment.productUrl != nil {
                            HStack {
                                Image(systemName: "arrow.up.right.square")
                                    .foregroundColor(.blue)
                                Text("Tap image to view product")
                                    .font(.caption)
                                    .foregroundColor(.blue)
                            }
                            .padding(.horizontal)
                        }
                    }
                    
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
                    .padding(.horizontal)
                    
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
                    .padding(.horizontal)
                    
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
                    .padding(.horizontal)
                    
                    Spacer()
                }
            }
            .navigationBarItems(trailing: Button("Done") {
                isPresented = false
            })
            .sheet(isPresented: $showingFeedbackView) {
                GarmentFeedbackView(
                    garment: garment,
                    isPresented: $showingFeedbackView
                )
            }
            .sheet(isPresented: $showingSafari) {
                if let productUrl = garment.productUrl, let url = URL(string: productUrl) {
                    SafariView(url: url)
                }
            }
        }
    }
}

struct SafariView: UIViewControllerRepresentable {
    let url: URL
    
    func makeUIViewController(context: Context) -> SFSafariViewController {
        return SFSafariViewController(url: url)
    }
    
    func updateUIViewController(_ uiViewController: SFSafariViewController, context: Context) {
        // No updates needed
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