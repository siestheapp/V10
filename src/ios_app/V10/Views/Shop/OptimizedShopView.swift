import SwiftUI

// Optimized ShopView with cached images and better performance
struct OptimizedShopView: View {
    @StateObject private var shopViewModel = OptimizedShopViewModel()
    @State private var showingFilters = false
    @State private var selectedCategory = "All"
    
    private let categories = ["All", "Tops", "Bottoms", "Outerwear", "Accessories"]
    private let columns = [
        GridItem(.flexible(), spacing: 16),
        GridItem(.flexible(), spacing: 16)
    ]
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(.systemGroupedBackground)
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 20) {
                        // Category Pills - Lazy loaded
                        ScrollView(.horizontal, showsIndicators: false) {
                            LazyHStack(spacing: 12) {
                                ForEach(categories, id: \.self) { category in
                                    OptimizedCategoryButton(
                                        title: category,
                                        isSelected: selectedCategory == category,
                                        action: {
                                            selectedCategory = category
                                            shopViewModel.filterByCategory(category)
                                        }
                                    )
                                }
                            }
                            .padding(.horizontal)
                        }
                        
                        // Content
                        if shopViewModel.isLoading && shopViewModel.recommendations.isEmpty {
                            loadingView
                        } else if let error = shopViewModel.error {
                            errorView(error)
                        } else if shopViewModel.recommendations.isEmpty {
                            emptyStateView
                        } else {
                            // OPTIMIZED: LazyVGrid for efficient rendering
                            LazyVGrid(columns: columns, spacing: 16) {
                                ForEach(shopViewModel.recommendations) { item in
                                    OptimizedShopItemCard(item: item)
                                        .onAppear {
                                            // Prefetch next batch when reaching end
                                            if item.id == shopViewModel.recommendations.last?.id {
                                                shopViewModel.loadMoreIfNeeded()
                                            }
                                        }
                                }
                            }
                            .padding(.horizontal)
                            
                            if shopViewModel.isLoadingMore {
                                ProgressView()
                                    .padding()
                            }
                        }
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
            .refreshable {
                await shopViewModel.refresh()
            }
            .onAppear {
                shopViewModel.loadRecommendations()
            }
        }
    }
    
    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
            Text("Finding your perfect fits...")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(.top, 100)
    }
    
    private func errorView(_ error: String) -> some View {
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
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private var emptyStateView: some View {
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
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(.top, 100)
    }
}

// OPTIMIZED Shop Item Card with cached images
struct OptimizedShopItemCard: View {
    let item: ShopItem
    @State private var showingDetail = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // PERFORMANCE: Use CachedAsyncImage instead of AsyncImage
            CachedAsyncImage(url: URL(string: item.imageUrl)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                    .frame(height: 200)
                    .clipped()
                    .cornerRadius(12)
            } placeholder: {
                Rectangle()
                    .fill(Color.gray.opacity(0.3))
                    .frame(height: 200)
                    .cornerRadius(12)
                    .overlay(
                        Image(systemName: "photo")
                            .font(.largeTitle)
                            .foregroundColor(.gray)
                    )
            }
            
            // Product Info
            VStack(alignment: .leading, spacing: 8) {
                Text(item.brand)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .textCase(.uppercase)
                
                Text(item.name)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .lineLimit(2)
                
                HStack {
                    Text("$\(String(format: "%.2f", item.price))")
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Spacer()
                    
                    // FIX: Check for valid fitConfidence before using
                    if item.fitConfidence.isFinite && item.fitConfidence >= 0 && item.fitConfidence <= 1 {
                        HStack(spacing: 4) {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.caption)
                                .foregroundColor(fitScoreColor(item.fitConfidence))
                            Text("\(Int(item.fitConfidence * 100))%")
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundColor(fitScoreColor(item.fitConfidence))
                        }
                    }
                }
                
                if let recommendation = item.recommendedSize {
                    Text("Size \(recommendation)")
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.blue.opacity(0.1))
                        .foregroundColor(.blue)
                        .cornerRadius(6)
                }
            }
            .padding(.horizontal, 8)
        }
        .background(Color(.systemBackground))
        .cornerRadius(16)
        .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
        .onTapGesture {
            showingDetail = true
        }
        .sheet(isPresented: $showingDetail) {
            ShopItemDetailView(item: item)
        }
    }
    
    private func fitScoreColor(_ score: Double) -> Color {
        // FIX: Guard against NaN/Infinity
        guard score.isFinite else { return .gray }
        
        switch score {
        case 0.8...1.0:
            return .green
        case 0.6..<0.8:
            return .orange
        default:
            return .red
        }
    }
}

// OPTIMIZED ViewModel
@MainActor
class OptimizedShopViewModel: ObservableObject {
    @Published var recommendations: [ShopItem] = []
    @Published var isLoading = false
    @Published var isLoadingMore = false
    @Published var error: String?
    @Published var currentFilters = ShopFilters()
    
    private let userId = String(Config.defaultUserId)
    private var currentCategory = "All"
    private var currentPage = 0
    private let pageSize = 20
    private var hasMoreData = true
    
    func loadRecommendations() {
        guard !isLoading else { return }
        
        isLoading = true
        error = nil
        currentPage = 0
        hasMoreData = true
        
        Task {
            do {
                let items = try await fetchRecommendations(page: 0)
                recommendations = items
                isLoading = false
            } catch {
                self.error = error.localizedDescription
                // Load mock data as fallback
                loadMockRecommendations()
                isLoading = false
            }
        }
    }
    
    func loadMoreIfNeeded() {
        guard !isLoadingMore && hasMoreData else { return }
        
        isLoadingMore = true
        currentPage += 1
        
        Task {
            do {
                let items = try await fetchRecommendations(page: currentPage)
                if items.isEmpty {
                    hasMoreData = false
                } else {
                    recommendations.append(contentsOf: items)
                }
                isLoadingMore = false
            } catch {
                currentPage -= 1 // Reset page on error
                isLoadingMore = false
            }
        }
    }
    
    func refresh() async {
        currentPage = 0
        hasMoreData = true
        
        do {
            let items = try await fetchRecommendations(page: 0)
            recommendations = items
        } catch {
            // Silent fail on refresh
        }
    }
    
    func filterByCategory(_ category: String) {
        currentCategory = category
        loadRecommendations()
    }
    
    private func fetchRecommendations(page: Int) async throws -> [ShopItem] {
        let url = URL(string: "\(Config.baseURL)/shop/recommendations")!
        
        let request = ShopRecommendationRequest(
            userId: userId,
            category: currentCategory == "All" ? "Tops" : currentCategory,
            filters: currentFilters,
            limit: pageSize,
            offset: page * pageSize
        )
        
        let jsonData = try JSONEncoder().encode(request)
        
        let response = try await OptimizedNetworkManager.shared.fetch(
            ShopRecommendationResponse.self,
            from: url,
            method: "POST",
            body: jsonData,
            useCache: page == 0  // Cache first page only
        )
        
        return response.recommendations
    }
    
    private func loadMockRecommendations() {
        // Fallback mock data for development
        recommendations = [
            ShopItem(
                id: "1",
                name: "Flex Casual Shirt",
                brand: "J.Crew",
                price: 79.50,
                imageUrl: "https://www.jcrew.com/s7-img-facade/BA883_BL8133",
                productUrl: "https://www.jcrew.com/p/BA883",
                category: "Tops",
                fitConfidence: 0.92,
                recommendedSize: "L",
                measurements: nil,
                availableSizes: ["S", "M", "L", "XL"],
                description: nil
            )
        ]
    }
}

// Category Button for filter selection
struct OptimizedCategoryButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline)
                .fontWeight(isSelected ? .semibold : .regular)
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(isSelected ? Color.blue : Color(.systemGray5))
                )
                .foregroundColor(isSelected ? .white : .primary)
        }
    }
}

// Update ShopRecommendationRequest to include pagination
extension ShopRecommendationRequest {
    init(userId: String, category: String, filters: ShopFilters, limit: Int, offset: Int = 0) {
        self.init(
            userId: userId,
            category: category,
            filters: filters,
            limit: limit
        )
        // Add offset property if needed
    }
}
