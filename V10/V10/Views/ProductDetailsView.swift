import SwiftUI

struct MeasurementRow: View {
    let label: String
    let value: String?
    
    var body: some View {
        if let value = value {
            HStack {
                Text(label.capitalized.replacingOccurrences(of: "_", with: " "))
                Spacer()
                Text(value)
            }
        }
    }
}

struct ProductDetailsView: View {
    let product: Product
    @Binding var isPresented: Bool
    
    init(product: Product, isPresented: Binding<Bool>) {
        self.product = product
        self._isPresented = isPresented
    }
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Product Image
                if let imageUrl = product.imageUrl,
                   let url = URL(string: imageUrl) {
                    AsyncImage(url: url) { phase in
                        switch phase {
                        case .empty:
                            ProgressView()
                                .frame(height: 300)
                        case .success(let image):
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(height: 300)
                        case .failure:
                            Color.gray
                                .frame(height: 300)
                                .overlay(
                                    Image(systemName: "photo")
                                        .foregroundColor(.white)
                                )
                        @unknown default:
                            EmptyView()
                        }
                    }
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .padding(.horizontal)
                }
                
                // Product details
                VStack(alignment: .leading, spacing: 12) {
                    Text(product.name)
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("Price: $\(product.price, specifier: "%.2f")")
                        .font(.headline)
                    
                    Text("Brand: \(product.brand)")
                    Text("Size: \(product.size)")
                    
                    // Measurements section
                    Text("Measurements")
                        .font(.headline)
                        .padding(.top)
                    
                    VStack(alignment: .leading) {
                        if let chest = product.measurements.chest {
                            MeasurementRow(label: "Chest", value: chest)
                        }
                        if let length = product.measurements.length {
                            MeasurementRow(label: "Length", value: length)
                        }
                        if let sleeve = product.measurements.sleeve {
                            MeasurementRow(label: "Sleeve", value: sleeve)
                        }
                    }
                    .padding(.leading)
                    .padding(.vertical, 4)
                }
                .padding()
                
                if let url = product.productUrl {
                    Link(destination: URL(string: url)!) {
                        Text("View on \(product.brand)")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                    }
                    .padding()
                }
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .navigationTitle("Product Details")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Done") {
                    isPresented = false
                }
            }
        }
    }
} 