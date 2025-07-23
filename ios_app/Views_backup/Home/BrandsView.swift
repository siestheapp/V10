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
        List {
            if brandStore.isLoading {
                HStack {
                    Spacer()
                    ProgressView("Loading brands...")
                    Spacer()
                }
                .listRowBackground(Color.clear)
            } else if let error = brandStore.error {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Error loading brands")
                        .font(.headline)
                        .foregroundColor(.red)
                    Text(error.localizedDescription)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Button("Try Again") {
                        brandStore.fetchBrands()
                    }
                    .padding(.top, 8)
                }
                .padding()
                .listRowBackground(Color(.systemBackground))
            } else if brandStore.brands.isEmpty {
                Text("No brands found")
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .listRowBackground(Color.clear)
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
        .onAppear {
            if brandStore.brands.isEmpty {
                brandStore.fetchBrands()
            }
        }
    }
}

#Preview {
    NavigationView {
        BrandsView()
    }
} 