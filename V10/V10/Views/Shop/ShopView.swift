import SwiftUI

struct ShopView: View {
    @StateObject private var shopViewModel = ShopViewModel()
    @State private var selectedCategory = "Tops"
    @State private var showingFilters = false
    
    let categories = ["Tops", "Bottoms", "Outerwear", "All"]
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Category Filter
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        ForEach(categories, id: \.self) { category in
                            CategoryButton(
                                title: category,
                                isSelected: selectedCategory == category
                            ) {
                                selectedCategory = category
                                shopViewModel.filterByCategory(category)
                            }
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical, 8)
                
                // Shop Feed
                if shopViewModel.isLoading {
                    Spacer()
                    ProgressView("Finding perfect fits for you...")
                        .font(.headline)
                    Spacer()
                } else if let error = shopViewModel.error {
                    Spacer()
                    VStack(spacing: 16) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.orange)
                        Text("Oops! Something went wrong")
                            .font(.headline)
                        Text(error)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                        Button("Try Again") {
                            shopViewModel.loadRecommendations()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .padding()
                    Spacer()
                } else if shopViewModel.recommendations.isEmpty {
                    Spacer()
                    VStack(spacing: 16) {
                        Image(systemName: "bag")
                            .font(.largeTitle)
                            .foregroundColor(.gray)
                        Text("No recommendations yet")
                            .font(.headline)
                        Text("Add some garments to your closet to get personalized recommendations")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                    .padding()
                    Spacer()
                } else {
                    ScrollView {
                        LazyVStack(spacing: 16) {
                            ForEach(shopViewModel.recommendations) { item in
                                ShopItemCard(item: item)
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("Shop")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingFilters = true }) {
                        Image(systemName: "slider.horizontal.3")
                    }
                }
            }
            .sheet(isPresented: $showingFilters) {
                ShopFiltersView()
            }
            .onAppear {
                shopViewModel.loadRecommendations()
            }
        }
    }
}

struct CategoryButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline)
                .fontWeight(.medium)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(isSelected ? Color.blue : Color.gray.opacity(0.1))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(20)
        }
    }
}

struct ShopItemCard: View {
    let item: ShopItem
    @State private var showingDetail = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Product Image
            AsyncImage(url: URL(string: item.imageUrl)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
                    .overlay(
                        Image(systemName: "photo")
                            .font(.largeTitle)
                            .foregroundColor(.gray)
                    )
            }
            .frame(height: 200)
            .clipped()
            .cornerRadius(12)
            
            // Product Info
            VStack(alignment: .leading, spacing: 8) {
                Text(item.brand)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.blue)
                
                Text(item.name)
                    .font(.headline)
                    .lineLimit(2)
                
                HStack {
                    Text("$\(String(format: "%.0f", item.price))")
                        .font(.title3)
                        .fontWeight(.bold)
                    
                    Spacer()
                    
                    // Fit Confidence Badge
                    HStack(spacing: 4) {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text("\(Int(item.fitConfidence * 100))% fit")
                            .font(.caption)
                            .fontWeight(.medium)
                    }
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(8)
                }
                
                // Size Recommendation
                if let recommendedSize = item.recommendedSize {
                    HStack {
                        Text("Recommended: \(recommendedSize)")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        Spacer()
                        Button("View Sizes") {
                            showingDetail = true
                        }
                        .font(.caption)
                        .foregroundColor(.blue)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(16)
        .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
        .onTapGesture {
            showingDetail = true
        }
        .sheet(isPresented: $showingDetail) {
            ShopItemDetailView(item: item)
        }
    }
}

struct ShopFiltersView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var priceRange: ClosedRange<Double> = 0...500
    @State private var selectedBrands: Set<String> = []
    @State private var selectedFitTypes: Set<String> = []
    
    let brands = ["Theory", "Uniqlo", "J.Crew", "Banana Republic", "Patagonia", "Lululemon"]
    let fitTypes = ["Tight", "Regular", "Relaxed"]
    
    var body: some View {
        NavigationView {
            Form {
                Section("Price Range") {
                    VStack {
                        HStack {
                            Text("$\(Int(priceRange.lowerBound))")
                            Spacer()
                            Text("$\(Int(priceRange.upperBound))")
                        }
                        .font(.caption)
                        .foregroundColor(.secondary)
                        
                        Slider(value: $priceRange.lowerBound, in: 0...500)
                        Slider(value: $priceRange.upperBound, in: 0...500)
                    }
                }
                
                Section("Brands") {
                    ForEach(brands, id: \.self) { brand in
                        HStack {
                            Text(brand)
                            Spacer()
                            if selectedBrands.contains(brand) {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.blue)
                            }
                        }
                        .contentShape(Rectangle())
                        .onTapGesture {
                            if selectedBrands.contains(brand) {
                                selectedBrands.remove(brand)
                            } else {
                                selectedBrands.insert(brand)
                            }
                        }
                    }
                }
                
                Section("Fit Preference") {
                    ForEach(fitTypes, id: \.self) { fitType in
                        HStack {
                            Text(fitType)
                            Spacer()
                            if selectedFitTypes.contains(fitType) {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.blue)
                            }
                        }
                        .contentShape(Rectangle())
                        .onTapGesture {
                            if selectedFitTypes.contains(fitType) {
                                selectedFitTypes.remove(fitType)
                            } else {
                                selectedFitTypes.insert(fitType)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Filters")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Apply") {
                        // Apply filters
                        dismiss()
                    }
                }
            }
        }
    }
}

struct ShopItemDetailView: View {
    let item: ShopItem
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Product Image
                    AsyncImage(url: URL(string: item.imageUrl)) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                    } placeholder: {
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .overlay(
                                Image(systemName: "photo")
                                    .font(.largeTitle)
                                    .foregroundColor(.gray)
                            )
                    }
                    .frame(maxHeight: 300)
                    
                    VStack(alignment: .leading, spacing: 16) {
                        // Product Info
                        VStack(alignment: .leading, spacing: 8) {
                            Text(item.brand)
                                .font(.subheadline)
                                .fontWeight(.medium)
                                .foregroundColor(.blue)
                            
                            Text(item.name)
                                .font(.title2)
                                .fontWeight(.bold)
                            
                            Text("$\(String(format: "%.0f", item.price))")
                                .font(.title)
                                .fontWeight(.bold)
                        }
                        
                        // Fit Analysis
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Fit Analysis")
                                .font(.headline)
                            
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text("Confidence")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Text("\(Int(item.fitConfidence * 100))%")
                                        .font(.title2)
                                        .fontWeight(.bold)
                                        .foregroundColor(.green)
                                }
                                
                                Spacer()
                                
                                VStack(alignment: .trailing, spacing: 4) {
                                    Text("Recommended Size")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    Text(item.recommendedSize ?? "N/A")
                                        .font(.title2)
                                        .fontWeight(.bold)
                                }
                            }
                            
                            // Size Chart
                            if let measurements = item.measurements {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Measurements")
                                        .font(.subheadline)
                                        .fontWeight(.medium)
                                    
                                    ForEach(measurements.sorted(by: { $0.key < $1.key }), id: \.key) { measurement in
                                        HStack {
                                            Text(measurement.key.capitalized)
                                                .font(.caption)
                                            Spacer()
                                            Text(measurement.value)
                                                .font(.caption)
                                                .fontWeight(.medium)
                                        }
                                    }
                                }
                                .padding()
                                .background(Color.gray.opacity(0.1))
                                .cornerRadius(8)
                            }
                        }
                        
                        // Action Buttons
                        VStack(spacing: 12) {
                            Button(action: {
                                // Open product URL
                                if let url = URL(string: item.productUrl) {
                                    UIApplication.shared.open(url)
                                }
                            }) {
                                Text("Shop Now")
                                    .font(.headline)
                                    .foregroundColor(.white)
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.blue)
                                    .cornerRadius(12)
                            }
                            
                            Button(action: {
                                // Add to wishlist or save for later
                            }) {
                                Text("Save for Later")
                                    .font(.subheadline)
                                    .foregroundColor(.blue)
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.blue.opacity(0.1))
                                    .cornerRadius(12)
                            }
                        }
                    }
                    .padding()
                }
            }
            .navigationTitle("Product Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    ShopView()
} 