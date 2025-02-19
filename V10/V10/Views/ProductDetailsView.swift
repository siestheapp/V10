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

struct SizeDetailView: View {
    let measurements: SizeMeasurements
    
    var body: some View {
        ForEach(Array(measurements.allMeasurements), id: \.key) { key, value in
            MeasurementRow(label: key, value: value)
        }
    }
}

struct ProductDetailsView: View {
    let product: Product
    @Binding var isPresented: Bool
    
    init(product: Product, isPresented: Binding<Bool>, ownsGarment: Bool = true) {
        self.product = product
        self._isPresented = isPresented
    }
    
    func trackProductClick() {
        guard let url = URL(string: "\(Config.baseURL)/track_click") else { return }
        
        let body: [String: Any] = [
            "product_code": product.id,
            "scanned_size": product.scanned_size,
        ]
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { _, _, _ in }.resume()
    }
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Image
                AsyncImage(url: URL(string: product.imageUrl)) { phase in
                    switch phase {
                    case .empty:
                        ProgressView()
                            .frame(height: 300)
                    case .success(let image):
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(height: 300)
                    case .failure(_):
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
                
                // Product details
                VStack(alignment: .leading, spacing: 12) {
                    Text(product.name)
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    if let price = product.price {
                        Text("Price: $\(price, specifier: "%.2f")")
                            .font(.headline)
                    }
                    
                    Text("Category: \(product.category)")
                    if let subcategory = product.subcategory {
                        Text("Subcategory: \(subcategory)")
                    }
                    
                    // Measurements section - only show scanned size
                    if let scannedSize = product.scanned_size,
                       let sizeData = product.measurements.sizes[scannedSize] {
                        Text("Measurements (\(product.measurements.units))")
                            .font(.headline)
                            .padding(.top)
                        
                        VStack(alignment: .leading) {
                            Text("Size \(scannedSize):")
                                .fontWeight(.medium)
                            MeasurementRow(label: "Body Length", value: sizeData.body_length_back)
                            MeasurementRow(label: "Body Width", value: sizeData.body_width)
                            MeasurementRow(label: "Sleeve Length", value: sizeData.sleeve_length)
                            MeasurementRow(label: "Shoulder Width", value: sizeData.shoulder_width)
                        }
                        .padding(.leading)
                        .padding(.vertical, 4)
                    }
                }
                .padding()
                
                // Uniqlo link
                Link(destination: URL(string: product.productUrl)!) {
                    Text("View on Uniqlo")
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