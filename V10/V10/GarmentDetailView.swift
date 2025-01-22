import SwiftUI
import SafariServices

struct GarmentDetailView: View {
    let garment: UniqloGarment
    @Environment(\.dismiss) private var dismiss
    @State private var showingWebPage = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Header Image
                if let imageUrl = URL(string: garment.imageUrl) {
                    AsyncImage(url: imageUrl) { phase in
                        switch phase {
                        case .empty:
                            ProgressView()
                                .frame(height: 300)
                        case .success(let image):
                            image
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(height: 300)
                                .clipped()
                                .onTapGesture {
                                    showingWebPage = true
                                }
                        case .failure:
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
                Button {
                    dismiss()
                } label: {
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

#Preview("Garment Detail") {
    NavigationView {
        GarmentDetailView(garment: UniqloGarment(
            id: "1",
            name: "CREW NECK SWEATER",
            size: "L",
            color: "Black",
            price: 49.90
        ))
    }
} 