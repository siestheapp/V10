import SwiftUI

struct BrandsView: View {
    @StateObject private var brandStore = BrandStore()
    @State private var selectedBrand: Brand?
    @State private var searchText = ""
    
    var filteredBrands: [Brand] {
        if searchText.isEmpty {
            return brandStore.brands
        }
        return brandStore.brands.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
    }
    
    var body: some View {
        NavigationView {
            List {
                if brandStore.isLoading {
                    ProgressView()
                        .frame(maxWidth: .infinity, alignment: .center)
                } else if let error = brandStore.error {
                    Text("Error: \(error.localizedDescription)")
                        .foregroundColor(.red)
                } else {
                    ForEach(filteredBrands) { brand in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(brand.name)
                                .font(.headline)
                            
                            if !brand.categories.isEmpty {
                                Text("Categories:")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                                HStack {
                                    ForEach(brand.categories, id: \.self) { category in
                                        Text(category)
                                            .font(.caption)
                                            .padding(.horizontal, 8)
                                            .padding(.vertical, 4)
                                            .background(Color.blue.opacity(0.1))
                                            .cornerRadius(8)
                                    }
                                }
                            }
                            
                            if !brand.measurements.isEmpty {
                                Text("Measurements:")
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                                HStack {
                                    ForEach(brand.measurements, id: \.self) { measurement in
                                        Text(measurement.capitalized)
                                            .font(.caption)
                                            .padding(.horizontal, 8)
                                            .padding(.vertical, 4)
                                            .background(Color.green.opacity(0.1))
                                            .cornerRadius(8)
                                    }
                                }
                            }
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
            .navigationTitle("Brands")
            .searchable(text: $searchText, prompt: "Search brands")
            .refreshable {
                brandStore.fetchBrands()
            }
        }
        .onAppear {
            brandStore.fetchBrands()
        }
    }
}

#Preview {
    BrandsView()
} 