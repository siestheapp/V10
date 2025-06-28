import Foundation
import SwiftUI

@MainActor
class ShopViewModel: ObservableObject {
    @Published var recommendations: [ShopItem] = []
    @Published var isLoading = false
    @Published var error: String?
    @Published var currentFilters = ShopFilters()
    
    private let userId = Config.defaultUserId
    private var currentCategory = "Tops"
    
    func loadRecommendations() {
        isLoading = true
        error = nil
        
        let request = ShopRecommendationRequest(
            userId: userId,
            category: currentCategory,
            filters: currentFilters,
            limit: 20
        )
        
        Task {
            do {
                let url = URL(string: "\(Config.baseURL)/shop/recommendations")!
                var urlRequest = URLRequest(url: url)
                urlRequest.httpMethod = "POST"
                urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
                
                let jsonData = try JSONEncoder().encode(request)
                urlRequest.httpBody = jsonData
                
                let (data, response) = try await URLSession.shared.data(for: urlRequest)
                
                if let httpResponse = response as? HTTPURLResponse {
                    if httpResponse.statusCode == 200 {
                        let shopResponse = try JSONDecoder().decode(ShopRecommendationResponse.self, from: data)
                        recommendations = shopResponse.recommendations
                    } else {
                        error = "Server error: \(httpResponse.statusCode)"
                    }
                }
            } catch {
                self.error = error.localizedDescription
                // For development, load mock data if API fails
                loadMockRecommendations()
            }
            
            isLoading = false
        }
    }
    
    func filterByCategory(_ category: String) {
        currentCategory = category
        currentFilters.category = category == "All" ? nil : category
        loadRecommendations()
    }
    
    func applyFilters(_ filters: ShopFilters) {
        currentFilters = filters
        loadRecommendations()
    }
    
    func loadMoreRecommendations() {
        // Implement pagination
        guard !isLoading else { return }
        
        let request = ShopRecommendationRequest(
            userId: userId,
            category: currentCategory,
            filters: currentFilters,
            limit: 10
        )
        
        Task {
            do {
                let url = URL(string: "\(Config.baseURL)/shop/recommendations")!
                var urlRequest = URLRequest(url: url)
                urlRequest.httpMethod = "POST"
                urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
                
                let jsonData = try JSONEncoder().encode(request)
                urlRequest.httpBody = jsonData
                
                let (data, response) = try await URLSession.shared.data(for: urlRequest)
                
                if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                    let shopResponse = try JSONDecoder().decode(ShopRecommendationResponse.self, from: data)
                    recommendations.append(contentsOf: shopResponse.recommendations)
                }
            } catch {
                print("Error loading more recommendations: \(error)")
            }
        }
    }
    
    // Mock data for development
    private func loadMockRecommendations() {
        recommendations = [
            ShopItem(
                id: "1",
                name: "Brenan Polo Shirt",
                brand: "Theory",
                price: 89.0,
                imageUrl: "https://via.placeholder.com/300x400/4A90E2/FFFFFF?text=Theory+Polo",
                productUrl: "https://www.theory.com/us/en/mens/polo-shirts/brenan-polo-shirt/",
                category: "Tops",
                fitConfidence: 0.95,
                recommendedSize: "M",
                measurements: [
                    "chest": "40-42\"",
                    "sleeve": "24-25\"",
                    "length": "28-29\""
                ],
                availableSizes: ["XS", "S", "M", "L", "XL"],
                description: "A refined polo shirt in soft cotton piqué with a modern fit."
            ),
            ShopItem(
                id: "2",
                name: "Classic Fit Oxford Shirt",
                brand: "J.Crew",
                price: 69.50,
                imageUrl: "https://via.placeholder.com/300x400/50C878/FFFFFF?text=J.Crew+Oxford",
                productUrl: "https://www.jcrew.com/p/mens_category/shirts/oxford/classic-fit-oxford-shirt/",
                category: "Tops",
                fitConfidence: 0.88,
                recommendedSize: "L",
                measurements: [
                    "chest": "42-44\"",
                    "sleeve": "25-26\"",
                    "length": "29-30\""
                ],
                availableSizes: ["XS", "S", "M", "L", "XL", "XXL"],
                description: "Our most popular oxford shirt in a classic fit."
            ),
            ShopItem(
                id: "3",
                name: "Merino Wool Sweater",
                brand: "Banana Republic",
                price: 79.99,
                imageUrl: "https://via.placeholder.com/300x400/FF6B35/FFFFFF?text=BR+Wool+Sweater",
                productUrl: "https://bananarepublic.gap.com/browse/product.do?pid=123456",
                category: "Tops",
                fitConfidence: 0.92,
                recommendedSize: "M",
                measurements: [
                    "chest": "40-42\"",
                    "sleeve": "24-25\"",
                    "length": "27-28\""
                ],
                availableSizes: ["S", "M", "L", "XL"],
                description: "Soft merino wool sweater with a relaxed fit."
            ),
            ShopItem(
                id: "4",
                name: "Performance Tech Tee",
                brand: "Lululemon",
                price: 58.0,
                imageUrl: "https://via.placeholder.com/300x400/000000/FFFFFF?text=Lulu+Tech+Tee",
                productUrl: "https://shop.lululemon.com/p/mens-tops/performance-tech-tee-2/",
                category: "Tops",
                fitConfidence: 0.85,
                recommendedSize: "S",
                measurements: [
                    "chest": "38-40\"",
                    "sleeve": "23-24\"",
                    "length": "26-27\""
                ],
                availableSizes: ["XS", "S", "M", "L", "XL", "XXL"],
                description: "Lightweight performance fabric with moisture-wicking technology."
            ),
            ShopItem(
                id: "5",
                name: "Down Sweater Jacket",
                brand: "Patagonia",
                price: 199.0,
                imageUrl: "https://via.placeholder.com/300x400/1E3A8A/FFFFFF?text=Patagonia+Down",
                productUrl: "https://www.patagonia.com/product/mens-down-sweater-jacket/84240.html",
                category: "Outerwear",
                fitConfidence: 0.90,
                recommendedSize: "M",
                measurements: [
                    "chest": "40-42\"",
                    "sleeve": "24-25\"",
                    "length": "28-29\""
                ],
                availableSizes: ["XS", "S", "M", "L", "XL", "XXL"],
                description: "Lightweight, windproof shell with 800-fill-power goose down insulation."
            )
        ]
    }
} 