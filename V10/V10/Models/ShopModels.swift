import Foundation

struct ShopItem: Identifiable, Codable {
    let id: String
    let name: String
    let brand: String
    let price: Double
    let imageUrl: String
    let productUrl: String
    let category: String
    let fitConfidence: Double
    let recommendedSize: String?
    let measurements: [String: String]?
    let availableSizes: [String]?
    let description: String?
    
    enum CodingKeys: String, CodingKey {
        case id, name, brand, price, category, description
        case imageUrl = "image_url"
        case productUrl = "product_url"
        case fitConfidence = "fit_confidence"
        case recommendedSize = "recommended_size"
        case measurements, availableSizes = "available_sizes"
    }
}

struct ShopFilters: Codable {
    var category: String?
    var priceRange: ClosedRange<Double>?
    var brands: [String]?
    var fitTypes: [String]?
    var sortBy: SortOption?
    
    enum SortOption: String, CaseIterable {
        case relevance = "relevance"
        case priceLowToHigh = "price_low_to_high"
        case priceHighToLow = "price_high_to_low"
        case fitConfidence = "fit_confidence"
        case newest = "newest"
    }
}

struct ShopRecommendationRequest: Codable {
    let userId: String
    let category: String?
    let filters: ShopFilters?
    let limit: Int?
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case category, filters, limit
    }
}

struct ShopRecommendationResponse: Codable {
    let recommendations: [ShopItem]
    let totalCount: Int
    let hasMore: Bool
    
    enum CodingKeys: String, CodingKey {
        case recommendations
        case totalCount = "total_count"
        case hasMore = "has_more"
    }
} 