import SwiftUI
import SafariServices

struct GarmentDetailView: View {
    let garment: UniqloGarment
    @Environment(\.dismiss) private var dismiss
    @State private var showingWebPage = false
    
    init(garment: UniqloGarment) {
        self.garment = garment
    }
    
    var body: some View {
        ScrollView(.vertical, showsIndicators: true) {
            VStack(spacing: 20) {
                // Header Image
                if let imageUrl = URL(string: garment.imageUrl) {
                    print("Attempting to load image from: \(garment.imageUrl)")
                    AsyncImage(url: imageUrl) { phase in
                        switch phase {
                        case .empty:
                            print("Loading image...")
                            ProgressView()
                                .frame(height: 300)
                        case .success(let image):
                            print("Image loaded successfully")
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(height: 300)
                                .clipped()
                                .onTapGesture {
                                    showingWebPage = true
                                }
                        case .failure(let error):
                            print("Image loading failed: \(error.localizedDescription)")
                            Image(systemName: "photo")
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(height: 300)
                                .foregroundColor(.gray)
                        @unknown default:
                            EmptyView()
                        }
                    }
                    .cornerRadius(12)
                    .shadow(radius: 5)
                } else {
                    print("Invalid image URL: \(garment.imageUrl)")
                }
                
                // Product Info
                VStack(alignment: .leading, spacing: 16) {
                    // Title and Price Section
                    HStack {
                        VStack(alignment: .leading) {
                            Text(garment.name)
                                .font(.title2)
                                .fontWeight(.bold)
                            
                            Text(garment.brand)
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                        }
                        
                        Spacer()
                        
                        Text("$\(String(format: "%.2f", garment.price))")
                            .font(.title3)
                            .fontWeight(.semibold)
                    }
                    
                    Divider()
                    
                    // Details Grid
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 16) {
                        DetailItem(title: "Size", value: garment.size)
                        DetailItem(title: "Color", value: garment.color)
                        DetailItem(title: "Category", value: garment.category)
                        DetailItem(title: "Subcategory", value: garment.subcategory)
                    }
                    
                    Divider()
                    
                    // Product Link Button
                    if let url = URL(string: garment.productUrl) {
                        Link(destination: url) {
                            HStack {
                                Text("View on UNIQLO")
                                Spacer()
                                Image(systemName: "arrow.up.right.square")
                            }
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                    }
                }
                .padding()
            }
            .padding()
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: {
                    dismiss()
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                }
            }
        }
        .sheet(isPresented: $showingWebPage) {
            if let url = URL(string: garment.productUrl) {
                SafariView(url: url)
            }
        }
    }
}

// Helper Views
struct DetailItem: View {
    let title: String
    let value: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.body)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

// Safari View Controller wrapper
struct SafariView: UIViewControllerRepresentable {
    let url: URL
    
    func makeUIViewController(context: Context) -> SFSafariViewController {
        return SFSafariViewController(url: url)
    }
    
    func updateUIViewController(_ uiViewController: SFSafariViewController, context: Context) {}
}

// Update the preview provider
struct GarmentDetailView_Previews: PreviewProvider {
    static var previews: some View {
        NavigationView {  // Keep this for preview
            GarmentDetailView(garment: UniqloGarment(
                id: "123456",
                name: "Test Garment",
                brand: "UNIQLO",
                size: "L",
                category: "Sweaters",
                subcategory: "Crew Neck",
                color: "Black",
                price: 49.90,
                imageUrl: "https://example.com/image.jpg",
                productUrl: "https://example.com/product"
            ))
        }
    }
} 